# research/

| 파일 | 무엇 | 누가 쓰나 |
|---|---|---|
| `sources.json` | 출처 · 주장 · 미조사 목록. 형식은 `schemas/source.schema.json` · `claim.schema.json` | 조사(사람 또는 에이전트). `catalogue.validate()` 를 통과해야 한다 |
| `gentle_monster/evidence.md` · `brands/` · `magazines/` · `comparative_analysis/matrix.md` | 원장에서 만든 표 | `python3 -m gentle_monster research` — 손으로 고치지 말 것 |
| `drift/se_new_drift.json` · `drift/SE_NEW_DRIFT.md` | SE_NEW Drift 원문 기록(커밋 · 인용 15개)과 해석의 구분 | 손으로. 인용은 QA 가 se_new 체크아웃에서 다시 찾는다 |
| `drift/drift_studio_disambiguation.md` | 네덜란드 스튜디오 DRIFT — SE_NEW Drift 와 **무관함**을 적어 두는 자리 | 원장에서 생성 |

**2026-10-09 기준 모든 주장은 `read: snippet` 이다.** 브랜드 · 매거진 사이트에 직접 접속이 막혀(프록시 403, DNS 실패)
검색 결과 조각으로만 모았다. 조각에는 `high` 신뢰도를 붙이지 않는다 — 19개를 `medium` 으로 내린 이유가 `confidence_note` 에 있다.
