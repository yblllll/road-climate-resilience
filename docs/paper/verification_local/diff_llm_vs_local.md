# Verification Diff — LLM vs Local PyMuPDF

Total entries: 63

## Agreement distribution

| Bucket | Count |
|---|---|
| AGREE_PARTIAL_QUOTE_VERIFIED | 15 |
| LLM_PARTIAL_WITHOUT_QUOTE | 12 |
| AGREE_MATCH | 12 |
| MATCH_WITHOUT_QUOTE | 9 |
| AGREE_PARTIAL | 4 |
| AGREE_NOT_FOUND | 3 |
| LLM_NOT_FOUND_LOCAL_MATCH | 2 |
| AGREE_MATCH_FUZZY | 2 |
| LLM_MATCH_LOCAL_NOT_FOUND | 1 |
| LLM_PARTIAL_LOCAL_NOT_FOUND | 1 |
| AGREE_PARTIAL_PAGE_OFF | 1 |
| LLM_FLAG_QUOTE_REAL | 1 |

## Disagreements (LLM said MATCH, local says NOT_FOUND)

- **huang2022overview** (line 70) — LLM reasoning: _Huang 2022 reviews agent-based models in transport, covering their ability to simulate counterfactual scenarios under different conditions — directly _

## Disagreements (LLM said NOT_FOUND, local found it)

- **dft2024rea** (line 66) — local found on p.10: _twork (srn) and the local road network. the srn comprises more than 4,300 miles of motorways and major a-class roads and is used by around 4 million v_
- **sias2025roadways** (line 66) — local found on p.13: _- ated costs will continue to increase. distances travelled by vehicles are likely to increase nationally and globally, with global tonne-kilometres o_