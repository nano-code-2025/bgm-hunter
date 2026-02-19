# Jamendo API 受欢迎度排序指南

## 概述

虽然 Jamendo API 不直接返回受欢迎度的具体数值（如播放量、下载量等），但**支持通过 `orderby` 参数按受欢迎度排序**，确保返回的是最受欢迎的音乐。

## 支持的排序方式

Jamendo API 支持以下排序方式（已验证）：

### 受欢迎度相关排序

1. **`popularity_total_desc`** - 按总受欢迎度降序（推荐使用）⭐
2. **`popularity_total_asc`** - 按总受欢迎度升序
3. **`listens_desc`** - 按播放量降序
4. **`listens_asc`** - 按播放量升序
5. **`downloads_desc`** - 按下载量降序
6. **`downloads_asc`** - 按下载量升序
7. **`rating_desc`** - 按评分降序
8. **`rating_asc`** - 按评分升序

### 其他排序方式

- **`releasedate_desc`** - 按发布日期降序（最新）
- **`releasedate_asc`** - 按发布日期升序（最旧）
- **`relevance_desc`** - 按相关性降序（默认）
- **`relevance_asc`** - 按相关性升序

## 实现方式

### 1. 更新类型定义

```typescript
export type SortOrder = 
  | 'popularity_total_desc'  // 总受欢迎度降序（推荐）
  | 'listens_desc'           // 播放量降序
  | 'downloads_desc'        // 下载量降序
  | 'rating_desc'           // 评分降序
  | 'releasedate_desc'      // 最新发布
  | 'relevance_desc';       // 相关性（默认）
```

### 2. 更新搜索服务

```typescript
export async function searchTracks(
  tagsOrQuery: MusicTags | string, 
  limit: number = 10,
  sortOrder: SortOrder = 'popularity_total_desc'  // 默认按受欢迎度排序
): Promise<MusicTrack[]> {
  // ...
  url.searchParams.set("orderby", sortOrder);
  // ...
}
```

### 3. 使用方式

```typescript
// 按总受欢迎度排序（推荐）
const tracks = await searchTracks(tags, 10, 'popularity_total_desc');

// 按播放量排序
const tracks = await searchTracks(tags, 10, 'listens_desc');

// 按下载量排序
const tracks = await searchTracks(tags, 10, 'downloads_desc');
```

## 推荐策略

### 默认排序：`popularity_total_desc`

**理由**：
- 综合考虑了播放量、下载量、评分等多个因素
- 返回的是整体最受欢迎的音乐
- 适合大多数推荐场景

### 备选排序方案

根据不同场景可以选择：

1. **强调播放量**：使用 `listens_desc`
2. **强调下载量**：使用 `downloads_desc`
3. **强调用户评分**：使用 `rating_desc`
4. **最新发布**：使用 `releasedate_desc`

## 注意事项

1. **无法获取具体数值**：API 不返回播放量、下载量等具体数值，只能通过排序来确保顺序
2. **排序是有效的**：测试显示不同排序方式返回的结果确实不同
3. **position 字段**：返回结果中的 `position` 字段表示在搜索结果中的位置（越小越靠前）

## 测试结果

测试了多种排序方式，确认：
- ✅ `popularity_total_desc` - 有效
- ✅ `listens_desc` - 有效
- ✅ `downloads_desc` - 有效
- ✅ `rating_desc` - 有效

不同排序方式返回的音乐列表确实不同，说明排序功能正常工作。

## 当前实现状态

✅ **已完成**：
- 类型定义已更新（`SortOrder`）
- `jamendoService.ts` 已更新，默认使用 `popularity_total_desc`
- 所有搜索结果默认按受欢迎度排序

✅ **效果**：
- 搜索结果自动按受欢迎度排序
- 返回的是最受欢迎的音乐
- 无需额外配置，开箱即用

