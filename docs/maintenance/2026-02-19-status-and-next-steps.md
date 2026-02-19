# BGM Hunter Pro Maintenance Status and Next Steps (2026-02-19)

## TL;DR
- The project has completed a major refactor and visual upgrade, but recommendation quality and result diversity are now the top bottlenecks.
- The next three tracks are: recommendation/search algorithm upgrade, mobile robustness, and user authentication + per-user data.

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
- Built specialized scenes (`RainGlass`, `Aurora`) and modularized parts of scene logic.
- Tuned beat reactivity, color behavior, and performance constraints.

## 2) Current Gaps / Risks

### 2.1 Recommendation Quality
- Search result pool is still narrow in many cases (high similarity, repeated tracks).
- Keyword expansion and multi-query retrieval are not yet systematic enough.
- Shuffle diversity is not always strong enough over consecutive batches.

### 2.2 Cross-Platform Stability
- Visual behavior and layout reliability at smaller resolutions are not fully verified.
- Some theme switching behavior at constrained viewport sizes can cause visual offsets.

### 2.3 Data and Account Layer
- Current persistence is mainly local storage, not full per-user cloud persistence.
- No formal auth, role management, user quotas, or admin panel yet.

## 3) Agreed Strategic Directions

1. **Recommendation/Search Upgrade**  
   Make retrieval broader and ranking smarter (multi-query, popularity, diversity, preference fusion).
2. **Mobile Adaptation and Robustness**  
   Add responsive QA baseline and fix visual module behavior at different viewport sizes.
3. **User Authentication and Management**  
   Enable invite/code-based login, per-user data isolation, and basic admin visibility.

## 4) Recommended Execution Order (Easy to Hard)

1. **Phase A (fast wins, low risk): recommendation retrieval expansion**
   - Introduce 2-3 query variants per request.
   - Merge and deduplicate top tracks.
   - Add diversity re-ranking and stronger batch refresh logic.
2. **Phase B: mobile/responsive hardening**
   - Add explicit viewport QA matrix and scene fallback rules.
   - Fix theme-specific small-screen rendering issues.
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


