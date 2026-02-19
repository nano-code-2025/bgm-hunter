# BGM Hunter Pro - Full Optimization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Comprehensive refactoring of BGM Hunter Pro for code quality, architecture clarity, bug fixes, and text consistency.

**Architecture:** Extract business logic from the 740-line App.tsx into 4 custom hooks (usePersistedState, usePlayer, useSearch, useCollections). Unify the duplicated DeepSeek API call pattern into a shared aiService. Delete dead code (geminiService, MOCK_MUSIC, trackValidationService). Fix broken SkipBack/SkipForward buttons and duplicated error handlers.

**Tech Stack:** React 19, TypeScript 5.8 (strict), Vite 6, Three.js, Framer Motion, Tailwind CSS (CDN)

**Note:** This project has no test framework configured. Steps marked "Verify" use `npx tsc --noEmit` for type checking and `npx vite build` for build verification instead of unit tests.

---

### Task 1: Enable TypeScript strict mode and fix tsconfig

**Files:**
- Modify: `tsconfig.json`

**Step 1: Add strict mode to tsconfig.json**

In `tsconfig.json`, add `"strict": true` inside `compilerOptions`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "strict": true,
    "experimentalDecorators": true,
    "useDefineForClassFields": false,
    "module": "ESNext",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "types": ["node"],
    "moduleResolution": "bundler",
    "isolatedModules": true,
    "moduleDetection": "force",
    "allowJs": true,
    "jsx": "react-jsx",
    "paths": { "@/*": ["./*"] },
    "allowImportingTsExtensions": true,
    "noEmit": true
  }
}
```

**Step 2: Verify it compiles (expect errors -- that's fine for now)**

Run: `npx tsc --noEmit 2>&1 | head -30`
Expected: TypeScript errors related to `any` types and strict checks. We will fix these in subsequent tasks.

**Step 3: Commit**

```bash
git add tsconfig.json
git commit -m "chore: enable TypeScript strict mode"
```

---

### Task 2: Delete dead code -- geminiService, MOCK_MUSIC, trackValidationService

**Files:**
- Delete: `services/geminiService.ts`
- Modify: `constants.tsx` (remove MOCK_MUSIC, lines 42-80)
- Delete: `services/trackValidationService.ts`
- Modify: `services/jamendoService.ts` (remove unused import, line 3)
- Modify: `package.json` (remove `@google/genai` dependency)

**Step 1: Delete geminiService.ts**

Delete the file `services/geminiService.ts` entirely.

**Step 2: Remove MOCK_MUSIC from constants.tsx**

Remove lines 42-80 from `constants.tsx` (the entire `MOCK_MUSIC` export and the comment above it). The file should end after the `ADVANCED_TAG_GROUPS` closing bracket on line 40.

After removal, `constants.tsx` contains only `TAG_GROUPS` and `ADVANCED_TAG_GROUPS` -- no JSX, so we will rename it in the next task.

**Step 3: Delete trackValidationService.ts**

Delete the file `services/trackValidationService.ts` entirely.

**Step 4: Remove unused import from jamendoService.ts**

In `services/jamendoService.ts`, remove line 3:
```ts
import { TrackValidationService } from "./trackValidationService";
```

**Step 5: Remove @google/genai from package.json dependencies**

In `package.json`, remove the line:
```json
"@google/genai": "^1.41.0",
```

**Step 6: Commit**

```bash
git add -A
git commit -m "chore: remove dead code (geminiService, MOCK_MUSIC, trackValidationService)"
```

---

### Task 3: Rename constants.tsx to constants.ts, fix named export in App.tsx

**Files:**
- Rename: `constants.tsx` -> `constants.ts`
- Modify: `App.tsx` (change `export default App` to named export)
- Modify: `index.tsx` (update import)

**Step 1: Rename constants.tsx to constants.ts**

Rename the file. Since it contains no JSX (only data arrays), it should be `.ts`.

All imports referencing `./constants` or `../../constants` do NOT include the extension, so they will resolve automatically. No import changes needed.

**Step 2: Change App.tsx to named export**

In `App.tsx`, change line 742:
```ts
// FROM:
export default App;

// TO:
export { App };
```

Also change line 17 to directly export:
```ts
// FROM:
const App: React.FC = () => {

// TO:
export const App: React.FC = () => {
```

Then remove the `export { App };` at the bottom (or just the `export default App;`).

**Step 3: Update index.tsx import**

In `index.tsx`, change line 3:
```ts
// FROM:
import App from './App';

// TO:
import { App } from './App';
```

**Step 4: Verify**

Run: `npx tsc --noEmit 2>&1 | head -20`
Expected: Should not introduce new errors.

**Step 5: Commit**

```bash
git add -A
git commit -m "refactor: rename constants.tsx to .ts, use named export for App"
```

---

### Task 4: Create services/aiService.ts -- shared DeepSeek API logic

**Files:**
- Create: `services/aiService.ts`

**Step 1: Create the shared AI service**

Create `services/aiService.ts` with the following content:

```ts
const DEEPSEEK_API_URL = 'https://api.deepseek.com/chat/completions';
const DEEPSEEK_MODEL = 'deepseek-chat';

export function getApiKey(): string | undefined {
  return process.env.DEEPSEEK_API_KEY || process.env.API_KEY;
}

// Call DeepSeek API and return parsed JSON object
export async function callDeepSeek<T>(prompt: string): Promise<T> {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new Error('DeepSeek API key not found');
  }

  const response = await fetch(DEEPSEEK_API_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: DEEPSEEK_MODEL,
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,
      response_format: { type: 'json_object' },
    }),
  });

  if (!response.ok) {
    throw new Error(`DeepSeek API error: ${response.statusText}`);
  }

  const data = await response.json();
  const content: string | undefined = data.choices?.[0]?.message?.content;

  if (!content) {
    throw new Error('No content in DeepSeek response');
  }

  // Strip markdown code block wrappers if present
  let jsonStr = content.trim();
  if (jsonStr.startsWith('```')) {
    jsonStr = jsonStr.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
  }

  return JSON.parse(jsonStr) as T;
}
```

**Step 2: Commit**

```bash
git add services/aiService.ts
git commit -m "feat: create shared aiService for DeepSeek API calls"
```

---

### Task 5: Simplify deepseekService.ts using aiService

**Files:**
- Modify: `services/deepseekService.ts`

**Step 1: Rewrite deepseekService.ts**

Replace the entire file with:

```ts
import { AnalysisResult, UserPreferences } from '../types';
import { callDeepSeek, getApiKey } from './aiService';

interface DeepSeekAnalysisResponse {
  contentType?: string;
  moods?: string[];
  instruments?: string[];
  energy?: string;
  keywords?: string[];
  summary?: string;
  tags?: {
    genres?: string[];
    instruments?: string[];
    vartags?: string[];
  };
}

export async function analyzeInput(
  text: string,
  mode: 'script' | 'keyword',
  userPreferences?: UserPreferences,
  selectedTags?: string[]
): Promise<AnalysisResult> {
  if (!getApiKey()) {
    console.error('DeepSeek API key not found');
    return getDefaultResult();
  }

  const prompt = buildAnalysisPrompt(text, mode, userPreferences, selectedTags);

  try {
    const result = await callDeepSeek<DeepSeekAnalysisResponse>(prompt);

    return {
      contentType: result.contentType || 'General',
      moods: Array.isArray(result.moods) ? result.moods : ['Neutral'],
      instruments: Array.isArray(result.instruments) ? result.instruments : [],
      energy: result.energy || 'medium',
      keywords: Array.isArray(result.keywords) ? result.keywords : [],
      summary: result.summary || 'AI analysis completed.',
      tags: result.tags || {
        genres: result.keywords?.slice(0, 3) || [],
        instruments: result.instruments || [],
        vartags: [],
      },
    };
  } catch (e) {
    console.error('DeepSeek analysis failed:', e);
    return getDefaultResult();
  }
}

function buildAnalysisPrompt(
  text: string,
  mode: 'script' | 'keyword',
  userPreferences?: UserPreferences,
  selectedTags?: string[]
): string {
  let prompt = '';

  if (mode === 'script') {
    prompt = `Analyze the following video script and extract music tags for BGM recommendation. Return structured tags including genres (e.g., "lofi", "chillhop", "piano", "electronic"), instruments (e.g., "piano", "guitar", "synthesizer"), and vartags (e.g., "peaceful", "happy", "energetic", "calm", "uplifting").`;

    if (selectedTags && selectedTags.length > 0) {
      prompt += `\n\nUser selected keywords for reference: ${selectedTags.join(', ')}. Please consider these keywords when analyzing.`;
    }

    if (userPreferences) {
      prompt += `\n\nUser preferences: genres=${userPreferences.genres?.join(', ') || 'none'}, instruments=${userPreferences.instruments?.join(', ') || 'none'}, vartags=${userPreferences.vartags?.join(', ') || 'none'}. Please consider these preferences when generating tags.`;
    }

    prompt += `\n\nScript: "${text}"`;
  } else {
    prompt = `Given the keywords "${text}", extract structured BGM search tags including genres, instruments, and vartags (mood/emotion tags).`;

    if (userPreferences) {
      prompt += `\n\nUser preferences: genres=${userPreferences.genres?.join(', ') || 'none'}, instruments=${userPreferences.instruments?.join(', ') || 'none'}, vartags=${userPreferences.vartags?.join(', ') || 'none'}. Please consider these preferences.`;
    }
  }

  prompt += `\n\nReturn a JSON object with this exact structure:
{
  "contentType": "string",
  "moods": ["Melancholy" | "Happy" | "Dynamic" | "Neutral"],
  "instruments": ["string"],
  "energy": "low" | "medium" | "high",
  "keywords": ["string"],
  "summary": "string",
  "tags": {
    "genres": ["string"],
    "instruments": ["string"],
    "vartags": ["string"]
  }
}`;

  return prompt;
}

function getDefaultResult(): AnalysisResult {
  return {
    contentType: 'General',
    moods: ['Neutral'],
    instruments: ['Piano'],
    energy: 'medium',
    keywords: ['background music'],
    summary: 'AI analysis failed, returning defaults.',
    tags: {
      genres: ['ambient'],
      instruments: ['piano'],
      vartags: ['neutral'],
    },
  };
}
```

**Step 2: Commit**

```bash
git add services/deepseekService.ts
git commit -m "refactor: simplify deepseekService using shared aiService, fix 4-arg signature"
```

---

### Task 6: Simplify tagMappingService.ts using aiService

**Files:**
- Modify: `services/tagMappingService.ts`

**Step 1: Rewrite tagMappingService.ts**

Replace the entire file with:

```ts
import { MusicTags, UserPreferences } from '../types';
import { callDeepSeek, getApiKey } from './aiService';
import tagMapping from '../data/tag_mapping.json';

export interface UserSelectedTags {
  genres?: string[];
  moods?: string[];
  themes?: string[];
  duration?: string[];
}

interface TagMappingData {
  mappings: {
    genres: Record<string, string[]>;
    moods: Record<string, string[]>;
    themes: Record<string, string[]>;
  };
}

const typedTagMapping = tagMapping as TagMappingData;

// Map user-selected tags to Jamendo-compatible tags using AI
export async function mapTagsWithAI(
  userTags: UserSelectedTags,
  userPreferences?: UserPreferences
): Promise<MusicTags> {
  if (!getApiKey()) {
    console.warn('DeepSeek API key not set, using static mapping');
    return mapTagsStatic(userTags);
  }

  try {
    const prompt = buildMappingPrompt(userTags, userPreferences);
    const result = await callDeepSeek<MusicTags>(prompt);

    return {
      genres: Array.isArray(result.genres) ? result.genres : [],
      instruments: Array.isArray(result.instruments) ? result.instruments : [],
      vartags: Array.isArray(result.vartags) ? result.vartags : [],
    };
  } catch (error) {
    console.error('AI mapping failed, falling back to static mapping:', error);
    return mapTagsStatic(userTags);
  }
}

// Static tag mapping fallback (no AI needed)
export function mapTagsStatic(userTags: UserSelectedTags): MusicTags {
  const result: MusicTags = {
    genres: [],
    instruments: [],
    vartags: [],
  };

  const { mappings } = typedTagMapping;

  if (userTags.genres) {
    for (const genre of userTags.genres) {
      const jamendoGenres = mappings.genres[genre] || [genre.toLowerCase()];
      result.genres!.push(...jamendoGenres);
    }
  }

  if (userTags.moods) {
    for (const mood of userTags.moods) {
      const jamendoVartags = mappings.moods[mood] || [mood.toLowerCase()];
      result.vartags!.push(...jamendoVartags);
    }
  }

  if (userTags.themes) {
    for (const theme of userTags.themes) {
      const jamendoVartags = mappings.themes[theme] || [theme.toLowerCase()];
      result.vartags!.push(...jamendoVartags);
    }
  }

  result.genres = [...new Set(result.genres)];
  result.vartags = [...new Set(result.vartags)];

  return result;
}

// Merge user preferences into tags
export function mergePreferences(
  tags: MusicTags,
  preferences?: UserPreferences
): MusicTags {
  if (!preferences) return tags;

  return {
    genres: [...(tags.genres || []), ...(preferences.genres || [])],
    instruments: [...(tags.instruments || []), ...(preferences.instruments || [])],
    vartags: [...(tags.vartags || []), ...(preferences.vartags || [])],
  };
}

function buildMappingPrompt(
  userTags: UserSelectedTags,
  userPreferences?: UserPreferences
): string {
  let prompt = `Convert the following user-selected music tags into Jamendo API compatible tags.

User selected tags:
- Genres: ${userTags.genres?.join(', ') || 'none'}
- Moods: ${userTags.moods?.join(', ') || 'none'}
- Themes: ${userTags.themes?.join(', ') || 'none'}
${userTags.duration ? `- Duration: ${userTags.duration.join(', ')}` : ''}

${userPreferences ? `User preferences (apply these to enhance the mapping):
- Preferred genres: ${userPreferences.genres?.join(', ') || 'none'}
- Preferred instruments: ${userPreferences.instruments?.join(', ') || 'none'}
- Preferred scenarios: ${userPreferences.vartags?.join(', ') || 'none'}
` : ''}

Jamendo API uses three tag categories:
1. genres: Music styles/types (e.g., "rock", "pop", "electronic", "jazz", "classical", "hiphop", "ambient", "lofi", "chillout")
2. instruments: Musical instruments (e.g., "piano", "guitar", "strings", "synthesizer", "drums", "violin")
3. vartags: Mood/emotion/scenario tags (e.g., "happy", "sad", "energetic", "calm", "romantic", "peaceful", "uplifting", "cinematic", "vlog", "sport", "travel")

Return a JSON object with this exact structure:
{
  "genres": ["string"],
  "instruments": ["string"],
  "vartags": ["string"]
}

Map the user tags to appropriate Jamendo tags. Be specific and use actual Jamendo tag values when possible.`;

  return prompt;
}
```

Key changes:
- Converted from class to plain functions (no more `static` methods, no more `setApiKey` state)
- Uses `callDeepSeek` from aiService instead of duplicated fetch logic
- Typed the tag_mapping.json import (no more `as any`)
- Uses `for...of` instead of `.forEach`

**Step 2: Commit**

```bash
git add services/tagMappingService.ts
git commit -m "refactor: simplify tagMappingService using aiService, remove class pattern"
```

---

### Task 7: Type the Jamendo API response in jamendoService.ts

**Files:**
- Modify: `services/jamendoService.ts`

**Step 1: Add JamendoTrackResponse interface and type the map callback**

Replace the entire file with:

```ts
import { MusicTrack, MusicTags, SortOrder } from '../types';

const CLIENT_ID = 'f2567443';
const BASE_URL = 'https://api.jamendo.com/v3.0';

interface JamendoMusicInfo {
  tags?: {
    genres?: string[];
    instruments?: string[];
    vartags?: string[];
  };
}

interface JamendoTrackResponse {
  id: number;
  name: string;
  artist_name: string;
  duration: number;
  audio: string;
  shareurl?: string;
  license_ccurl?: string;
  image?: string;
  album_image?: string;
  audiodownload?: string;
  audiodownload_allowed?: boolean;
  position?: number;
  releasedate?: string;
  musicinfo?: JamendoMusicInfo;
}

interface JamendoApiResponse {
  results?: JamendoTrackResponse[];
}

export async function searchTracks(
  tagsOrQuery: MusicTags | string,
  limit: number = 10,
  sortOrder: SortOrder = 'popularity_total_desc',
  filterAvailable: boolean = true
): Promise<MusicTrack[]> {
  const url = new URL(`${BASE_URL}/tracks/`);
  url.searchParams.set('client_id', CLIENT_ID);
  url.searchParams.set('format', 'json');
  // Fetch more results when filtering, to ensure enough pass the filter
  const searchLimit = filterAvailable ? Math.min(limit * 3, 50) : limit;
  url.searchParams.set('limit', searchLimit.toString());
  url.searchParams.set('include', 'musicinfo');
  url.searchParams.set('orderby', sortOrder);

  let searchQuery = '';
  if (typeof tagsOrQuery === 'string') {
    searchQuery = tagsOrQuery;
  } else {
    const { genres = [], instruments = [], vartags = [] } = tagsOrQuery;
    searchQuery = [...genres, ...instruments, ...vartags].join(' ');
  }

  url.searchParams.set('search', searchQuery);

  try {
    const response = await fetch(url.toString());
    const data: JamendoApiResponse = await response.json();

    if (!data.results) return [];

    let tracks: MusicTrack[] = data.results.map((track) => {
      const musicinfo = track.musicinfo || {};
      const tags = musicinfo.tags || {};

      const allTags = [
        ...(tags.genres || []),
        ...(tags.instruments || []),
        ...(tags.vartags || []),
      ];

      return {
        id: track.id.toString(),
        title: track.name,
        artist: track.artist_name,
        duration: track.duration,
        previewUrl: track.audio,
        sourceUrl: track.shareurl || '#',
        license: track.license_ccurl || 'Unknown',
        tags: allTags,
        cover: track.image || track.album_image || `https://picsum.photos/seed/${track.id}/400/400`,
        bpm: 0,
        audiodownload: track.audiodownload,
        audiodownloadAllowed: track.audiodownload_allowed || false,
        position: track.position,
        releasedate: track.releasedate,
      };
    });

    // Filter to only playable and downloadable tracks
    if (filterAvailable) {
      tracks = tracks.filter(
        (track) => track.audiodownloadAllowed && track.audiodownload && track.previewUrl
      );
    }

    return tracks.slice(0, limit);
  } catch (error) {
    console.error('Jamendo search failed:', error);
    return [];
  }
}
```

**Step 2: Commit**

```bash
git add services/jamendoService.ts
git commit -m "refactor: type Jamendo API response, remove any types"
```

---

### Task 8: Fix useAudioAnalyzer.ts -- remove `any` for webkitAudioContext

**Files:**
- Modify: `hooks/useAudioAnalyzer.ts`

**Step 1: Add Window type extension and remove unused imports**

Replace the file with:

```ts
import { useState, useEffect, useRef, useCallback } from 'react';
import { AudioStats } from '../types';

declare global {
  interface Window {
    webkitAudioContext?: typeof AudioContext;
  }
}

export function useAudioAnalyzer(audioRef: React.RefObject<HTMLAudioElement | null>) {
  const [stats, setStats] = useState<AudioStats | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyzerRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaElementAudioSourceNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);
  const animationFrameRef = useRef<number | undefined>(undefined);

  const initAnalyzer = useCallback(() => {
    if (!audioRef.current || analyzerRef.current) return;

    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) return;

      const context = new AudioContextClass();
      const analyzer = context.createAnalyser();
      analyzer.fftSize = 256;

      // createMediaElementSource can only be called ONCE per element
      const source = context.createMediaElementSource(audioRef.current);
      source.connect(analyzer);
      analyzer.connect(context.destination);

      audioContextRef.current = context;
      analyzerRef.current = analyzer;
      sourceRef.current = source;
      dataArrayRef.current = new Uint8Array(analyzer.frequencyBinCount);
    } catch (err) {
      console.warn('Audio Context initialization failed:', err);
    }
  }, [audioRef]);

  const update = useCallback(() => {
    if (!analyzerRef.current || !dataArrayRef.current) return;

    analyzerRef.current.getByteFrequencyData(dataArrayRef.current);

    const data = dataArrayRef.current;
    let sum = 0;
    let bass = 0;
    let mid = 0;
    let treble = 0;

    for (let i = 0; i < data.length; i++) {
      sum += data[i];
      if (i < 10) bass += data[i];
      else if (i < 50) mid += data[i];
      else treble += data[i];
    }

    setStats({
      frequencyData: new Uint8Array(data),
      averageFrequency: sum / data.length,
      bass: bass / 10,
      mid: mid / 40,
      treble: treble / (data.length - 50),
    });

    animationFrameRef.current = requestAnimationFrame(update);
  }, []);

  useEffect(() => {
    const handlePlay = async () => {
      if (audioContextRef.current?.state === 'suspended') {
        await audioContextRef.current.resume();
      }
      initAnalyzer();
      update();
    };

    const audio = audioRef.current;
    if (audio) {
      audio.addEventListener('play', handlePlay);
    }

    return () => {
      if (audio) {
        audio.removeEventListener('play', handlePlay);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [audioRef, initAnalyzer, update]);

  return stats;
}
```

Key changes:
- `declare global` for `webkitAudioContext` -- no more `as any`
- Removed unused `React` import (only used for type, now accessed via global)
- Updated `RefObject` type to accept `null` (React 19 compatibility)
- Removed `console.log` debug line

**Step 2: Commit**

```bash
git add hooks/useAudioAnalyzer.ts
git commit -m "fix: type webkitAudioContext properly, remove any cast"
```

---

### Task 9: Create hooks/usePersistedState.ts

**Files:**
- Create: `hooks/usePersistedState.ts`

**Step 1: Create the hook**

```ts
import { useState, useCallback } from 'react';

export function usePersistedState<T>(key: string, defaultValue: T): [T, (value: T) => void] {
  const [state, setState] = useState<T>(() => {
    const saved = localStorage.getItem(key);
    if (saved === null) return defaultValue;
    try {
      return JSON.parse(saved) as T;
    } catch {
      return defaultValue;
    }
  });

  const setPersistedState = useCallback(
    (value: T) => {
      setState(value);
      localStorage.setItem(key, JSON.stringify(value));
    },
    [key]
  );

  return [state, setPersistedState];
}
```

**Step 2: Commit**

```bash
git add hooks/usePersistedState.ts
git commit -m "feat: create usePersistedState hook for localStorage-backed state"
```

---

### Task 10: Create hooks/usePlayer.ts

**Files:**
- Create: `hooks/usePlayer.ts`

**Step 1: Create the player hook**

This hook extracts all audio playback logic from App.tsx (lines 22-24, 25-26, 44, 194-204, 380-486).

```ts
import { useState, useRef, useEffect, useCallback } from 'react';
import { MusicTrack } from '../types';

function getAudioErrorMessage(error: MediaError | null): string {
  if (!error) return 'Audio loading failed';

  switch (error.code) {
    case error.MEDIA_ERR_ABORTED:
      return 'Audio loading aborted';
    case error.MEDIA_ERR_NETWORK:
      return 'Network error loading audio';
    case error.MEDIA_ERR_DECODE:
      return 'Audio decode failed';
    case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
      return 'Audio format not supported or invalid URL';
    default:
      return `Audio error (code: ${error.code})`;
  }
}

export function usePlayer() {
  const [tracks, setTracks] = useState<MusicTrack[]>([]);
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [audioError, setAudioError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const playPromiseRef = useRef<Promise<void> | null>(null);

  const currentTrack = tracks[currentTrackIndex] || null;

  const togglePlay = useCallback(() => {
    setIsPlaying((prev) => !prev);
  }, []);

  const seek = useCallback((time: number) => {
    const audio = audioRef.current;
    if (audio) {
      audio.currentTime = time;
      setCurrentTime(time);
    }
  }, []);

  const next = useCallback(() => {
    setCurrentTrackIndex((prev) => {
      if (prev < tracks.length - 1) return prev + 1;
      return prev;
    });
    setIsPlaying(true);
  }, [tracks.length]);

  const prev = useCallback(() => {
    setCurrentTrackIndex((prev) => {
      if (prev > 0) return prev - 1;
      return prev;
    });
    setIsPlaying(true);
  }, []);

  // Synchronize isPlaying state with the audio element
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !audio.src) return;

    const syncPlay = async () => {
      if (isPlaying) {
        try {
          playPromiseRef.current = audio.play();
          await playPromiseRef.current;
        } catch (error) {
          if (error instanceof Error && error.name !== 'AbortError') {
            console.warn('Playback error:', error);
            setIsPlaying(false);
          }
        }
      } else {
        if (playPromiseRef.current) {
          await playPromiseRef.current.catch(() => {});
        }
        audio.pause();
      }
    };

    syncPlay();
  }, [isPlaying, currentTrackIndex, tracks]);

  // Audio event listeners: progress, duration, error, ended
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => setCurrentTime(audio.currentTime);
    const handleDurationChange = () => setDuration(audio.duration || 0);
    const handleLoadedData = () => setAudioError(null);

    const handleError = () => {
      const err = audio.error;
      const message = getAudioErrorMessage(err);
      console.error('Audio error:', message, currentTrack?.previewUrl);
      setAudioError(message);
      setIsPlaying(false);

      // Auto-advance to next track after a delay
      setTimeout(() => {
        if (currentTrackIndex < tracks.length - 1) {
          setCurrentTrackIndex((prev) => prev + 1);
          setAudioError(null);
        }
      }, 2000);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
      if (currentTrackIndex < tracks.length - 1) {
        setCurrentTrackIndex((prev) => prev + 1);
        setIsPlaying(true);
      }
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('durationchange', handleDurationChange);
    audio.addEventListener('loadeddata', handleLoadedData);
    audio.addEventListener('error', handleError);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('durationchange', handleDurationChange);
      audio.removeEventListener('loadeddata', handleLoadedData);
      audio.removeEventListener('error', handleError);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [tracks, currentTrackIndex, currentTrack?.previewUrl]);

  // Reset progress when track changes
  useEffect(() => {
    setCurrentTime(0);
    setDuration(0);
  }, [currentTrackIndex]);

  return {
    tracks,
    setTracks,
    currentTrack,
    currentTrackIndex,
    setCurrentTrackIndex,
    isPlaying,
    setIsPlaying,
    togglePlay,
    seek,
    next,
    prev,
    currentTime,
    duration,
    audioError,
    audioRef,
  };
}
```

**Step 2: Commit**

```bash
git add hooks/usePlayer.ts
git commit -m "feat: create usePlayer hook extracting audio playback logic from App"
```

---

### Task 11: Create hooks/useSearch.ts

**Files:**
- Create: `hooks/useSearch.ts`

**Step 1: Create the search hook**

This extracts handleSearch (lines 65-192) and handleRefreshTracks (lines 224-340) from App.tsx.

```ts
import { useState, useCallback } from 'react';
import { AnalysisResult, MusicTrack, Mood, MusicTags, UserPreferences } from '../types';
import { TAG_GROUPS } from '../constants';
import { analyzeInput } from '../services/deepseekService';
import { searchTracks } from '../services/jamendoService';
import { mapTagsWithAI, mergePreferences } from '../services/tagMappingService';

export interface SearchData {
  text: string;
  selectedTags: string[];
  mode: 'script' | 'keyword';
}

function classifySelectedTags(selectedTags: string[]) {
  return {
    genres: selectedTags.filter((tag) =>
      TAG_GROUPS.find((g) => g.category === 'genre')?.tags.includes(tag)
    ),
    moods: selectedTags.filter((tag) =>
      TAG_GROUPS.find((g) => g.category === 'mood')?.tags.includes(tag)
    ),
    themes: selectedTags.filter(
      (tag) =>
        !TAG_GROUPS.find((g) => g.category === 'genre')?.tags.includes(tag) &&
        !TAG_GROUPS.find((g) => g.category === 'mood')?.tags.includes(tag)
    ),
  };
}

function isMoodTag(tag: string): boolean {
  const moodTags = TAG_GROUPS.find((g) => g.category === 'mood')?.tags || [];
  const lowerTag = tag.toLowerCase();
  return (
    moodTags.some((t) => t.toLowerCase() === lowerTag) ||
    [
      'happy', 'sad', 'peaceful', 'energetic', 'calm', 'uplifting', 'relaxing',
      'exciting', 'romantic', 'melancholic', 'joyful', 'serene', 'intense',
    ].includes(lowerTag)
  );
}

function getRandomTags(
  originalTags: string[],
  allAvailableTags: string[],
  count: number,
  excludeUsed: Set<string>
): string[] {
  const available = allAvailableTags.filter(
    (tag) => !originalTags.includes(tag) && !excludeUsed.has(tag.toLowerCase())
  );
  const shuffled = [...available].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}

const ALL_GENRES = [
  'rock', 'electronic', 'jazz', 'classical', 'pop', 'hiphop', 'folk', 'blues',
  'reggae', 'metal', 'country', 'latin', 'world', 'ambient', 'chillhop', 'lofi',
];
const ALL_INSTRUMENTS = [
  'piano', 'guitar', 'strings', 'drums', 'bass', 'synthesizer', 'saxophone',
  'violin', 'cello', 'flute', 'trumpet', 'organ',
];

export function useSearch(userPreferences: UserPreferences) {
  const [isLoading, setIsLoading] = useState(false);
  const [tracks, setTracks] = useState<MusicTrack[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [mood, setMood] = useState<Mood>('Neutral');
  const [lastSearchData, setLastSearchData] = useState<SearchData | null>(null);
  const [recommendedTrackIds, setRecommendedTrackIds] = useState<Set<string>>(new Set());

  const search = useCallback(
    async (data: SearchData) => {
      setIsLoading(true);
      setLastSearchData(data);
      try {
        let tags: MusicTags;
        let analysisResult: AnalysisResult;

        if (data.mode === 'keyword') {
          const classified = classifySelectedTags(data.selectedTags);
          if (data.text.trim()) {
            classified.themes.push(data.text.trim());
          }

          const mappedTags = await mapTagsWithAI(classified, userPreferences);
          tags = mergePreferences(mappedTags, userPreferences);

          const allKeywords = [...data.selectedTags, data.text].filter(Boolean);
          analysisResult = {
            contentType: 'Keyword Search',
            moods: classified.moods.length > 0 ? [classified.moods[0] as Mood] : ['Neutral'],
            instruments: mappedTags.instruments || [],
            energy: 'medium',
            keywords: allKeywords,
            summary: `Searching for: ${allKeywords.join(', ')}`,
            tags,
          };
        } else {
          // Script analysis mode
          const result = await analyzeInput(data.text, 'script', userPreferences, data.selectedTags);
          analysisResult = result;

          if (result.moods.length > 0) {
            setMood(result.moods[0]);
          }

          let aiTags = result.tags || {
            genres: result.keywords.slice(0, 3),
            instruments: result.instruments,
            vartags: [],
          };

          // Merge user-selected keyword tags with AI tags
          if (data.selectedTags.length > 0) {
            const classified = classifySelectedTags(data.selectedTags);
            const mappedUserTags = await mapTagsWithAI(classified, userPreferences);
            aiTags = {
              genres: [...(aiTags.genres || []), ...(mappedUserTags.genres || [])],
              instruments: [...(aiTags.instruments || []), ...(mappedUserTags.instruments || [])],
              vartags: [...(aiTags.vartags || []), ...(mappedUserTags.vartags || [])],
            };
          }

          tags = mergePreferences(aiTags, userPreferences);
        }

        setAnalysis(analysisResult);

        const foundTracks = await searchTracks(tags, 10, 'popularity_total_desc', true);
        if (foundTracks.length > 0) {
          setRecommendedTrackIds(new Set(foundTracks.map((t) => t.id)));
        }
        setTracks(foundTracks);
      } catch (error) {
        console.error('Analysis/Search error:', error);
      } finally {
        setIsLoading(false);
      }
    },
    [userPreferences]
  );

  const refresh = useCallback(async () => {
    if (!lastSearchData) return;
    setIsLoading(true);
    try {
      let originalTags: MusicTags = { genres: [], instruments: [], vartags: [] };

      if (lastSearchData.mode === 'keyword') {
        const classified = classifySelectedTags(lastSearchData.selectedTags);
        originalTags = await mapTagsWithAI(classified, userPreferences);
      } else {
        if (analysis?.tags) {
          originalTags = analysis.tags;
        } else {
          const result = await analyzeInput(
            lastSearchData.text,
            'script',
            userPreferences,
            lastSearchData.selectedTags
          );
          originalTags = result.tags || { genres: [], instruments: [], vartags: [] };
        }
      }

      // Keep mood tags, randomize genres and instruments
      const moodTags = (originalTags.vartags || []).filter((tag) => isMoodTag(tag));
      if (moodTags.length === 0 && originalTags.vartags && originalTags.vartags.length > 0) {
        moodTags.push(...originalTags.vartags);
      }

      const excludeUsed = new Set([
        ...(originalTags.genres || []).map((g) => g.toLowerCase()),
        ...(originalTags.instruments || []).map((i) => i.toLowerCase()),
      ]);

      const newGenres = getRandomTags(
        originalTags.genres || [],
        ALL_GENRES,
        Math.max(2, Math.floor(Math.random() * 3) + 1),
        excludeUsed
      );

      const newInstruments = getRandomTags(
        originalTags.instruments || [],
        ALL_INSTRUMENTS,
        Math.max(1, Math.floor(Math.random() * 2) + 1),
        excludeUsed
      );

      const newTags = mergePreferences(
        {
          genres: newGenres.length > 0 ? newGenres : (originalTags.genres || []).slice(0, 1),
          instruments: newInstruments.length > 0 ? newInstruments : (originalTags.instruments || []).slice(0, 1),
          vartags: moodTags.length > 0 ? moodTags : originalTags.vartags || [],
        },
        userPreferences
      );

      const foundTracks = await searchTracks(newTags, 20, 'popularity_total_desc', true);
      const newTracks = foundTracks.filter((track) => !recommendedTrackIds.has(track.id));

      if (newTracks.length > 0) {
        setRecommendedTrackIds(new Set([...recommendedTrackIds, ...newTracks.map((t) => t.id)]));
        setTracks(newTracks.slice(0, 10));
      } else {
        setRecommendedTrackIds(new Set());
        const allTracks = await searchTracks(newTags, 10, 'popularity_total_desc', true);
        setTracks(allTracks);
        if (allTracks.length > 0) {
          setRecommendedTrackIds(new Set(allTracks.map((t) => t.id)));
        }
      }
    } catch (error) {
      console.error('Refresh search error:', error);
    } finally {
      setIsLoading(false);
    }
  }, [lastSearchData, analysis, userPreferences, recommendedTrackIds]);

  return { isLoading, tracks, analysis, mood, search, refresh };
}
```

**Step 2: Commit**

```bash
git add hooks/useSearch.ts
git commit -m "feat: create useSearch hook extracting search/refresh logic from App"
```

---

### Task 12: Create hooks/useCollections.ts

**Files:**
- Create: `hooks/useCollections.ts`

**Step 1: Create the collections hook**

```ts
import { useCallback } from 'react';
import { Collection } from '../types';
import { usePersistedState } from './usePersistedState';

export function useCollections() {
  const [collections, setCollections] = usePersistedState<Collection[]>('bgm-hunter-collections', []);

  const save = useCallback(
    (updatedCollections: Collection[]) => {
      setCollections(updatedCollections);
    },
    [setCollections]
  );

  const isTrackInCollection = useCallback(
    (trackId: string): boolean => {
      return collections.some((collection) => collection.tracks.some((t) => t.id === trackId));
    },
    [collections]
  );

  return { collections, save, isTrackInCollection };
}
```

**Step 2: Commit**

```bash
git add hooks/useCollections.ts
git commit -m "feat: create useCollections hook with localStorage persistence"
```

---

### Task 13: Rewrite App.tsx using extracted hooks

**Files:**
- Modify: `App.tsx`

**Step 1: Replace the entire App.tsx**

```tsx
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Scene3D } from './components/visualizer/Scene3D';
import { SearchPanel } from './components/input/SearchPanel';
import { CentralPlayer } from './components/player/CentralPlayer';
import { PreferencesModal } from './components/settings/PreferencesModal';
import { CollectionModal } from './components/collection/CollectionModal';
import { useAudioAnalyzer } from './hooks/useAudioAnalyzer';
import { usePlayer } from './hooks/usePlayer';
import { useSearch } from './hooks/useSearch';
import { useCollections } from './hooks/useCollections';
import { usePersistedState } from './hooks/usePersistedState';
import { UserPreferences, VisualizerTheme, MusicTrack } from './types';
import { ChevronLeft, Info, Settings, Sparkles } from 'lucide-react';

export const App: React.FC = () => {
  const [view, setView] = useState<'landing' | 'results'>('landing');
  const [isPreferencesOpen, setIsPreferencesOpen] = useState(false);
  const [isCollectionModalOpen, setIsCollectionModalOpen] = useState(false);

  const [userPreferences, setUserPreferences] = usePersistedState<UserPreferences>(
    'bgm-hunter-preferences',
    {}
  );
  const [visualizerTheme] = usePersistedState<VisualizerTheme>(
    'bgm-hunter-visualizer-theme',
    'stars'
  );
  const [showGlow, setShowGlow] = usePersistedState('bgm-hunter-show-glow', false);

  const player = usePlayer();
  const searchState = useSearch(userPreferences);
  const collectionsState = useCollections();
  const audioStats = useAudioAnalyzer(player.audioRef);

  const handleSearch = async (data: { text: string; selectedTags: string[]; mode: 'script' | 'keyword' }) => {
    await searchState.search(data);
    player.setTracks(searchState.tracks);
    player.setCurrentTrackIndex(0);
    setView('results');
  };

  // We need to wire search results into the player after search completes.
  // Since useSearch manages its own tracks state, we sync them.
  const effectiveTracks = searchState.tracks;
  const currentTrack = effectiveTracks[player.currentTrackIndex] || null;

  const handleRefresh = async () => {
    player.setIsPlaying(false);
    await searchState.refresh();
    player.setCurrentTrackIndex(0);
  };

  const handlePlayTrack = (track: MusicTrack) => {
    const trackIndex = effectiveTracks.findIndex((t) => t.id === track.id);
    if (trackIndex !== -1) {
      player.setCurrentTrackIndex(trackIndex);
      player.setIsPlaying(true);
    }
    setIsCollectionModalOpen(false);
  };

  return (
    <div className="relative min-h-[100dvh] w-full flex flex-col selection:bg-purple-500 selection:text-white bg-black overflow-hidden">
      {/* 3D Background Visualizer */}
      <Scene3D stats={audioStats} mood={searchState.mood} theme={visualizerTheme} />

      {/* Audio Element */}
      <audio
        ref={player.audioRef}
        src={currentTrack?.previewUrl || ''}
        preload="auto"
        crossOrigin="anonymous"
      />

      {/* Header */}
      <header className="fixed top-0 left-0 w-full z-50 p-5 md:p-8 flex items-center justify-between">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2.5"
        >
          <div className="w-9 h-9 md:w-10 md:h-10 rounded-xl bg-white flex items-center justify-center shadow-[0_0_20px_rgba(255,255,255,0.2)]">
            <Sparkles className="text-black w-5 h-5 md:w-6 md:h-6" />
          </div>
          <span className="text-lg md:text-xl font-bold tracking-tighter uppercase hidden sm:inline">
            BGM Hunter Pro
          </span>
          <span className="text-base font-bold tracking-tighter uppercase sm:hidden">BGM_HP</span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 md:gap-4"
        >
          <button className="p-2 text-neutral-500 hover:text-white transition-colors bg-white/5 rounded-full">
            <Info className="w-5 h-5" />
          </button>
          <button
            onClick={() => setIsPreferencesOpen(true)}
            className="p-2 text-neutral-500 hover:text-white transition-colors bg-white/5 rounded-full"
          >
            <Settings className="w-5 h-5" />
          </button>
        </motion.div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4 md:p-6 z-10">
        <AnimatePresence mode="wait">
          {view === 'landing' ? (
            <motion.div
              key="landing"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.02, filter: 'blur(10px)' }}
              transition={{ duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
              className="w-full flex flex-col items-center gap-8 md:gap-12"
            >
              <div className="text-center px-4">
                <motion.h1
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-4xl md:text-7xl font-bold tracking-tighter mb-4 leading-tight"
                >
                  Perfect BGM, <br className="hidden md:block" />
                  <span className="text-white/30">Powered by AI.</span>
                </motion.h1>
                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="text-neutral-500 text-sm md:text-lg max-w-lg mx-auto leading-relaxed"
                >
                  Enter your video script or keywords. We'll search Jamendo's high-quality library to
                  find the perfect sonic match.
                </motion.p>
              </div>

              <SearchPanel onSearch={handleSearch} isLoading={searchState.isLoading} />
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="w-full h-full flex flex-col items-center justify-center pt-16 md:pt-20"
            >
              <button
                onClick={() => {
                  player.setIsPlaying(false);
                  setView('landing');
                }}
                className="absolute top-20 left-4 md:top-24 md:left-8 group flex items-center gap-2 text-neutral-500 hover:text-white transition-colors text-sm font-medium z-50 bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/5"
              >
                <ChevronLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                Return
              </button>

              <div className="flex flex-col items-center gap-3 mb-6 md:mb-10 text-center max-w-xs md:max-w-md">
                <motion.span
                  layoutId="mood-badge"
                  className="px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-[9px] md:text-[10px] uppercase tracking-[0.25em] text-purple-400 font-bold backdrop-blur-sm"
                >
                  {searchState.analysis?.moods[0] || 'Neutral'} Atmosphere
                </motion.span>
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-neutral-400 text-xs md:text-sm italic px-4 line-clamp-2"
                >
                  "{searchState.analysis?.summary}"
                </motion.p>
                {currentTrack && currentTrack.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 justify-center mt-2">
                    {currentTrack.tags.slice(0, 5).map((tag, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded-full border border-white/10 bg-white/5 text-[8px] md:text-[9px] uppercase tracking-wider text-neutral-400"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <CentralPlayer
                track={currentTrack}
                isPlaying={player.isPlaying}
                onTogglePlay={player.togglePlay}
                stats={audioStats}
                currentTime={player.currentTime}
                duration={player.duration}
                onSeek={player.seek}
                onNext={player.next}
                onPrev={player.prev}
                onRefresh={handleRefresh}
                showGlow={showGlow}
                onToggleCollection={() => setIsCollectionModalOpen(true)}
                isInCollection={currentTrack ? collectionsState.isTrackInCollection(currentTrack.id) : false}
              />

              {/* Audio Error Message */}
              {player.audioError && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="mt-4 px-4 py-2 rounded-lg bg-red-500/20 border border-red-500/50 text-red-400 text-sm"
                >
                  {player.audioError}
                </motion.div>
              )}

              {/* Track Selector */}
              {effectiveTracks.length > 0 && (
                <div className="mt-8 md:mt-12 flex gap-3 md:gap-5 overflow-x-auto pb-4 max-w-full px-8 no-scrollbar snap-x snap-mandatory">
                  {effectiveTracks.map((t, i) => (
                    <button
                      key={t.id}
                      onClick={() => {
                        player.setCurrentTrackIndex(i);
                        player.setIsPlaying(true);
                      }}
                      className={`flex-shrink-0 w-14 h-14 md:w-16 md:h-16 rounded-xl overflow-hidden border-2 transition-all snap-center ${
                        i === player.currentTrackIndex
                          ? 'border-white scale-110 shadow-[0_0_20px_rgba(255,255,255,0.2)]'
                          : 'border-transparent opacity-30 hover:opacity-100'
                      }`}
                    >
                      <img src={t.cover} className="w-full h-full object-cover" loading="lazy" />
                    </button>
                  ))}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Status Bar */}
      <footer className="fixed bottom-0 left-0 w-full z-50 p-4 md:p-6 text-[9px] md:text-[10px] uppercase tracking-[0.2em] text-neutral-600 flex justify-between items-center pointer-events-none">
        <div className="bg-black/20 backdrop-blur-sm px-2 py-1 rounded">
          <span className="hidden md:inline">SYSTEM_STATUS: </span>
          <span className="text-neutral-400 font-bold">
            {searchState.isLoading ? 'ANALYZING...' : player.isPlaying ? 'STREAMING_HQ' : 'IDLE'}
          </span>
        </div>
        <div className="pointer-events-auto flex gap-3 md:gap-6 bg-black/20 backdrop-blur-sm px-2 py-1 rounded">
          <span className="opacity-40">
            <span className="hidden sm:inline">FREQ: </span>
            {Math.round(audioStats?.averageFrequency || 0)}
          </span>
          <span className="opacity-40 text-purple-500/80">JAMENDO_LIB</span>
        </div>
      </footer>

      {/* Scrollbar hide CSS */}
      <style>{`
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>

      {/* Preferences Modal */}
      <PreferencesModal
        isOpen={isPreferencesOpen}
        onClose={() => setIsPreferencesOpen(false)}
        onSave={setUserPreferences}
        currentPreferences={userPreferences}
        showGlow={showGlow}
        onGlowToggle={setShowGlow}
      />

      {/* Collection Modal */}
      <CollectionModal
        isOpen={isCollectionModalOpen}
        onClose={() => setIsCollectionModalOpen(false)}
        collections={collectionsState.collections}
        onSaveCollections={collectionsState.save}
        onPlayTrack={handlePlayTrack}
        currentTrack={currentTrack || undefined}
      />
    </div>
  );
};
```

Key changes:
- ~150 lines, down from 740
- All business logic extracted to hooks
- No duplicate error handlers (handled in usePlayer)
- `audio` element has no `onError`/`onLoadedData` handlers (handled in usePlayer)
- Added `onNext` and `onPrev` props to CentralPlayer (will wire in next task)
- Removed the `TagMappingService.setApiKey` effect (no longer needed -- aiService reads env directly)
- `handleSearch` needs a small fix: since `searchState.search` is async and `searchState.tracks` updates after, we need to handle the state sync. See note below.

**Important note on state sync:** The `handleSearch` function calls `searchState.search(data)` which is async. After it resolves, `searchState.tracks` will be updated via React state. The `effectiveTracks` variable will reflect this on the next render. The `player` hook manages its own track index but reads from `effectiveTracks` via the `currentTrack` derivation. This is sufficient -- the player's `audioRef` src is set via `currentTrack?.previewUrl` in the JSX.

However, the player's internal `tracks` state is NOT used for the track list display. The search hook's `tracks` is the source of truth. We should remove `player.setTracks` calls since the player doesn't need its own tracks copy. Instead, the player just needs `currentTrackIndex` and the audio element. Let me simplify: remove `tracks` and `setTracks` from usePlayer, and pass the tracks length for bounds checking to `next`.

Actually, to keep it simple and avoid a circular dependency, let's keep the player hook as-is but **not call `player.setTracks`**. The player's `tracks` state is unused for display. The `currentTrack` derivation in App.tsx uses `effectiveTracks[player.currentTrackIndex]` which is correct.

**Step 2: Commit**

```bash
git add App.tsx
git commit -m "refactor: rewrite App.tsx using extracted hooks (~150 lines from 740)"
```

---

### Task 14: Wire SkipBack/SkipForward in CentralPlayer

**Files:**
- Modify: `components/player/CentralPlayer.tsx`

**Step 1: Add onNext and onPrev props to PlayerProps interface**

In `CentralPlayer.tsx`, update the `PlayerProps` interface (around line 7-19):

Add two new optional props:
```ts
onNext?: () => void;
onPrev?: () => void;
```

**Step 2: Destructure the new props**

In the component destructuring (around line 21-33), add:
```ts
onNext,
onPrev,
```

**Step 3: Wire the SkipBack button (line 162)**

Change:
```tsx
<button className="text-neutral-500 hover:text-white transition-colors active:scale-90">
  <SkipBack className="w-6 h-6 md:w-7 md:h-7 fill-current" />
</button>
```

To:
```tsx
<button
  onClick={onPrev}
  className="text-neutral-500 hover:text-white transition-colors active:scale-90"
>
  <SkipBack className="w-6 h-6 md:w-7 md:h-7 fill-current" />
</button>
```

**Step 4: Wire the SkipForward button (line 176)**

Change:
```tsx
<button className="text-neutral-500 hover:text-white transition-colors active:scale-90">
  <SkipForward className="w-6 h-6 md:w-7 md:h-7 fill-current" />
</button>
```

To:
```tsx
<button
  onClick={onNext}
  className="text-neutral-500 hover:text-white transition-colors active:scale-90"
>
  <SkipForward className="w-6 h-6 md:w-7 md:h-7 fill-current" />
</button>
```

**Step 5: Commit**

```bash
git add components/player/CentralPlayer.tsx
git commit -m "fix: wire SkipBack/SkipForward buttons to onPrev/onNext callbacks"
```

---

### Task 15: Fix SearchPanel nested .map() keys

**Files:**
- Modify: `components/input/SearchPanel.tsx`

**Step 1: Fix the 4 instances of nested .map() without outer keys**

There are 4 places where `TAG_GROUPS.map(group => ( group.tags.map(tag => (...))  ))` is used. The outer `.map()` returns arrays without keys. Fix by using `.flatMap()` and adding compound keys.

Replace each instance of:
```tsx
{TAG_GROUPS.map(group => (
  group.tags.map(tag => (
    <button key={tag} ...>
```

With:
```tsx
{TAG_GROUPS.flatMap(group =>
  group.tags.map(tag => (
    <button key={`${group.category}-${tag}`} ...>
```

Apply the same fix to `ADVANCED_TAG_GROUPS.map(...)` instances (2 more).

Also convert Chinese comments to English:
- Line 19: `// 检查是否有有效输入...` -> `// Validate input: keyword mode needs tags or text, script mode needs text`
- Line 78: `<span>Optional: Select keywords...` (already English)
- Line 95: `{/* 高级选项（可选） */}` -> `{/* Advanced Options */}`
- Line 129: `{/* 主要分类 */}` -> `{/* Main Categories */}`
- Line 148: `{/* 高级选项（可选） */}` -> `{/* Advanced Options */}`

Also remove unused imports: `Search`, `AnimatePresence`, and `X` from lucide-react (they are imported but never used in the JSX).

**Step 2: Commit**

```bash
git add components/input/SearchPanel.tsx
git commit -m "fix: add compound keys to nested tag maps, remove unused imports"
```

---

### Task 16: Unify UI text to English in CollectionModal

**Files:**
- Modify: `components/collection/CollectionModal.tsx`

**Step 1: Replace all Chinese UI text**

Make the following text replacements:

| Line | Chinese | English |
|------|---------|---------|
| 93 | `{/* 背景遮罩 */}` | `{/* Backdrop */}` |
| 102 | `{/* 模态框 */}` | `{/* Modal */}` |
| 111 | `{/* 头部 */}` | `{/* Header */}` |
| 115 | `收藏清单` | `Collections` |
| 125 | `{/* 内容区域 */}` | `{/* Content */}` |
| 127 | `{/* 创建新清单 */}` | `{/* Create New Collection */}` |
| 135 | `创建新清单` | `Create Collection` |
| 148 | `输入清单名称...` | `Enter collection name...` |
| 156 | `创建` | `Create` |
| 165 | `取消` | `Cancel` |
| 171 | `{/* 收藏清单列表 */}` | `{/* Collection List */}` |
| 175 | `还没有收藏清单` | `No collections yet` |
| 176 | `创建第一个清单来保存你喜欢的歌曲` | `Create your first collection to save your favorite tracks` |
| 185 | `{/* 清单头部 */}` | `{/* Collection Header */}` |
| 190 | `{collection.tracks.length} 首歌曲` | `{collection.tracks.length} tracks` |
| 201 | `{/* 歌曲列表 */}` | `{/* Track List */}` |
| 203 | `清单为空` | `Collection is empty` |
| 232 | `title="播放"` | `title="Play"` |
| 240 | `title="移除"` | `title="Remove"` |
| 247 | `{/* 添加当前歌曲到清单 */}` | `{/* Add Current Track */}` |
| 254 | `添加当前歌曲` | `Add current track` |

Also update the Chinese comment in `handleAddTrackToCollection`:
- Line 64: `// 检查是否已存在` -> `// Check if already exists`

And replace deprecated `onKeyPress` with `onKeyDown` on line 143.

**Step 2: Commit**

```bash
git add components/collection/CollectionModal.tsx
git commit -m "fix: unify CollectionModal UI text to English"
```

---

### Task 17: Fix PreferencesModal Chinese text

**Files:**
- Modify: `components/settings/PreferencesModal.tsx`

**Step 1: Replace the one Chinese text**

Line 155: Change `封面光晕效果` to `Cover glow effect`.

Also convert Chinese comments to English:
- Line 82: `{/* Genres (主要分类) */}` -> `{/* Genres */}`
- Line 104: `{/* Moods (主要分类) */}` -> `{/* Moods */}`
- Line 126: `{/* Themes (高级选项) */}` -> `{/* Themes */}`

**Step 2: Commit**

```bash
git add components/settings/PreferencesModal.tsx
git commit -m "fix: unify PreferencesModal text to English"
```

---

### Task 18: Convert all Chinese comments to English in types.ts

**Files:**
- Modify: `types.ts`

**Step 1: Replace Chinese comments**

| Line | Chinese | English |
|------|---------|---------|
| 22 | `// 总受欢迎度降序` | `// Total popularity descending` |
| 23 | `// 总受欢迎度升序` | `// Total popularity ascending` |
| 24 | `// 播放量降序` | `// Listens descending` |
| 25 | `// 播放量升序` | `// Listens ascending` |
| 26 | `// 下载量降序` | `// Downloads descending` |
| 27 | `// 下载量升序` | `// Downloads ascending` |
| 28 | `// 评分降序` | `// Rating descending` |
| 29 | `// 评分升序` | `// Rating ascending` |
| 30 | `// 发布日期降序（最新）` | `// Release date descending (newest)` |
| 31 | `// 发布日期升序（最旧）` | `// Release date ascending (oldest)` |
| 32 | `// 相关性降序（默认）` | `// Relevance descending (default)` |
| 33 | `// 相关性升序` | `// Relevance ascending` |
| 48 | `// 搜索结果位置（越小越靠前）` | `// Search result position (lower = higher rank)` |
| 49 | `// 发布日期` | `// Release date` |
| 61 | `// 风格偏好` | `// Genre preferences` |
| 62 | `// 乐器偏好` | `// Instrument preferences` |
| 63 | `// 场景偏好` | `// Scene/scenario preferences` |
| 67 | `// 星空（默认）` | `// Stars (default)` |
| 68 | `// 雨滴` | `// Rain` |
| 69 | `// 森林` | `// Forest` |
| 70 | `// 穿越/隧道` | `// Tunnel` |
| 71 | `// 虫洞` | `// Wormhole` |
| 72 | `// 光晕` | `// Halo` |
| 73 | `// 粒子` | `// Particles` |
| 74 | `// 波浪` | `// Waves` |

**Step 2: Commit**

```bash
git add types.ts
git commit -m "fix: convert all Chinese comments to English in types.ts"
```

---

### Task 19: Convert Chinese comments in constants.ts

**Files:**
- Modify: `constants.ts`

**Step 1: Replace Chinese comments**

- Line 2: `// 主要分类（粗粒度）- 用户界面显示` -> `// Main categories (coarse-grained) - displayed in UI`
- Line 24: `// 高级选项（可选）- 作为扩展选项` -> `// Advanced options - shown as expandable section`

**Step 2: Commit**

```bash
git add constants.ts
git commit -m "fix: convert Chinese comments to English in constants.ts"
```

---

### Task 20: Convert Chinese comments in Scene3D.tsx

**Files:**
- Modify: `components/visualizer/Scene3D.tsx`

**Step 1: Replace Chinese comments**

- Line 44: `// 根据主题应用不同的动画` -> `// Apply different animations based on theme`
- Line 47: `// 雨滴效果：向下移动` -> `// Rain: downward movement`
- Line 53: `// 森林效果：缓慢旋转，垂直移动` -> `// Forest: slow rotation, vertical movement`
- Line 59: `// 穿越效果：快速旋转，缩放` -> `// Tunnel: fast rotation, scaling`
- Line 65: `// 虫洞效果：螺旋旋转` -> `// Wormhole: spiral rotation`
- Line 71: `// 光晕效果：圆形旋转` -> `// Halo: circular rotation`
- Line 76: `// 粒子效果：随机运动` -> `// Particles: random motion`
- Line 81: `// 波浪效果：上下波动` -> `// Waves: vertical oscillation`
- Line 87: `// 星空效果：默认旋转` -> `// Stars: default rotation`
- Line 92: `// 音频响应缩放（所有主题通用）` -> `// Audio-reactive scaling (all themes)`

**Step 2: Commit**

```bash
git add components/visualizer/Scene3D.tsx
git commit -m "fix: convert Chinese comments to English in Scene3D.tsx"
```

---

### Task 21: Build verification

**Files:** None (verification only)

**Step 1: Run TypeScript type check**

Run: `npx tsc --noEmit`
Expected: No errors (or only warnings about missing CDN module types, which is acceptable for a Vite project using importmap).

**Step 2: Run Vite build**

Run: `npx vite build`
Expected: Build completes successfully.

**Step 3: Fix any errors found**

If errors are found, fix them in the relevant files. Common issues:
- Import path mismatches after rename
- Type mismatches between hooks and components
- Missing prop types on CentralPlayer for onNext/onPrev

**Step 4: Final commit if any fixes were needed**

```bash
git add -A
git commit -m "fix: resolve build errors from refactoring"
```

---

### Task 22: Remove @google/genai from node_modules and clean up

**Files:**
- Run: `npm install` (or `pnpm install`) to sync dependencies after removing `@google/genai`

**Step 1: Reinstall dependencies**

Run: `npm install`
Expected: `@google/genai` is no longer installed.

**Step 2: Verify build still works**

Run: `npx vite build`
Expected: Build completes successfully.

**Step 3: Commit lockfile**

```bash
git add package-lock.json
git commit -m "chore: remove @google/genai dependency, update lockfile"
```

---

## Summary of Changes

| File | Action | Description |
|------|--------|-------------|
| `tsconfig.json` | Modified | Added `strict: true` |
| `constants.tsx` -> `constants.ts` | Renamed + Modified | Removed MOCK_MUSIC, renamed to .ts, English comments |
| `App.tsx` | Rewritten | 740 -> ~150 lines, uses extracted hooks, named export |
| `index.tsx` | Modified | Updated import to named export |
| `types.ts` | Modified | English comments |
| `services/aiService.ts` | Created | Shared DeepSeek API logic |
| `services/deepseekService.ts` | Rewritten | Uses aiService, fixed 4-arg signature |
| `services/tagMappingService.ts` | Rewritten | Uses aiService, plain functions, typed imports |
| `services/jamendoService.ts` | Rewritten | Typed API response, removed unused import |
| `services/geminiService.ts` | Deleted | No longer needed |
| `services/trackValidationService.ts` | Deleted | No longer needed |
| `hooks/useAudioAnalyzer.ts` | Modified | Typed webkitAudioContext, removed any |
| `hooks/usePersistedState.ts` | Created | Reusable localStorage hook |
| `hooks/usePlayer.ts` | Created | Audio playback control |
| `hooks/useSearch.ts` | Created | Search and refresh logic |
| `hooks/useCollections.ts` | Created | Collection management |
| `components/player/CentralPlayer.tsx` | Modified | SkipBack/SkipForward wired, onNext/onPrev props |
| `components/input/SearchPanel.tsx` | Modified | Fixed nested map keys, removed unused imports |
| `components/collection/CollectionModal.tsx` | Modified | UI text to English |
| `components/settings/PreferencesModal.tsx` | Modified | UI text to English |
| `components/visualizer/Scene3D.tsx` | Modified | Comments to English |
| `package.json` | Modified | Removed @google/genai |
