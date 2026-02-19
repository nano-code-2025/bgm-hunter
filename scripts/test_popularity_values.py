"""测试是否能获取受欢迎度的具体数值

检查不同的 API 端点和参数组合
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()

CLIENT_ID = os.environ.get("JAMENDO_CLIENT_ID", "f2567443")
BASE_URL = "https://api.jamendo.com/v3.0"


def test_track_details():
    """测试获取单首音乐的详细信息"""
    print("=" * 80)
    print("测试获取单首音乐的详细信息")
    print("=" * 80)
    
    # 先搜索一首音乐获取 ID
    url = f"{BASE_URL}/tracks/"
    params = {
        "client_id": CLIENT_ID,
        "format": "json",
        "limit": 1,
        "search": "lofi",
        "include": "musicinfo"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results"):
            print("❌ 未找到音乐")
            return
        
        track_id = data["results"][0]["id"]
        print(f"✅ 找到音乐 ID: {track_id}")
        
        # 尝试不同的方式获取详细信息
        test_cases = [
            {
                "name": "使用 tracks/ 端点，指定 ID",
                "url": f"{BASE_URL}/tracks/",
                "params": {
                    "client_id": CLIENT_ID,
                    "format": "json",
                    "id": track_id,
                    "include": "musicinfo"
                }
            },
            {
                "name": "尝试添加 stats 参数",
                "url": f"{BASE_URL}/tracks/",
                "params": {
                    "client_id": CLIENT_ID,
                    "format": "json",
                    "id": track_id,
                    "include": "musicinfo,stats"
                }
            },
            {
                "name": "尝试添加 popularity 参数",
                "url": f"{BASE_URL}/tracks/",
                "params": {
                    "client_id": CLIENT_ID,
                    "format": "json",
                    "id": track_id,
                    "include": "musicinfo,popularity"
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n[测试] {test_case['name']}")
            print("-" * 80)
            try:
                response = requests.get(test_case['url'], params=test_case['params'], timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if data.get("results") and len(data["results"]) > 0:
                    track = data["results"][0]
                    print(f"✅ 成功获取数据")
                    print(f"   字段数量: {len(track)}")
                    
                    # 查找受欢迎度相关字段
                    popularity_keys = [k for k in track.keys() if any(
                        keyword in k.lower() for keyword in 
                        ['popular', 'listen', 'download', 'rating', 'score', 'view', 'play', 'like']
                    )]
                    
                    if popularity_keys:
                        print(f"   🎯 发现受欢迎度字段:")
                        for key in popularity_keys:
                            print(f"      - {key}: {track[key]}")
                    else:
                        print(f"   ⚠️  未发现受欢迎度字段")
                        print(f"   所有字段: {', '.join(track.keys())}")
                else:
                    print("❌ 未返回结果")
            except Exception as e:
                print(f"❌ 错误: {e}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


def test_orderby_effectiveness():
    """测试不同排序方式的效果"""
    print("\n" + "=" * 80)
    print("测试不同排序方式的效果")
    print("=" * 80)
    
    orderby_options = [
        "popularity_total_desc",
        "listens_desc", 
        "downloads_desc",
        "rating_desc",
        "releasedate_desc"
    ]
    
    for orderby in orderby_options:
        print(f"\n[测试] 排序方式: {orderby}")
        print("-" * 80)
        try:
            url = f"{BASE_URL}/tracks/"
            params = {
                "client_id": CLIENT_ID,
                "format": "json",
                "limit": 3,
                "search": "lofi",
                "include": "musicinfo",
                "orderby": orderby
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results"):
                print(f"✅ 成功获取 {len(data['results'])} 首音乐")
                for i, track in enumerate(data['results'], 1):
                    print(f"   {i}. {track['name']} - {track['artist_name']} (ID: {track['id']}, Position: {track.get('position', 'N/A')})")
            else:
                print("❌ 未返回结果")
        except Exception as e:
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    test_track_details()
    test_orderby_effectiveness()

