"""检查 Jamendo API 是否返回受欢迎度相关字段

用途：测试 API 返回的所有字段，查找播放量、下载量、受欢迎度等信息
"""
import os
import sys
import json
from pathlib import Path

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


def test_api_fields():
    """测试 API 返回的所有字段"""
    print("=" * 80)
    print("测试 Jamendo API 返回的字段")
    print("=" * 80)
    
    # 测试不同的参数组合
    test_cases = [
        {
            "name": "基础搜索（包含 musicinfo）",
            "params": {
                "client_id": CLIENT_ID,
                "format": "json",
                "limit": 5,
                "search": "lofi",
                "include": "musicinfo"
            }
        },
        {
            "name": "尝试 popularity 排序",
            "params": {
                "client_id": CLIENT_ID,
                "format": "json",
                "limit": 5,
                "search": "lofi",
                "include": "musicinfo",
                "order": "popularity_total_desc"
            }
        },
        {
            "name": "尝试 listens 排序",
            "params": {
                "client_id": CLIENT_ID,
                "format": "json",
                "limit": 5,
                "search": "lofi",
                "include": "musicinfo",
                "order": "listens_desc"
            }
            },
        {
            "name": "尝试 downloads 排序",
            "params": {
                "client_id": CLIENT_ID,
                "format": "json",
                "limit": 5,
                "search": "lofi",
                "include": "musicinfo",
                "order": "downloads_desc"
            }
        },
        {
            "name": "尝试 rating 排序",
            "params": {
                "client_id": CLIENT_ID,
                "format": "json",
                "limit": 5,
                "search": "lofi",
                "include": "musicinfo",
                "order": "rating_desc"
            }
        }
    ]
    
    all_fields = set()
    sample_track = None
    
    for test_case in test_cases:
        print(f"\n[测试] {test_case['name']}")
        print("-" * 80)
        
        try:
            url = f"{BASE_URL}/tracks/"
            response = requests.get(url, params=test_case['params'], timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results") and len(data["results"]) > 0:
                track = data["results"][0]
                if not sample_track:
                    sample_track = track
                
                # 收集所有字段
                def collect_fields(obj, prefix=""):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            full_key = f"{prefix}.{key}" if prefix else key
                            all_fields.add(full_key)
                            if isinstance(value, (dict, list)):
                                collect_fields(value, full_key)
                    elif isinstance(obj, list) and len(obj) > 0:
                        collect_fields(obj[0], prefix)
                
                collect_fields(track)
                
                print(f"✅ 成功获取 {len(data['results'])} 首音乐")
                print(f"   第一个结果包含 {len(track)} 个顶级字段")
            else:
                print("⚠️  未返回结果")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"   错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"   响应内容: {e.response.text[:200]}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    # 显示所有收集到的字段
    print("\n" + "=" * 80)
    print("所有发现的字段:")
    print("=" * 80)
    
    # 按类别分组
    popularity_fields = []
    basic_fields = []
    musicinfo_fields = []
    other_fields = []
    
    for field in sorted(all_fields):
        field_lower = field.lower()
        if any(keyword in field_lower for keyword in ['popular', 'listen', 'download', 'rating', 'score', 'view', 'play', 'like', 'favorite', 'trend']):
            popularity_fields.append(field)
        elif 'musicinfo' in field_lower:
            musicinfo_fields.append(field)
        elif field in ['id', 'name', 'artist_name', 'duration', 'audio', 'image', 'releasedate', 'position', 'license']:
            basic_fields.append(field)
        else:
            other_fields.append(field)
    
    if popularity_fields:
        print("\n🎯 受欢迎度相关字段:")
        for field in popularity_fields:
            print(f"  - {field}")
    
    print("\n📋 基础字段:")
    for field in basic_fields:
        print(f"  - {field}")
    
    if musicinfo_fields:
        print("\n🎵 音乐信息字段:")
        for field in musicinfo_fields[:20]:  # 只显示前20个
            print(f"  - {field}")
        if len(musicinfo_fields) > 20:
            print(f"  ... 还有 {len(musicinfo_fields) - 20} 个字段")
    
    if other_fields:
        print("\n📦 其他字段:")
        for field in other_fields[:30]:  # 只显示前30个
            print(f"  - {field}")
        if len(other_fields) > 30:
            print(f"  ... 还有 {len(other_fields) - 30} 个字段")
    
    # 显示示例 track 的完整结构
    if sample_track:
        print("\n" + "=" * 80)
        print("示例 Track 完整结构:")
        print("=" * 80)
        print(json.dumps(sample_track, indent=2, ensure_ascii=False)[:2000])
        if len(json.dumps(sample_track, indent=2, ensure_ascii=False)) > 2000:
            print("\n... (已截断)")
    
    # 检查 orderby 参数支持的值
    print("\n" + "=" * 80)
    print("测试 orderby 参数支持的值:")
    print("=" * 80)
    
    orderby_options = [
        "popularity_total_desc", "popularity_total_asc",
        "listens_desc", "listens_asc",
        "downloads_desc", "downloads_asc",
        "rating_desc", "rating_asc",
        "releasedate_desc", "releasedate_asc",
        "position_asc", "position_desc"
    ]
    
    for orderby in orderby_options:
        try:
            url = f"{BASE_URL}/tracks/"
            params = {
                "client_id": CLIENT_ID,
                "format": "json",
                "limit": 1,
                "search": "lofi",
                "orderby": orderby
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                print(f"✅ {orderby}")
            else:
                print(f"❌ {orderby} (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ {orderby} (错误: {str(e)[:50]})")


if __name__ == "__main__":
    test_api_fields()

