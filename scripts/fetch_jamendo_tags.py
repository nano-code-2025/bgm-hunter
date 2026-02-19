"""获取 Jamendo API 实际标签数据

用途：从 Jamendo API 收集所有 genres, instruments, vartags
输出：data/jamendo_tags.json
"""
import os
import sys
import json
from pathlib import Path
from collections import Counter
from typing import Dict, List, Set

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get("JAMENDO_CLIENT_ID", "f2567443")
BASE_URL = "https://api.jamendo.com/v3.0"

# 搜索关键词列表，覆盖各种音乐类型
SEARCH_KEYWORDS = [
    "rock", "pop", "jazz", "classical", "electronic", "hip hop", "country",
    "folk", "blues", "reggae", "metal", "latin", "r&b", "soul", "indie",
    "alternative", "lofi", "chill", "ambient", "piano", "guitar", "violin",
    "happy", "sad", "energetic", "calm", "romantic", "peaceful", "uplifting",
    "vlog", "travel", "food", "sport", "game", "cinematic", "epic"
]


def search_jamendo(keyword: str, limit: int = 50) -> Dict:
    """调用 Jamendo API 搜索音乐"""
    url = f"{BASE_URL}/tracks/"
    params = {
        "client_id": CLIENT_ID,
        "format": "json",
        "limit": limit,
        "search": keyword,
        "include": "musicinfo"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[警告] 搜索 '{keyword}' 失败: {e}")
        return {"results": []}


def collect_tags() -> Dict[str, Dict]:
    """收集所有标签并统计频率"""
    all_genres: Counter = Counter()
    all_instruments: Counter = Counter()
    all_vartags: Counter = Counter()
    
    total_tracks = 0
    
    print("开始收集 Jamendo API 标签数据...")
    print(f"搜索关键词数量: {len(SEARCH_KEYWORDS)}")
    print("-" * 80)
    
    for i, keyword in enumerate(SEARCH_KEYWORDS, 1):
        print(f"[{i}/{len(SEARCH_KEYWORDS)}] 搜索: {keyword}")
        data = search_jamendo(keyword)
        
        if not data.get("results"):
            print(f"  未找到结果")
            continue
        
        results = data["results"]
        total_tracks += len(results)
        print(f"  找到 {len(results)} 首音乐")
        
        for track in results:
            musicinfo = track.get("musicinfo", {})
            tags = musicinfo.get("tags", {})
            
            # 收集 genres
            for genre in tags.get("genres", []):
                all_genres[genre.lower()] += 1
            
            # 收集 instruments
            for instrument in tags.get("instruments", []):
                all_instruments[instrument.lower()] += 1
            
            # 收集 vartags
            for vartag in tags.get("vartags", []):
                all_vartags[vartag.lower()] += 1
    
    print("-" * 80)
    print(f"总计处理 {total_tracks} 首音乐")
    print(f"收集到 {len(all_genres)} 个 genres")
    print(f"收集到 {len(all_instruments)} 个 instruments")
    print(f"收集到 {len(all_vartags)} 个 vartags")
    
    return {
        "genres": dict(all_genres.most_common()),
        "instruments": dict(all_instruments.most_common()),
        "vartags": dict(all_vartags.most_common()),
        "statistics": {
            "total_tracks": total_tracks,
            "total_genres": len(all_genres),
            "total_instruments": len(all_instruments),
            "total_vartags": len(all_vartags)
        }
    }


def main():
    """主函数"""
    # 创建 data 目录
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # 收集标签
    tags_data = collect_tags()
    
    # 保存到 JSON 文件
    output_file = data_dir / "jamendo_tags.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(tags_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n标签数据已保存到: {output_file}")
    
    # 打印 Top 20
    print("\n=== Top 20 Genres ===")
    for genre, count in list(tags_data["genres"].items())[:20]:
        print(f"  {genre}: {count}")
    
    print("\n=== Top 20 Instruments ===")
    for instrument, count in list(tags_data["instruments"].items())[:20]:
        print(f"  {instrument}: {count}")
    
    print("\n=== Top 20 Vartags ===")
    for vartag, count in list(tags_data["vartags"].items())[:20]:
        print(f"  {vartag}: {count}")


if __name__ == "__main__":
    main()

