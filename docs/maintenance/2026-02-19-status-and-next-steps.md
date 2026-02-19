# BGM Hunter Pro Maintenance Status and Next Steps (2026-02-19)

## TL;DR
- The project has completed a major refactor, visual upgrade, and a critical round of **mobile adaptation fixes**.
- **All future changes MUST treat mobile-first adaptation as a prerequisite** — any new feature, visual effect, or layout change should be validated on portrait viewports (360–412px width) before merging.
- The next three tracks are: recommendation/search algorithm upgrade, continued mobile robustness, and user authentication + per-user data.

## 1) What Has Been Done So Far

### 1.1 Core Product and Search Flow
- Migrated AI analysis from Gemini to DeepSeek service abstraction.
- Implemented mixed input logic (script, keywords, script+keywords) with OR-style behavior.
- Added tag mapping pipeline and preference-aware search.
- Switched recommendation baseline toward popularity-related sorting where available.

### 1.2 Playback and UX
- Added progress bar, seek, download button (with availability constraints), and standalone Shuffle.
- Upgraded player to carousel interaction (desktop drag + mobile swipe behavior).
- Added copy/share actions and improved active-card behavior.
- Added collection/favorites workflow and persistence.

### 1.3 Architecture Refactor
- Reduced `App.tsx` complexity by moving logic into hooks:
  - `useSearch`
  - `usePlayer`
  - `useCollections`
  - `usePersistedState`
- Added service layer split for:
  - AI calls (`aiService`)
  - DeepSeek analysis
  - tag mapping
  - Jamendo search

### 1.4 3D Visual System
- Added multiple visualizer themes and significant shader iteration.
- Built specialized scenes (`RainGlass`, `Aurora`, `MilkyWayBackdrop`) and modularized scene logic.
- Tuned beat reactivity, color behavior, and performance constraints.
- Themes reduced to three: **Milky Way** (`halo`), **Rain Glass** (`rainGlass`), **Aurora** (`aurora`).

### 1.5 Mobile Adaptation Fixes (latest round)

> **Root cause discovery**: All three shader backgrounds (`RainGlassScene`, `AuroraScene`, `MilkyWayBackdrop`) shared two systemic bugs that caused mobile distortion — DPR resolution mismatch, and camera-dependent UV mapping.

1. **DPR (Device Pixel Ratio) mismatch fix** — All three shader scenes were setting `uResolution` to `window.innerWidth / innerHeight` (CSS pixels), while `gl_FragCoord` uses actual framebuffer pixels (CSS × DPR). On Windows with display scaling (125%/150%) or mobile with DPR ≥ 2, this caused coordinate misalignment.
   - **Fix**: Changed all scenes to use `state.gl.domElement.width / height` (the real framebuffer size).
   - **Affected files**: `RainGlassScene.tsx`, `AuroraScene.tsx`, `MilkyWayBackdrop.tsx`.

2. **MilkyWay clip-space rewrite** — The galaxy was rendered on a 30×18 3D plane at z=-7.8 via the perspective camera. On portrait mobile, the narrow horizontal FOV made only ~30% of the plane visible, causing severe UV distortion and visual "zooming."
   - **Fix**: Rewrote to use a 2×2 clip-space full-screen quad (`gl_Position = vec4(position.xy, 0, 1)`) with `gl_FragCoord`-based UV normalised by `min(uResolution.x, uResolution.y)`. This bypasses the 3D camera entirely and always fills the viewport proportionally.
   - **Affected file**: `MilkyWayBackdrop.tsx`.

3. **Waveform bar scaling** — Frequency visualization bars in `CentralPlayer` appeared stuck at maximum amplitude on mobile because the bar height formula (`v / 3`, max ~85px) exceeded the container height (`h-10` = 40px), clipping every bar to the same height.
   - **Fix**: Dynamic divisor by viewport width — mobile ÷8, tablet ÷5, desktop ÷3 — keeping max bar height within the container.
   - **Affected file**: `CentralPlayer.tsx`.

4. **RainGlass brightness enhancement** — Added `uBrightness` uniform and `SCREEN_BRIGHTNESS = 1.2` knob; lowered `BEAT_THRESHOLD` from 0.38 to 0.3 for more responsive audio reactivity.
   - **Affected file**: `RainGlassScene.tsx`.

## 2) Current Gaps / Risks

### 2.1 Recommendation Quality
- Search result pool is still narrow in many cases (high similarity, repeated tracks).
- Keyword expansion and multi-query retrieval are not yet systematic enough.
- Shuffle diversity is not always strong enough over consecutive batches.

### 2.2 Cross-Platform Stability
- ~~Visual behavior and layout reliability at smaller resolutions are not fully verified.~~ **(Partially resolved)** — DPR mismatch and MilkyWay distortion fixed; further QA on real mobile devices recommended.
- ~~Some theme switching behavior at constrained viewport sizes can cause visual offsets.~~ **(Resolved)** — MilkyWay now uses fixed clip-space rendering; no camera-dependent drift.
- SearchPanel tag layout and CentralPlayer card sizing have been reduced for mobile but need testing on 360px-width devices.

### 2.3 Data and Account Layer
- Current persistence is mainly local storage, not full per-user cloud persistence.
- No formal auth, role management, user quotas, or admin panel yet.

## 3) Agreed Strategic Directions

> **Guiding principle**: All changes — features, visuals, or architecture — **must be validated for mobile-first adaptation** before they are considered complete.

1. **Recommendation/Search Upgrade**  
   Make retrieval broader and ranking smarter (multi-query, popularity, diversity, preference fusion).
2. **Mobile Adaptation and Robustness** *(ongoing)*  
   Continue responsive hardening and fix remaining layout/visual issues at all target viewports.
3. **User Authentication and Management**  
   Enable invite/code-based login, per-user data isolation, and basic admin visibility.

## 4) Recommended Execution Order (Easy to Hard)

1. **Phase A (fast wins, low risk): recommendation retrieval expansion**
   - Introduce 2-3 query variants per request.
   - Merge and deduplicate top tracks.
   - Add diversity re-ranking and stronger batch refresh logic.
2. **Phase B: mobile/responsive hardening** *(partially done, continues)*
   - ✅ Fixed DPR resolution across all shaders.
   - ✅ Rewrote MilkyWay to clip-space rendering.
   - ✅ Fixed waveform scaling.
   - ⬜ Real-device QA on iOS Safari and Android Chrome.
   - ⬜ SearchPanel and landing page compact mobile layout polish.
   - ⬜ Performance profiling on low-end mobile GPUs.
3. **Phase C: authentication + user data**
   - Add login and invite-code gate.
   - Move preferences/favorites to per-user backend storage.
   - Add minimal admin user visibility.

## 5) Definition of Success (Next Milestone)
- Recommendation list shows significantly lower repetition across consecutive searches.
- Shuffle produces visibly different and still relevant sets.
- Mobile (common resolutions) has no visual overflow/offset regressions in major scenes.
- Users can log in and retrieve their own preferences and favorites from server-side storage.

## 6) Linked Docs
- Architecture and implementation plan: `docs/maintenance/architecture-and-delivery-plan.md`
- Search/recommendation deep plan: `docs/maintenance/recommendation-engine-v2-plan.md`
- Project briefing for AI assistants: `claude_web_ui.md`


