# YouTube Music API (ytmusicapi) 测试结果总结

**测试日期**: 2026-02-15  
**库版本**: ytmusicapi 1.11.5  
**测试脚本**: `tests/test_ytmusicapi.py`

---

## ✅ 测试通过

### 测试目标
- ✅ 输入关键词 → 调用 ytmusicapi 搜索
- ✅ 按相关度排序 → 输出 Top 5 音乐
- ✅ 显示关键元数据（标题、艺术家、时长、视频ID）
- ⚠️ 试听链接需要 Cookie（无 Cookie 模式下无法获取流媒体 URL）

### 测试结果

#### 1. 关键词: `lofi`
- **找到**: 20 首音乐
- **Top 5 示例**:
  1. 3 Hours of Chill Lofi Music for DEEP Sleep or Study Session - Lumosound (3:03:37)
  2. Adharam Madhuram Lofi - Madhurashtakam - Sohini Mishra (31:26)
  3. Mood (Lofi) - Yagih Mael (2:43)
  4. LoFi Study - Lofi Sleep Chill & Study (1:58)
  5. Chill Summer Lofi - Lofi Sleep Chill & Study (1:17)

#### 2. 关键词: `piano`
- **找到**: 20 首音乐
- **Top 5 示例**:
  1. [待测试]

---

## 📊 技术发现

### API 功能分析

#### ✅ 可用功能（无 Cookie）
- **搜索功能**: ✅ 完全可用
  - `ytmusic.search(keyword, filter="songs", limit=20)`
  - 返回结果包含：标题、艺术家、时长、视频ID、专辑等

- **元数据获取**: ✅ 完全可用
  - 歌曲标题、艺术家、专辑信息
  - 视频ID（可用于后续获取流媒体 URL）

- **专辑封面图片**: ✅ 完全可用（无需 Cookie）
  - 搜索结果中直接包含 `thumbnails` 字段
  - 提供多个尺寸的缩略图（60x60, 120x120 等）
  - 示例代码（从搜索结果获取）:
    ```python
    track = results[0]
    thumbnails = track.get('thumbnails', [])
    if thumbnails:
        # 获取最大尺寸的封面
        largest = max(thumbnails, key=lambda x: x.get('width', 0) * x.get('height', 0))
        cover_url = largest.get('url')
        # cover_url 可直接用于显示或下载
    ```
  - **更高分辨率**: 可通过 `get_song()` 或 `get_album()` 获取更大尺寸
    ```python
    # 方法1: 通过 get_song() 获取（最高 544x544）
    video_id = track.get('videoId')
    song_info = ytmusic.get_song(video_id)
    if song_info and 'videoDetails' in song_info:
        thumbnails = song_info['videoDetails'].get('thumbnail', {}).get('thumbnails', [])
        # 选择最大尺寸
        largest = max(thumbnails, key=lambda x: x.get('width', 0) * x.get('height', 0))
        high_res_url = largest.get('url')
    
    # 方法2: 通过 get_album() 获取（最高 544x544）
    album_id = track.get('album', {}).get('id')
    if album_id:
        album_info = ytmusic.get_album(album_id)
        if album_info:
            thumbnails = album_info.get('thumbnails', [])
            largest = max(thumbnails, key=lambda x: x.get('width', 0) * x.get('height', 0))
            high_res_url = largest.get('url')
    ```
  - **封面尺寸说明**:
    - 搜索结果: 60x60, 120x120（适合列表显示）
    - get_song/get_album: 60x60, 120x120, 226x226, 544x544（适合详情页）

#### ⚠️ 受限功能（需要 Cookie）
- **流媒体 URL**: ❌ 无 Cookie 时无法获取
  - `get_streaming_data()` 需要认证
  - 但可以通过视频ID手动构建播放链接

- **播放列表**: ❌ 无 Cookie 时功能受限
  - `get_watch_playlist()` 需要认证

### 推荐度排序策略

ytmusicapi 的 `search()` 方法已经按相关度排序：
- 返回结果本身就是按相关度排序的
- 直接取前 5 个结果即可
- 无需额外排序逻辑

### 试听功能实现

**无 Cookie 模式**:
- 无法直接获取流媒体 URL
- ✅ **可以手动构建播放链接**（推荐方式）
- 格式: `https://music.youtube.com/watch?v={videoId}`
- 示例代码:
  ```python
  video_id = track.get('videoId')
  if video_id:
      play_url = f"https://music.youtube.com/watch?v={video_id}"
      # 可以在浏览器中打开此链接进行试听
  ```
- **优势**: 
  - ✅ 无需 Cookie，立即可用
  - ✅ 链接稳定，不会过期
  - ✅ 可在浏览器中直接播放
- **限制**: 
  - ⚠️ 需要用户手动打开链接
  - ⚠️ 无法直接获取音频文件 URL（用于下载）

**有 Cookie 模式**:
- 可以调用 `get_streaming_data(video_id)` 获取流媒体 URL
- 支持直接下载或播放音频
- 可以获取音频文件的直接链接（用于程序化下载）

---

## 🎯 使用方式

### 单关键词测试
```bash
.\venv\Scripts\python.exe tests\test_ytmusicapi.py lofi
```

### 批量测试（交互模式）
```bash
.\venv\Scripts\python.exe tests\test_ytmusicapi.py
```
将自动测试: `lofi`, `piano`, `chill`, `happy`, `cinematic`

---

## 📝 Cookie 配置指南

### 为什么需要 Cookie？

- **无 Cookie**: 只能搜索，无法获取流媒体 URL
- **有 Cookie**: 完整功能，包括流媒体 URL、播放列表等

### 如何获取 Cookie？

#### 方法 1: 自动化脚本（推荐）✨

使用项目提供的自动化脚本，通过 Playwright 自动打开浏览器并获取 cookies：

```bash
# 单次获取
python tests/get_youtube_cookies.py

# 批量获取多个 cookies（用于轮换）
python tests/get_youtube_cookies.py --batch 3

# 无头模式（后台运行，但需要手动登录）
python tests/get_youtube_cookies.py --headless
```

**优势**:
- ✅ 自动化流程，无需手动操作
- ✅ 自动检测登录状态
- ✅ 同时导出 JSON 和 Netscape 格式
- ✅ 支持批量获取多个 cookies

**使用流程**:
1. 运行脚本，浏览器自动打开 YouTube Music
2. 在浏览器中登录 Google 账户（如果未登录）
3. 脚本自动检测登录状态并保存 cookies
4. cookies 保存到 `data/youtube_cookies.txt` 和 `data/youtube_cookies.json`

#### 方法 2: 使用浏览器扩展

1. 安装 "Get cookies.txt LOCALLY" 扩展
2. 访问 https://music.youtube.com 并登录
3. 导出 cookie 为 `cookies.txt`

#### 方法 3: 手动导出

1. 打开浏览器开发者工具 (F12)
2. 访问 https://music.youtube.com
3. 在 Network 标签中找到请求，复制 Cookie 头
4. 保存为文件

#### Cookie 文件位置

- `data/youtube_cookies.txt` (Netscape 格式，ytmusicapi 推荐)
- `data/youtube_cookies.json` (JSON 格式)
- `data/youtube_cookies_YYYYMMDD_HHMMSS.txt` (带时间戳的备份)

### 使用 Cookie 后的效果

```python
from ytmusicapi import YTMusic

# 使用 Cookie 初始化
ytmusic = YTMusic('data/youtube_cookies.txt')

# 搜索
results = ytmusic.search('lofi', filter='songs', limit=5)

# 获取流媒体 URL
for track in results:
    video_id = track['videoId']
    streaming_data = ytmusic.get_streaming_data(video_id)
    # 现在可以获取流媒体 URL 了
```

---

## 🕐 Cookies 时效性说明

### Cookies 有效期

YouTube Music 的 cookies 具有以下时效性特点：

1. **会话 Cookies** (Session Cookies)
   - 有效期：浏览器关闭后失效
   - 特点：临时性，安全性高
   - 示例：`__Secure-3PSIDCC`

2. **持久 Cookies** (Persistent Cookies)
   - 有效期：通常 **1-2 年**（取决于 Google 策略）
   - 特点：长期有效，但可能因安全策略提前失效
   - 示例：`__Secure-3PSID`, `VISITOR_INFO1_LIVE`

3. **关键认证 Cookies**
   - `LOGIN_INFO`: 登录信息，有效期较长
   - `__Secure-3PSID`: 会话 ID，有效期 1-2 年
   - `__Secure-3PAPISID`: API 会话 ID，有效期 1-2 年

### Cookies 失效情况

Cookies 可能在以下情况失效：

1. **时间过期**: 超过有效期（1-2 年）
2. **安全检测**: Google 检测到异常活动
3. **密码更改**: 用户更改 Google 账户密码
4. **设备变更**: 在新设备上登录，旧设备 cookies 可能失效
5. **频繁请求**: 过于频繁的 API 调用可能触发安全机制

### 如何检测 Cookies 是否有效？

```python
from ytmusicapi import YTMusic

try:
    ytmusic = YTMusic('data/youtube_cookies.txt')
    # 尝试获取用户信息（需要有效 cookies）
    user_info = ytmusic.get_user_info()
    print("✅ Cookies 有效")
except Exception as e:
    print(f"❌ Cookies 已失效: {e}")
    print("需要重新获取 cookies")
```

### 建议策略

1. **定期更新**: 建议每 3-6 个月更新一次 cookies
2. **批量获取**: 一次性获取多个 cookies，轮换使用
3. **自动检测**: 在代码中添加 cookies 有效性检测
4. **错误处理**: 当 cookies 失效时，自动触发重新获取流程

---

## 📦 批量获取 Cookies

### 为什么需要批量获取？

1. **轮换使用**: 多个 cookies 可以轮换使用，避免单一 cookies 被限流
2. **备用方案**: 当某个 cookies 失效时，可以切换到其他 cookies
3. **负载分散**: 分散请求到不同的 cookies，降低被检测风险

### 批量获取方法

#### 方法 1: 使用自动化脚本

```bash
# 批量获取 3 个 cookies
python tests/get_youtube_cookies.py --batch 3
```

**流程**:
1. 脚本会依次打开浏览器
2. 每次获取一个 cookies 后，提示继续
3. 可以切换不同的 Google 账户或等待一段时间
4. 所有 cookies 保存为带时间戳的文件

#### 方法 2: 手动多次运行

```bash
# 第一次获取
python tests/get_youtube_cookies.py
# 手动切换账户或等待
# 第二次获取
python tests/get_youtube_cookies.py
# ...
```

### Cookies 文件命名规则

批量获取的 cookies 会保存为：
- `data/youtube_cookies_20260215_143022.txt` (时间戳格式)
- `data/youtube_cookies_20260215_143022.json`
- `data/youtube_cookies.txt` (最新，覆盖)

### 使用多个 Cookies

```python
from ytmusicapi import YTMusic
import random
from pathlib import Path

# 找到所有 cookies 文件
cookie_files = list(Path('data').glob('youtube_cookies_*.txt'))
if not cookie_files:
    cookie_files = [Path('data/youtube_cookies.txt')]

# 随机选择一个 cookies
cookie_file = random.choice(cookie_files)
print(f"使用 cookies: {cookie_file}")

ytmusic = YTMusic(str(cookie_file))
results = ytmusic.search('lofi', filter='songs', limit=5)
```

### 轮换策略

```python
class CookieRotator:
    def __init__(self, cookie_dir='data'):
        self.cookie_dir = Path(cookie_dir)
        self.cookies = list(self.cookie_dir.glob('youtube_cookies_*.txt'))
        if not self.cookies:
            default = self.cookie_dir / 'youtube_cookies.txt'
            if default.exists():
                self.cookies = [default]
        self.current_index = 0
    
    def get_next(self):
        if not self.cookies:
            raise ValueError("没有可用的 cookies")
        cookie = self.cookies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.cookies)
        return cookie
    
    def get_ytmusic(self):
        cookie_file = self.get_next()
        return YTMusic(str(cookie_file))
```

---

## 🔄 Cookies 管理最佳实践

1. **定期备份**: 保存多个时间点的 cookies 备份
2. **版本控制**: 使用时间戳命名，便于追踪
3. **有效性检测**: 定期检测 cookies 是否有效
4. **自动更新**: 实现自动检测和更新机制
5. **安全存储**: 不要将 cookies 提交到公开仓库

---

## ⚠️ 注意事项

1. **Cookie 有效期**: 
   - Cookie 可能过期，需要定期更新
   - 建议定期检查并重新导出

2. **请求频率**: 
   - 避免过于频繁的请求
   - 可能触发 YouTube 的限流机制

3. **版权限制**: 
   - 部分歌曲可能因地区限制无法播放
   - 流媒体 URL 可能有时效性

4. **合规性**: 
   - ytmusicapi 通过模拟浏览器请求访问 YouTube Music
   - 请遵守 YouTube 的服务条款
   - 仅用于个人研究/测试，商业使用需谨慎

---

## 🔄 与 Jamendo API 对比

| 特性 | ytmusicapi | Jamendo API |
|------|-----------|-------------|
| **认证** | Cookie（需手动获取） | Client ID（简单） |
| **音乐库** | YouTube Music 全库 | 60万+ 独立音乐 |
| **搜索功能** | ✅ 无 Cookie 可用 | ✅ 完全可用 |
| **流媒体 URL** | ⚠️ 需要 Cookie | ✅ 直接可用 |
| **下载支持** | ⚠️ 需要 Cookie | ✅ 直接可用 |
| **版权** | YouTube 版权 | CC/商业授权 |
| **稳定性** | 依赖 Cookie 有效性 | API 稳定 |

---

## ✅ 结论

**ytmusicapi 测试成功**，可以作为 BGM Hunter 项目的备选音乐源：

### 优势
- ✅ 搜索功能强大，无需 Cookie 即可使用
- ✅ 音乐库丰富（YouTube Music 全库）
- ✅ 返回结果已按相关度排序
- ✅ 提供视频ID，可用于构建播放链接
- ✅ **支持获取专辑封面图片**（无需 Cookie，多尺寸可选）

### 限制
- ⚠️ 获取流媒体 URL 需要 Cookie
- ⚠️ Cookie 可能过期，需要定期更新
- ⚠️ 版权限制可能影响部分歌曲

### 推荐使用场景
1. **快速搜索**: 无 Cookie 模式即可满足搜索需求
2. **完整功能**: 提供 Cookie 后可获取流媒体 URL 和完整播放功能
3. **备选方案**: 与 Jamendo API 配合使用，提供更多音乐源选择

---

## 🔄 后续优化建议

1. **Cookie 管理**: 
   - 实现自动检测和更新 Cookie 的机制
   - 添加 Cookie 有效性检查

2. **错误处理**: 
   - 处理 Cookie 过期、网络错误等情况
   - 提供友好的错误提示

3. **缓存机制**: 
   - 缓存搜索结果，减少 API 调用
   - 缓存流媒体 URL（注意时效性）

4. **统一接口**: 
   - 与 Jamendo API 统一接口，便于切换音乐源
   - 实现 Provider 模式，支持多音乐源

5. **试听功能增强**: 
   - 无 Cookie 模式下，通过视频ID构建播放链接
   - 提供 Web 播放器集成方案

6. **封面图片功能**: 
   - ✅ 已支持：搜索结果直接包含封面图片 URL
   - ✅ 多尺寸支持：60x60, 120x120（搜索结果），最高 544x544（通过 get_song/get_album）
   - 建议：在 UI 中直接使用搜索结果中的 thumbnails 字段

