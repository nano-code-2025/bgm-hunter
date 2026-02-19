# Recommendation Engine V2 Plan
# 这里需要先调研一下网易云音乐spotify，还有youtube music，他们的这个搜索和推荐系统是什么样的架构，有没有开源的代码或者逻辑可以进行参考的。
## TL;DR
- The current bottleneck is not UI, but retrieval breadth + ranking logic.
- V2 should combine multi-query retrieval, popularity-aware ranking, diversity control, and user preference fusion.

## 1) Target
Build a recommendation pipeline that is:
1. more diverse,
2. still relevant to script/keywords,
3. aligned with popularity/trend signals,
4. personalized by user behavior and explicit preferences.

## 2) Proposed Pipeline (per request)

1. **Intent extraction**
   - Inputs: `script`, `selectedKeywords`, `userPreferences`, `recentFavorites`.
   - Output: rich tag set (genre, mood, instrument, scenario, era/tempo hints).

2. **Multi-query generation (2-3 variants minimum)**
   - Query A: high-confidence core tags (precision).
   - Query B: expanded synonyms/neighbor tags (recall).
   - Query C: exploratory tags based on mood and preference embedding (novelty).

3. **Parallel retrieval**
   - Run all query variants against provider(s) in parallel.
   - For each provider, fetch top N (suggest 40-50 total merged candidate pool).

4. **Candidate normalization**
   - Deduplicate by stable track signature (`provider + trackId` + title/artist fallback).
   - Remove unavailable entries (non-playable, blocked URLs, optional non-downloadable based on mode).

5. **Scoring and reranking**
   - Score = relevance + popularity + novelty + preference fit + quality checks.
   - Add penalties for duplicates/near-duplicates and recently shown tracks.

6. **Final selection**
   - Return top K with diversity constraints (artist/tag spread).
   - Persist shown IDs for stronger future batch refresh.

## 3) Shuffle V2 Behavior

Current pain: shuffle can still look similar.

V2 method:
1. regenerate query variants with new exploratory seed;
2. apply stronger exclusion window (recently shown/recently played);
3. enforce minimum novelty ratio in final list (e.g., at least 60% not in previous batch);
4. fallback to broader tag expansion if novelty target fails.

## 4) Preference Fusion Strategy

Combine three preference channels:
1. explicit preferences (user-selected genres/instruments/themes),
2. implicit preferences (favorites/collections history),
3. session context (current query + recent interactions).

Recommended weighting baseline:
- relevance to current intent: 0.45
- popularity/trend: 0.20
- explicit preference fit: 0.15
- implicit preference fit: 0.15
- novelty bonus: 0.05

Adjust by mode:
- pure keyword mode: higher relevance weight.
- script mode: higher exploratory and mood weights.

## 5) Multi-Provider Validation Track

Goal: evaluate adding YouTube/Spotify-like sources before full production merge.

Steps:
1. Build provider adapter interface (unified output schema).
2. Implement sandbox connectors behind feature flags.
3. Run offline comparison:
   - coverage
   - playability
   - metadata quality
   - popularity signal quality
4. Decide merge policy: single-provider fallback vs blended ranking.

## 6) Engineering Tasks

1. Add query variant generator module.
2. Add candidate merge/dedup utility.
3. Add scoring/ranking module with configurable weights.
4. Add novelty/exclusion memory store.
5. Add provider adapter abstraction and test harness.
6. Add telemetry for recommendation quality.

## 7) KPIs (must track)

1. repetition rate across consecutive batches
2. unique artist ratio in top K
3. play success rate
4. favorite/save conversion rate
5. skip rate in first 10 seconds

## 8) Immediate Sprint Scope (first cut)

1. implement 3-query retrieval and merge top 50 candidates;
2. apply dedup + popularity-aware rerank + novelty filter;
3. update shuffle to forced requery with exclusion window;
4. add logs/metrics for result diversity and playability.


