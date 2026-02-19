# BGM Hunter Pro - Full Optimization Design

**Date**: 2026-02-18
**Scope**: Code quality, architecture, functionality, consistency

---

## 1. Code Quality & Type Safety

### 1.1 Enable TypeScript strict mode
- Add `"strict": true` to `tsconfig.json`

### 1.2 Eliminate `any` types
| Location | Issue | Fix |
|----------|-------|-----|
| `constants.tsx:43` | `MOCK_MUSIC: any[]` | Delete entirely (dead code) |
| `jamendoService.ts:41` | `track: any` in `.map()` | Define `JamendoTrackResponse` interface |
| `tagMappingService.ts:99` | `mappings as any` | Add typed interface for `tag_mapping.json` |
| `useAudioAnalyzer.ts:17` | `(window as any).webkitAudioContext` | Extend `Window` interface via `declare global` |

### 1.3 Named exports everywhere
- `App.tsx`: Change `export default App` to `export const App`
- `index.tsx`: Update import accordingly

### 1.4 Comments unified to English
- Convert all Chinese comments to English across all source files

---

## 2. Architecture - Custom Hooks Extraction

### Current problem
`App.tsx` is 740 lines with 15+ `useState`, 5 `useEffect`, and heavy business logic mixed with UI.

### 2.1 `hooks/usePersistedState.ts` (NEW)
**Responsibility**: Reusable localStorage-backed state
```ts
export function usePersistedState<T>(key: string, defaultValue: T): [T, (value: T) => void]
```
Replaces 4 identical patterns in App.tsx for preferences, theme, glow, collections.

### 2.2 `hooks/usePlayer.ts` (NEW)
**Responsibility**: Audio playback control
- **State**: `isPlaying`, `currentTrackIndex`, `currentTime`, `duration`, `audioError`
- **Logic**: `togglePlay`, `seek`, `next`, `prev`, play sync effect, error handling, auto-next on end
- **Refs**: `audioRef`, `playPromiseRef`
- **Interface**:
```ts
{
  isPlaying, currentTrack, currentTrackIndex,
  togglePlay, seek, next, prev,
  currentTime, duration, audioError,
  audioRef, setTracks, setCurrentTrackIndex, setIsPlaying
}
```

### 2.3 `hooks/useSearch.ts` (NEW)
**Responsibility**: Search and refresh logic
- **State**: `isLoading`, `tracks`, `analysis`, `lastSearchData`, `recommendedTrackIds`
- **Logic**: `handleSearch`, `handleRefresh` (includes tag classification, preference merging, API calls)
- **Extracts**: `mergeWithPreferences`, `isMoodTag`, `getRandomTags` as private helpers
- **Interface**:
```ts
{
  isLoading, tracks, analysis,
  search: (data: SearchData) => Promise<void>,
  refresh: () => Promise<void>,
  mood: Mood
}
```

### 2.4 `hooks/useCollections.ts` (NEW)
**Responsibility**: Collection management with localStorage persistence
- **State**: `collections`, `isModalOpen`
- **Logic**: `save`, `openModal`, `closeModal`, `isTrackInCollection`
- **Interface**:
```ts
{
  collections, isModalOpen,
  save: (collections: Collection[]) => void,
  openModal, closeModal,
  isTrackInCollection: (trackId: string) => boolean
}
```

### 2.5 Resulting App.tsx (~150 lines)
Composed from hooks, contains only:
- View state management (`landing` / `results`)
- Preferences modal state
- JSX layout orchestration

---

## 3. Service Layer Unification

### 3.1 Create `services/aiService.ts` (NEW)
Extract shared DeepSeek API call logic:
```ts
export async function callDeepSeek(prompt: string): Promise<string>
```
- Handles: fetch call, auth headers, JSON response parsing, markdown code block stripping, error handling
- Single source of truth for DeepSeek API interaction

### 3.2 Simplify `deepseekService.ts`
- Keep `analyzeInput` function
- Fix signature: add missing `selectedTags?: string[]` parameter
- Replace inline fetch with `callDeepSeek(prompt)`
- Remove duplicate JSON parsing logic

### 3.3 Simplify `tagMappingService.ts`
- Keep `TagMappingService` class with `mapTagsWithAI` and `mapTagsStatic`
- Replace inline fetch with `callDeepSeek(prompt)`
- Remove duplicate JSON parsing logic
- Remove `setApiKey` pattern (get key from env directly, like deepseekService does)

### 3.4 Delete `geminiService.ts`
No longer needed; confirmed by user.

---

## 4. Dead Code Cleanup

| Item | Reason |
|------|--------|
| `constants.tsx` - `MOCK_MUSIC` | Completely unused test data |
| `geminiService.ts` | Confirmed removal |
| `trackValidationService.ts` - `validateTrack()` | No-cors makes HEAD request useless |
| `trackValidationService.ts` - `testPlayability()` | Never called from anywhere |
| `TrackValidationService` import in `jamendoService.ts` | Imported but never used |

After cleanup, `trackValidationService.ts` only has `validateTracks()` (quick filter). Consider inlining it into `jamendoService.ts` since it's trivial.

---

## 5. Functionality Fixes

| Bug | Fix |
|-----|-----|
| SkipBack/SkipForward buttons do nothing | Wire to `player.prev()` / `player.next()` in CentralPlayer |
| `analyzeInput` called with 4 args but only accepts 3 | Add `selectedTags?: string[]` param to deepseekService's `analyzeInput` |
| Audio error handler duplicated (JSX `onError` + `useEffect` listener) | Unify in `usePlayer` hook, remove JSX `onError` |
| SearchPanel tag buttons: nested `.map()` without outer key | Use `flatMap` or add `React.Fragment` with compound key |
| `constants.tsx` file extension should be `.ts` not `.tsx` | Rename - no JSX in this file (after MOCK_MUSIC removal) |

---

## 6. UI Text Consistency

Unify all UI text to English:

### CollectionModal.tsx
| Chinese | English |
|---------|---------|
| 收藏清单 | Collections |
| 创建新清单 | Create Collection |
| 输入清单名称... | Enter collection name... |
| 创建 | Create |
| 取消 | Cancel |
| 还没有收藏清单 | No collections yet |
| 创建第一个清单来保存你喜欢的歌曲 | Create your first collection to save your favorite tracks |
| X 首歌曲 | X tracks |
| 清单为空 | Collection is empty |
| 添加当前歌曲 | Add current track |

### PreferencesModal.tsx
| Chinese | English |
|---------|---------|
| 封面光晕效果 | Cover glow effect |

---

## 7. File Structure After Refactoring

```
bgm-hunter-pro/
  index.html
  index.tsx
  App.tsx                          (~150 lines, down from 740)
  types.ts
  constants.ts                     (renamed from .tsx, MOCK_MUSIC removed)
  hooks/
    useAudioAnalyzer.ts            (existing, minor fixes)
    usePlayer.ts                   (NEW)
    useSearch.ts                   (NEW)
    useCollections.ts              (NEW)
    usePersistedState.ts           (NEW)
  services/
    aiService.ts                   (NEW - shared DeepSeek API logic)
    deepseekService.ts             (simplified)
    jamendoService.ts              (typed, validation inlined)
    tagMappingService.ts           (simplified)
  components/
    input/SearchPanel.tsx           (minor fixes)
    player/CentralPlayer.tsx        (SkipBack/SkipForward wired)
    visualizer/Scene3D.tsx          (no changes)
    settings/PreferencesModal.tsx   (text fix)
    collection/CollectionModal.tsx  (text unified to English)
  data/
    jamendo_tags.json
    tag_mapping.json

DELETED:
  services/geminiService.ts
  services/trackValidationService.ts (inlined into jamendoService)
```

---

## 8. Implementation Order

1. **Phase 1 - Foundation**: tsconfig strict, type fixes, named exports, rename constants.tsx -> constants.ts
2. **Phase 2 - Service layer**: Create aiService.ts, simplify deepseek/tagMapping services, delete gemini/trackValidation
3. **Phase 3 - Hooks extraction**: usePersistedState, usePlayer, useSearch, useCollections
4. **Phase 4 - App.tsx refactor**: Rewrite to use extracted hooks
5. **Phase 5 - Component fixes**: SkipBack/Forward, SearchPanel keys, error handler dedup
6. **Phase 6 - Text consistency**: All comments to English, all UI text to English
7. **Phase 7 - Verification**: Build check, manual smoke test
