"""Jamendo API 测试脚本：关键词搜索 → 推荐度排序 → Top 5

用途：验证 Jamendo API 搜索功能，按推荐度输出前5首音乐
"""
import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
from dotenv import load_dotenv

# 加载环境变量（如果存在 .env 文件）
load_dotenv()


def pick_score(track: Dict) -> Tuple[int, str]:
    """从 track 中提取推荐度分数，按优先级降级策略"""
    # 优先级1: popularity 相关字段
    for key in ("popularity_total", "popularity_month", "likes", "listens"):
        value = track.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return int(value), key
    
    # 优先级2: position 字段（越小越靠前，转换为分数：1000 - position）
    position = track.get("position")
    if isinstance(position, int) and position > 0:
        # position 越小越好，所以用 1000 - position 作为分数
        return 1000 - position, "position_inverted"
    
    # 优先级3: 使用 releasedate 的年份（较新的可能更受欢迎）
    releasedate = track.get("releasedate", "")
    if releasedate:
        try:
            year = int(releasedate.split("-")[0])
            # 2020年后的音乐给更高分数
            if year >= 2020:
                return year, "release_year"
        except (ValueError, IndexError):
            pass
    
    return 0, "fallback_rank"


def search_jamendo(keyword: str, client_id: str, limit: int = 50, include_musicinfo: bool = True) -> Dict:
    """调用 Jamendo API 搜索音乐"""
    url = "https://api.jamendo.com/v3.0/tracks/"
    params = {
        "client_id": client_id,
        "format": "json",
        "limit": limit,
        "search": keyword,
        # 注意：Jamendo API 的 order 参数可能不支持 popularity_total_desc
        # 如果 API 支持，可以尝试: "order": "popularity_total_desc"
    }
    
    # 添加 musicinfo 参数以获取标签信息（genres, instruments, vartags 等）
    if include_musicinfo:
        params["include"] = "musicinfo"
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[错误] API 请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应内容: {e.response.text}")
        sys.exit(1)


def format_duration(seconds: Optional[int]) -> str:
    """格式化时长（秒 → MM:SS）"""
    if not seconds:
        return "N/A"
    mins, secs = divmod(seconds, 60)
    return f"{mins}:{secs:02d}"


def search_top5(keyword: str, client_id: Optional[str] = None) -> None:
    """搜索并输出 Top 5 推荐音乐"""
    # 获取 Client ID
    if not client_id:
        client_id = os.environ.get("JAMENDO_CLIENT_ID")
    
    if not client_id:
        print("[错误] 未找到 JAMENDO_CLIENT_ID")
        print("请设置环境变量: $env:JAMENDO_CLIENT_ID='your_client_id'")
        print("或在代码中直接传入 client_id 参数")
        sys.exit(1)
    
    print(f"\n[搜索] 关键词: '{keyword}'")
    print(f"[配置] Client ID: {client_id[:8]}...")
    print("-" * 80)
    
    # 调用 API
    data = search_jamendo(keyword, client_id)
    
    # 检查返回结构
    if "results" not in data:
        print(f"[错误] API 返回格式异常: {json.dumps(data, indent=2, ensure_ascii=False)}")
        sys.exit(1)
    
    results = data.get("results", [])
    
    if not results:
        print(f"[警告] 未找到匹配 '{keyword}' 的音乐")
        print(f"API 响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return
    
    print(f"[成功] 找到 {len(results)} 首音乐，按推荐度排序后取 Top 5:\n")
    
    # 计算推荐度并排序
    scored = []
    for i, track in enumerate(results):
        score, score_source = pick_score(track)
        scored.append((score, score_source, i, track))
    
    # 按分数降序排序（分数相同则按原始顺序）
    scored.sort(key=lambda x: (x[0], -x[2]), reverse=True)
    
    # 输出 Top 5
    top5 = scored[:5]
    for rank, (score, score_source, _, track) in enumerate(top5, 1):
        name = track.get("name", "Unknown")
        artist = track.get("artist_name", "Unknown")
        duration = format_duration(track.get("duration"))
        audio_url = track.get("audio", "N/A")
        track_id = track.get("id", "N/A")
        
        print(f"[{rank}] {name}")
        print(f"     艺术家: {artist}")
        print(f"     时长: {duration} | ID: {track_id}")
        print(f"     推荐度: {score} (来源: {score_source})")
        print(f"     音频: {audio_url}")
        
        # 显示封面图片
        cover_url = track.get('image') or track.get('album_image')
        if cover_url:
            print(f"     封面: {cover_url}")
            # 可以修改 URL 中的 width 参数获取不同尺寸
            # 默认是 300，可以改为 200, 400, 500 等
        else:
            print(f"     封面: 未找到")
        
        # 显示下载链接
        download_url = track.get('audiodownload')
        download_allowed = track.get('audiodownload_allowed', False)
        if download_url and download_allowed:
            print(f"     下载: {download_url}")
            print(f"     [提示] 可直接下载 MP3 文件")
        elif download_url:
            print(f"     下载: {download_url} (需要授权)")
        else:
            print(f"     下载: 不可用")
        
        # 显示标签信息（如果存在）
        musicinfo = track.get('musicinfo', {})
        if musicinfo:
            tags = musicinfo.get('tags', {})
            if tags:
                genres = tags.get('genres', [])
                instruments = tags.get('instruments', [])
                vartags = tags.get('vartags', [])
                
                if genres:
                    print(f"     类型: {', '.join(genres)}")
                if instruments:
                    print(f"     乐器: {', '.join(instruments)}")
                if vartags:
                    print(f"     标签: {', '.join(vartags)}")
                
                # 显示其他音乐信息
                vocal_instrumental = musicinfo.get('vocalinstrumental', '')
                acoustic_electric = musicinfo.get('acousticelectric', '')
                speed = musicinfo.get('speed', '')
                
                if vocal_instrumental:
                    print(f"     人声/器乐: {vocal_instrumental}")
                if acoustic_electric:
                    print(f"     原声/电声: {acoustic_electric}")
                if speed:
                    print(f"     速度: {speed}")
        
        print()
    
    # 统计信息
    if len(results) > 5:
        print(f"[统计] 共 {len(results)} 首，已显示前 5 首")
    
    # 检查推荐度字段分布
    score_sources = {}
    for _, src, _, _ in scored:
        score_sources[src] = score_sources.get(src, 0) + 1
    print(f"[分析] 推荐度字段分布: {score_sources}")


def main():
    """主函数：支持命令行参数或交互式输入"""
    # 从环境变量或直接使用已知的 Client ID
    # 注意：根据 log.txt，Client ID 是 f2567443
    default_client_id = os.environ.get("JAMENDO_CLIENT_ID", "f2567443")
    
    if len(sys.argv) > 1:
        # 命令行模式：python test_jamendo_api.py lofi
        keyword = sys.argv[1]
        search_top5(keyword, default_client_id)
    else:
        # 交互模式：测试多个关键词
        test_keywords = ["lofi", "piano", "chill", "happy", "cinematic"]
        print("=" * 80)
        print("Jamendo API 测试 - 关键词搜索 Top 5")
        print("=" * 80)
        print(f"\n[测试] 将测试以下关键词: {', '.join(test_keywords)}\n")
        
        for keyword in test_keywords:
            search_top5(keyword, default_client_id)
            print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()

