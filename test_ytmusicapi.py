"""YouTube Music API (ytmusicapi) 测试脚本：关键词搜索 → 推荐排序 → Top 5 → 试听

用途：验证 ytmusicapi 搜索功能，按相关度输出前5首音乐，并提供试听链接
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

try:
    from ytmusicapi import YTMusic
except ImportError:
    print("[错误] 未安装 ytmusicapi")
    print("请运行: pip install ytmusicapi")
    sys.exit(1)


def format_duration(seconds: Optional[int]) -> str:
    """格式化时长（秒 → MM:SS）"""
    if not seconds:
        return "N/A"
    mins, secs = divmod(seconds, 60)
    return f"{mins}:{secs:02d}"


def find_cookie_file() -> Optional[Path]:
    """查找 cookie 文件"""
    possible_paths = [
        Path(__file__).parent.parent / 'data' / 'youtube_cookies.txt',
        Path(__file__).parent.parent / 'data' / 'youtube_cookies.json',
        Path(__file__).parent.parent / 'youtube_cookies.txt',
        Path(__file__).parent.parent / 'youtube_cookies.json',
        Path.home() / '.ytmusic_cookies.txt',
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def initialize_ytmusic(cookie_path: Optional[Path] = None) -> YTMusic:
    """初始化 YTMusic 客户端"""
    if cookie_path:
        cookie_str = str(cookie_path)  # 转换为字符串
        print(f"[配置] 使用 Cookie 文件: {cookie_str}")
        try:
            # 尝试使用 cookie 文件初始化
            if cookie_path.suffix == '.json':
                return YTMusic(auth=cookie_str)
            else:
                # Netscape 格式（cookies.txt）
                return YTMusic(cookie_str)
        except Exception as e:
            print(f"[警告] Cookie 文件初始化失败: {e}")
            print("[提示] 将尝试无 Cookie 模式（功能受限）")
    
    # 无 Cookie 模式（功能受限，但可以测试基本搜索）
    print("[配置] 使用无 Cookie 模式（功能受限）")
    print("[提示] 如需完整功能，请提供 Cookie 文件")
    return YTMusic()


def search_top5(keyword: str, ytmusic: Optional[YTMusic] = None) -> None:
    """搜索并输出 Top 5 推荐音乐"""
    if ytmusic is None:
        cookie_path = find_cookie_file()
        ytmusic = initialize_ytmusic(cookie_path)
    
    print(f"\n[搜索] 关键词: '{keyword}'")
    print("-" * 80)
    
    try:
        # 搜索歌曲
        results = ytmusic.search(keyword, filter="songs", limit=20)
        
        if not results:
            print(f"[警告] 未找到匹配 '{keyword}' 的音乐")
            return
        
        print(f"[成功] 找到 {len(results)} 首音乐，显示 Top 5:\n")
        
        # 输出 Top 5
        top5 = results[:5]
        for rank, track in enumerate(top5, 1):
            title = track.get('title', 'Unknown')
            artist = track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown'
            duration = track.get('duration', 'N/A')
            video_id = track.get('videoId', 'N/A')
            
            # 尝试获取流媒体 URL（需要 Cookie）
            streaming_url = None
            try:
                if video_id and video_id != 'N/A':
                    # 获取播放列表信息（包含流媒体 URL）
                    watch_playlist = ytmusic.get_watch_playlist(video_id)
                    if watch_playlist and 'tracks' in watch_playlist:
                        first_track = watch_playlist['tracks'][0]
                        if 'videoId' in first_track:
                            # 获取流媒体数据
                            streaming_data = ytmusic.get_streaming_data(video_id)
                            if streaming_data and 'adaptiveFormats' in streaming_data:
                                # 查找音频格式
                                for fmt in streaming_data['adaptiveFormats']:
                                    if 'audio' in fmt.get('mimeType', '').lower():
                                        streaming_url = fmt.get('url')
                                        break
            except Exception as e:
                # 获取流媒体 URL 失败（可能是无 Cookie 或权限问题）
                pass
            
            print(f"[{rank}] {title}")
            print(f"     艺术家: {artist}")
            print(f"     时长: {duration} | 视频ID: {video_id}")
            
            if streaming_url:
                print(f"     试听链接: {streaming_url[:80]}...")
            else:
                # 无 Cookie 模式下，手动构建播放链接
                if video_id and video_id != 'N/A':
                    play_url = f"https://music.youtube.com/watch?v={video_id}"
                    print(f"     试听链接: {play_url}")
                    print(f"     [提示] 这是播放页面链接，可在浏览器中打开试听")
                else:
                    print(f"     试听链接: 需要 Cookie 才能获取（或使用视频ID: {video_id}）")
            
            # 显示其他元数据
            album = track.get('album', {})
            if album and isinstance(album, dict):
                album_name = album.get('name', '')
                if album_name:
                    print(f"     专辑: {album_name}")
            
            # 显示封面图片
            thumbnails = track.get('thumbnails', [])
            if thumbnails:
                # 选择最大尺寸的缩略图
                largest_thumb = max(thumbnails, key=lambda x: x.get('width', 0) * x.get('height', 0))
                cover_url = largest_thumb.get('url', '')
                if cover_url:
                    print(f"     封面: {cover_url}")
                    print(f"     封面尺寸: {largest_thumb.get('width')}x{largest_thumb.get('height')}")
            
            print()
        
        # 统计信息
        if len(results) > 5:
            print(f"[统计] 共 {len(results)} 首，已显示前 5 首")
        
    except Exception as e:
        print(f"[错误] 搜索失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n[提示] 可能的原因:")
        print("  1. 未提供有效的 Cookie 文件")
        print("  2. Cookie 已过期，需要重新获取")
        print("  3. 网络连接问题")
        print("  4. YouTube Music API 限制")


def main():
    """主函数：支持命令行参数或交互式输入"""
    print("=" * 80)
    print("YouTube Music API (ytmusicapi) 测试 - 关键词搜索 Top 5")
    print("=" * 80)
    
    # 检查 Cookie 文件
    cookie_path = find_cookie_file()
    if cookie_path:
        print(f"[发现] Cookie 文件: {cookie_path}")
    else:
        print("[提示] 未找到 Cookie 文件，将使用无 Cookie 模式")
        print("[提示] Cookie 文件应放在以下位置之一:")
        print("  - data/youtube_cookies.txt")
        print("  - data/youtube_cookies.json")
        print("  - 项目根目录/youtube_cookies.txt")
        print()
    
    # 初始化 YTMusic
    ytmusic = initialize_ytmusic(cookie_path)
    
    if len(sys.argv) > 1:
        # 命令行模式：python test_ytmusicapi.py lofi
        keyword = sys.argv[1]
        search_top5(keyword, ytmusic)
    else:
        # 交互模式：测试多个关键词
        test_keywords = ["lofi", "piano", "chill", "happy", "cinematic"]
        print(f"\n[测试] 将测试以下关键词: {', '.join(test_keywords)}\n")
        
        for keyword in test_keywords:
            search_top5(keyword, ytmusic)
            print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()

