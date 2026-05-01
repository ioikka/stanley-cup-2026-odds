# Graph Report - .  (2026-05-01)

## Corpus Check
- Corpus is ~8,121 words - fits in a single context window. You may not need a graph.

## Summary
- 57 nodes · 115 edges · 7 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Static Webhook Server|Static Webhook Server]]
- [[_COMMUNITY_Odds Parsing Pipeline|Odds Parsing Pipeline]]
- [[_COMMUNITY_Contender Teams|Contender Teams]]
- [[_COMMUNITY_Favorite Teams|Favorite Teams]]
- [[_COMMUNITY_Strong Contenders|Strong Contenders]]
- [[_COMMUNITY_Playoff Teams|Playoff Teams]]
- [[_COMMUNITY_Longshot Teams|Longshot Teams]]

## God Nodes (most connected - your core abstractions)
1. `2026 Stanley Cup Championship Odds` - 32 edges
2. `Stanley Cup 2026` - 15 edges
3. `main()` - 7 edges
4. `WebhookHandler` - 7 edges
5. `Contenders Tier` - 7 edges
6. `Longshots Tier` - 6 edges
7. `Vegas Golden Knights` - 6 edges
8. `parse_espn_futures()` - 5 edges
9. `Colorado Avalanche` - 5 edges
10. `Tampa Bay Lightning` - 5 edges

## Surprising Connections (you probably didn't know these)
- `2026 Stanley Cup Championship Odds` --references--> `Anaheim Ducks Logo`  [EXTRACTED]
  stanley-cup-odds.html → logos/ANA_light.svg
- `2026 Stanley Cup Championship Odds` --references--> `Boston Bruins Logo`  [EXTRACTED]
  stanley-cup-odds.html → logos/BOS_light.svg
- `2026 Stanley Cup Championship Odds` --references--> `Buffalo Sabres Logo`  [EXTRACTED]
  stanley-cup-odds.html → logos/BUF_light.svg
- `2026 Stanley Cup Championship Odds` --references--> `Colorado Avalanche Logo`  [EXTRACTED]
  stanley-cup-odds.html → logos/COL_light.svg
- `2026 Stanley Cup Championship Odds` --references--> `Dallas Stars Logo`  [EXTRACTED]
  stanley-cup-odds.html → logos/DAL_light.svg

## Hyperedges (group relationships)
- **2026 Stanley Cup Playoff Contenders** — COL_ColoradoAvalanche, CAR_CarolinaHurricanes, TBL_TampaBayLightning, VGK_VegasGoldenKnights, BUF_BuffaloSabres, DAL_DallasStars, MIN_MinnesotaWild, MTL_MontrealCanadiens, ANA_AnaheimDucks, PHI_PhiladelphiaFlyers, UTA_UtahMammoth, EDM_EdmontonOilers, PIT_PittsburghPenguins, BOS_BostonBruins [EXTRACTED 1.00]
- **Stanley Cup Favorites** — COL_ColoradoAvalanche, CAR_CarolinaHurricanes, TBL_TampaBayLightning [EXTRACTED 1.00]
- **Stanley Cup Contenders** — VGK_VegasGoldenKnights, BUF_BuffaloSabres, DAL_DallasStars, MIN_MinnesotaWild, MTL_MontrealCanadiens, ANA_AnaheimDucks [EXTRACTED 1.00]
- **Stanley Cup Longshots** — PHI_PhiladelphiaFlyers, UTA_UtahMammoth, EDM_EdmontonOilers, PIT_PittsburghPenguins, BOS_BostonBruins [EXTRACTED 1.00]
- **First Round R1 Matchups** — TBL_TampaBayLightning, MTL_MontrealCanadiens, VGK_VegasGoldenKnights, UTA_UtahMammoth, BUF_BuffaloSabres, BOS_BostonBruins, DAL_DallasStars, MIN_MinnesotaWild, ANA_AnaheimDucks, EDM_EdmontonOilers, PHI_PhiladelphiaFlyers, PIT_PittsburghPenguins [EXTRACTED 1.00]
- **Round 2 (Advanced Past R1)** — COL_ColoradoAvalanche, CAR_CarolinaHurricanes [EXTRACTED 1.00]
- **NHL Team Logo Assets** — ANA_logo, BOS_logo, BUF_logo, CAR_logo, COL_logo, DAL_logo, EDM_logo, MIN_logo, MTL_logo, PHI_logo, PIT_logo, TBL_logo, UTA_logo, VGK_logo [EXTRACTED 1.00]

## Communities

### Community 0 - "Static Webhook Server"
Cohesion: 0.21
Nodes (5): get_status(), Send JSON response with CORS headers., Get server and data status., Handle POST /webhook/refresh - runs parse-odds.py, WebhookHandler

### Community 1 - "Odds Parsing Pipeline"
Cohesion: 0.33
Nodes (10): assign_tier(), calc_probability(), download_logos(), enhance_status(), fetch_url(), load_cached_json(), main(), parse_espn_futures() (+2 more)

### Community 2 - "Contender Teams"
Cohesion: 0.25
Nodes (9): Anaheim Ducks, Anaheim Ducks Logo, Buffalo Sabres, Buffalo Sabres Logo, Dallas Stars, Dallas Stars Logo, Minnesota Wild, Minnesota Wild Logo (+1 more)

### Community 3 - "Favorite Teams"
Cohesion: 0.46
Nodes (8): Carolina Hurricanes, Carolina Hurricanes Logo, Montreal Canadiens, Montreal Canadiens Logo, Tampa Bay Lightning, Tampa Bay Lightning Logo, Favorites Tier, 2026 Stanley Cup Championship Odds

### Community 4 - "Strong Contenders"
Cohesion: 0.33
Nodes (6): Colorado Avalanche, Colorado Avalanche Logo, Utah Mammoth, Utah Mammoth Logo, Vegas Golden Knights, Vegas Golden Knights Logo

### Community 5 - "Playoff Teams"
Cohesion: 0.5
Nodes (5): Philadelphia Flyers, Philadelphia Flyers Logo, Pittsburgh Penguins, Pittsburgh Penguins Logo, Stanley Cup 2026

### Community 6 - "Longshot Teams"
Cohesion: 0.4
Nodes (5): Boston Bruins, Boston Bruins Logo, Edmonton Oilers, Edmonton Oilers Logo, Longshots Tier

## Knowledge Gaps
- **4 isolated node(s):** `Extract Stanley Cup futures odds from ESPN embedded JSON.`, `Handle POST /webhook/refresh - runs parse-odds.py`, `Send JSON response with CORS headers.`, `Get server and data status.`
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `2026 Stanley Cup Championship Odds` connect `Favorite Teams` to `Contender Teams`, `Strong Contenders`, `Playoff Teams`, `Longshot Teams`?**
  _High betweenness centrality (0.242) - this node is a cross-community bridge._
- **Why does `Stanley Cup 2026` connect `Playoff Teams` to `Contender Teams`, `Favorite Teams`, `Strong Contenders`, `Longshot Teams`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **What connects `Extract Stanley Cup futures odds from ESPN embedded JSON.`, `Handle POST /webhook/refresh - runs parse-odds.py`, `Send JSON response with CORS headers.` to the rest of the system?**
  _4 weakly-connected nodes found - possible documentation gaps or missing edges._