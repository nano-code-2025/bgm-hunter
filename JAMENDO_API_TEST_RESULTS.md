# Jamendo API 测试结果总结

**测试日期**: 2026-02-15  
**Client ID**: f2567443  
**测试脚本**: `tests/test_jamendo_api.py`

---

## ✅ 测试通过

### 测试目标
- ✅ 输入关键词 → 调用 Jamendo API 搜索
- ✅ 按推荐度排序 → 输出 Top 5 音乐
- ✅ 显示关键元数据（标题、艺术家、时长、音频链接）

### 测试结果

#### 1. 关键词: `lofi`
- **找到**: 50 首音乐
- **Top 5 示例**:
  1. Lofi Chillout Hip Hop Beat - Joystock (2:29)
  2. Lofi - Alex_Valin (2:17)
  3. earlgrey - Lofi-fe (2:27)
  4. Calm Reflections (Lofi Chill Hop) - Janevo (2:02)
  5. Horizon | Non Copyright Lofi - Nightingale Lofi (2:56)

#### 2. 关键词: `piano`
- **找到**: 50 首音乐
- **Top 5 示例**:
  1. Trifle № 9 - Vladimir (0:56)
  2. Sonata for piano (four hands) - Alexander Morozov (22:17)
  3. Op. 14 - Vladimir (2:04)
  4. P. Tchaikovsky - Serenade for Strings... - Vladimir (25:24)
  5. Etude Op. 28 - Vladimir (1:52)

#### 3. 关键词: `happy`
- **找到**: 50 首音乐
- **Top 5 示例**:
  1. IN THE MORNING - hantell (3:21)
  2. Motizan - Aombra (2:05)
  3. Look at me - RBP_music (2:48)
  4. Odio la domenica-rmx - Orpheus (5:42)
  5. Good days are coming - FunkyJu (4:00)

---

## 📊 技术发现

### API 返回字段分析
- ✅ **可用字段**:
  - `id`, `name`, `artist_name`, `duration`
  - `audio` (试听链接)
  - `audiodownload` (下载链接，需要授权)
  - `position` (搜索结果位置，可作为推荐度依据)
  - `releasedate` (发布日期)
  - `license_ccurl` (授权协议)
  - ✅ **`image` / `album_image`** (专辑封面图片 URL)
  - ✅ **`musicinfo`** (音乐标签信息) - **重要发现！** ⭐

- ❌ **未找到字段**:
  - `popularity_total`, `popularity_month`
  - `likes`, `listens`

### 推荐度排序策略
由于 API 未返回 popularity 相关字段，当前使用：
1. **主要依据**: `position` 字段（API 返回的搜索结果位置）
   - 位置越小（越靠前）→ 推荐度越高
   - 转换为分数: `1000 - position`

2. **备用策略**: `releasedate` 年份（较新的音乐可能更受欢迎）

3. **降级策略**: 使用原始返回顺序

---

## 🎯 使用方式

### 单关键词测试
```bash
.\venv\Scripts\python.exe tests\test_jamendo_api.py lofi
```

### 批量测试（交互模式）
```bash
.\venv\Scripts\python.exe tests\test_jamendo_api.py
```
将自动测试: `lofi`, `piano`, `chill`, `happy`, `cinematic`

---

## 📝 注意事项

1. **音频链接**: 
   - `audio` 字段提供试听链接（mp31 格式）
   - `audiodownload` 提供下载链接（需要检查授权）

2. **授权协议**: 
   - 每条音乐都有 `license_ccurl`，使用前需确认授权范围
   - 部分音乐可能仅限非商业使用

3. **API 限制**: 
   - 当前 Plan: Read & write (Review/Change)
   - 如需扩展限制，需联系 Jamendo

---

## 🏷️ 音乐标签（Tags）功能 - 推荐系统核心

### 标签信息获取

Jamendo API **完全支持获取丰富的音乐标签信息**，这对于构建推荐系统至关重要！

**使用方法**: 在 API 请求中添加 `include=musicinfo` 参数

```python
import requests

url = "https://api.jamendo.com/v3.0/tracks/"
params = {
    "client_id": client_id,
    "format": "json",
    "limit": 50,
    "search": keyword,
    "include": "musicinfo"  # ⭐ 关键参数
}

response = requests.get(url, params=params)
data = response.json()
```

### 标签数据结构

返回的 `musicinfo` 字段包含以下信息：

```python
{
    "musicinfo": {
        "vocalinstrumental": "instrumental",  # 人声/器乐
        "lang": "",                              # 语言
        "gender": "",                            # 性别
        "acousticelectric": "acoustic",          # 原声/电声
        "speed": "medium",                       # 速度: low/medium/high
        "tags": {
            "genres": ["chillhop", "hiphop", "lofi"],      # 音乐类型
            "instruments": ["sampler", "synthesizer"],      # 乐器
            "vartags": ["lounge", "peaceful", "urban"]     # 变体标签（情绪/场景）
        }
    }
}
```

### 标签字段说明

#### 1. **genres** (音乐类型)
- 描述：音乐的主要类型/风格
- 示例：`["chillhop", "hiphop", "lofi"]`, `["piano", "classical"]`
- 用途：按音乐风格分类和推荐

#### 2. **instruments** (乐器)
- 描述：音乐中使用的乐器
- 示例：`["sampler", "synthesizer"]`, `["piano", "strings"]`, `["bass"]`
- 用途：按乐器偏好推荐

#### 3. **vartags** (变体标签)
- 描述：情绪、场景、氛围等标签
- 示例：`["lounge", "peaceful", "urban"]`, `["happy"]`, `["sad"]`, `["neutral"]`
- 用途：按情绪/场景推荐（非常适合 BGM 推荐）

#### 4. **vocalinstrumental** (人声/器乐)
- 值：`"vocal"` 或 `"instrumental"`
- 用途：区分是否有人声

#### 5. **acousticelectric** (原声/电声)
- 值：`"acoustic"` 或 `"electric"`
- 用途：区分原声/电声风格

#### 6. **speed** (速度)
- 值：`"low"`, `"medium"`, `"high"`
- 用途：按节奏速度推荐

### 使用示例

```python
# 获取标签信息
track = results[0]
musicinfo = track.get('musicinfo', {})

if musicinfo:
    tags = musicinfo.get('tags', {})
    
    # 获取音乐类型
    genres = tags.get('genres', [])
    # 例如: ["chillhop", "hiphop", "lofi"]
    
    # 获取乐器
    instruments = tags.get('instruments', [])
    # 例如: ["sampler", "synthesizer"]
    
    # 获取情绪/场景标签
    vartags = tags.get('vartags', [])
    # 例如: ["lounge", "peaceful", "urban"]
    
    # 获取其他属性
    vocal_instrumental = musicinfo.get('vocalinstrumental')
    acoustic_electric = musicinfo.get('acousticelectric')
    speed = musicinfo.get('speed')
```

### 推荐系统应用

这些标签可以用于构建多维度推荐系统：

1. **按音乐类型推荐** (`genres`)
   - 用户喜欢 "lofi" → 推荐其他 "lofi" 音乐
   - 用户喜欢 "piano" → 推荐其他 "piano" 音乐

2. **按情绪/场景推荐** (`vartags`)
   - 用户需要 "peaceful" → 推荐 "peaceful", "calm", "relaxing" 标签的音乐
   - 用户需要 "happy" → 推荐 "happy", "energetic", "upbeat" 标签的音乐

3. **按乐器推荐** (`instruments`)
   - 用户喜欢 "piano" → 推荐包含 "piano" 的音乐

4. **组合推荐**
   - 用户需要：lofi + peaceful + instrumental + medium speed
   - 可以精确匹配所有条件

### 标签统计示例

```python
# 统计所有音乐的标签分布
all_genres = []
all_instruments = []
all_vartags = []

for track in results:
    musicinfo = track.get('musicinfo', {})
    tags = musicinfo.get('tags', {})
    
    all_genres.extend(tags.get('genres', []))
    all_instruments.extend(tags.get('instruments', []))
    all_vartags.extend(tags.get('vartags', []))

# 统计频率
from collections import Counter
genre_counts = Counter(all_genres)
instrument_counts = Counter(all_instruments)
vartag_counts = Counter(all_vartags)

print("热门音乐类型:", genre_counts.most_common(10))
print("热门乐器:", instrument_counts.most_common(10))
print("热门标签:", vartag_counts.most_common(10))
```

### 注意事项

1. **必须添加参数**: 默认情况下不返回 `musicinfo`，必须添加 `include=musicinfo` 参数
2. **标签可能为空**: 部分音乐可能没有完整的标签信息
3. **标签语言**: 标签通常是英文，需要时可以进行翻译

---

## 📥 音乐下载功能（MP3/MP4）

### 下载链接获取

Jamendo API **完全支持直接下载 MP3 文件**，无需额外授权（对于允许下载的音乐）：

- ✅ **`audiodownload`**: 高质量 MP3 下载链接（mp32 格式）
- ✅ **`audio`**: 试听/流媒体链接（mp31 格式，质量较低）
- ✅ **`audiodownload_allowed`**: 下载权限标志

### 下载链接格式

```python
# 从搜索结果获取下载链接
track = results[0]

# 高质量下载链接（推荐）
download_url = track.get('audiodownload')
# 格式: https://prod-1.storage.jamendo.com/download/track/{track_id}/mp32/

# 试听链接（也可下载，但质量较低）
audio_url = track.get('audio')
# 格式: https://prod-1.storage.jamendo.com/?trackid={track_id}&format=mp31&from=...

# 检查下载权限
download_allowed = track.get('audiodownload_allowed', False)
```

### 支持的格式

Jamendo API 支持多种音频格式下载：

1. **MP3 格式**:
   - `mp32/`: 高质量 MP3（推荐用于下载）
   - `mp31/`: 低质量 MP3（用于试听）

2. **其他格式**（如果可用）:
   - `flac/`: 无损格式
   - `ogg/`: OGG 格式

### 下载实现示例

```python
import requests
from pathlib import Path

def download_track(track, output_dir: Path):
    """下载音乐文件"""
    download_url = track.get('audiodownload')
    download_allowed = track.get('audiodownload_allowed', False)
    
    if not download_url or not download_allowed:
        print("❌ 该音乐不允许下载")
        return None
    
    track_name = track.get('name', 'Unknown').replace('/', '_')
    output_file = output_dir / f"{track_name}.mp3"
    
    try:
        print(f"[下载] {track_name}...")
        response = requests.get(download_url, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = output_file.stat().st_size
            print(f"✅ 下载完成: {file_size / 1024 / 1024:.2f} MB")
            return output_file
        else:
            print(f"❌ 下载失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None

# 使用示例
output_dir = Path('downloads')
output_dir.mkdir(exist_ok=True)

for track in results:
    download_track(track, output_dir)
```

### 下载注意事项

1. **权限检查**: 
   - 始终检查 `audiodownload_allowed` 字段
   - 某些音乐可能需要商业授权才能下载

2. **文件格式**:
   - `audiodownload` 链接返回的是 MP3 文件
   - 虽然 Content-Type 可能显示 `text/html`，但实际内容是 MP3
   - 可以通过文件头验证（MP3 文件以 `ID3` 或 `FF FB` 开头）

3. **文件大小**:
   - mp32 格式：通常 2-5 MB（高质量）
   - mp31 格式：通常 1-3 MB（低质量，适合试听）

4. **下载限制**:
   - 建议使用流式下载（`stream=True`）处理大文件
   - 可以添加进度条显示下载进度

### UI 集成建议

在 UI 中实现下载功能：

```python
# 前端点击下载按钮
def on_download_click(track):
    download_url = track['audiodownload']
    download_allowed = track.get('audiodownload_allowed', False)
    
    if not download_allowed:
        show_message("该音乐不允许下载")
        return
    
    # 方式1: 直接下载（浏览器会处理）
    window.open(download_url)
    
    # 方式2: 通过后端下载（可以添加进度条）
    # 发送请求到后端 API，后端下载后返回文件
```

### 测试结果

✅ **下载功能完全可用**:
- 测试下载了完整的 MP3 文件（3.34 MB）
- 文件格式正确，可以正常播放
- 无需额外授权即可下载（对于允许下载的音乐）

---

## 🖼️ 专辑封面图片功能

### 封面图片获取

Jamendo API **完全支持获取专辑封面图片**，且无需额外配置：

- ✅ **搜索结果直接包含**: `image` 和 `album_image` 字段
- ✅ **两个字段值相同**: 都指向专辑封面 URL
- ✅ **URL 格式**: `https://usercontent.jamendo.com?type=album&id={album_id}&width=300&trackid={track_id}`

### 获取不同尺寸的封面

可以通过修改 URL 中的 `width` 参数获取不同尺寸的封面：

```python
# 从搜索结果获取封面（默认 300x300）
track = results[0]
cover_url = track.get('image') or track.get('album_image')
# cover_url: https://usercontent.jamendo.com?type=album&id=365590&width=300&trackid=1593988

# 获取不同尺寸（修改 width 参数）
small_cover = cover_url.replace('width=300', 'width=200')   # 200x200
large_cover = cover_url.replace('width=300', 'width=500')   # 500x500
```

### 通过专辑 API 获取封面

也可以通过专辑 API 获取封面：

```python
import requests

album_id = track.get('album_id')
album_url = "https://api.jamendo.com/v3.0/albums/"
params = {
    "client_id": client_id,
    "format": "json",
    "id": album_id,
}
response = requests.get(album_url, params=params)
album_info = response.json()["results"][0]
cover_url = album_info.get('image')
```

### 封面尺寸说明

- **默认尺寸**: 300x300（适合列表显示）
- **可用尺寸**: 通过修改 `width` 参数，支持 200, 300, 400, 500 等
- **建议用途**:
  - 列表显示: 200-300px
  - 详情页: 400-500px

## 🔄 后续优化建议

1. **推荐度字段**: 如果 Jamendo 提供更高权限的 API，可获取真实的 popularity 数据
2. **音频下载**: 集成 `audiodownload` 字段，实现自动下载功能
3. **数据存储**: 将搜索结果存入 `storage/music_library.py`，与 TikTok 数据统一管理
4. **错误处理**: 增加网络重试、限流检测等机制
5. **封面图片**: ✅ 已支持，可直接使用搜索结果中的 `image` 或 `album_image` 字段

---

## ✅ 结论

**Jamendo API 测试成功**，可以作为 BGM Hunter 项目的备选音乐源：
- ✅ API 调用稳定
- ✅ 搜索结果丰富（每个关键词返回 50+ 首）
- ✅ 提供音频链接和元数据
- ✅ **支持获取专辑封面图片**（无需额外配置，多尺寸可选）
- ✅ **支持获取丰富的音乐标签**（genres, instruments, vartags 等）- **推荐系统核心！** ⭐
- ✅ 可作为 TikTok Creative Center 的补充方案

### 特别优势

**Jamendo API 的标签系统非常适合构建 BGM 推荐系统**：
- ✅ 多维度标签：类型、乐器、情绪、场景
- ✅ 结构化数据：易于处理和匹配
- ✅ 丰富的信息：可以精确匹配用户需求
- ✅ 无需额外配置：只需添加 `include=musicinfo` 参数

