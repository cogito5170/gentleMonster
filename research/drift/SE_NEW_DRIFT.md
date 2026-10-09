# SE_NEW Drift — 원문 검증과 적용

## 답

**SE_NEW 의 Drift 는 se_new 저장소(github.com/cogito5170/se_new)가 스스로 정의한 창작 방법론이다.**
네덜란드 예술가 듀오 DRIFT(Lonneke Gordijn · Ralph Nauta, driftlab.com)와는 무관하다. 두 개념을 섞지 않는다 —
스튜디오 쪽 조사는 [`drift_studio_disambiguation.md`](drift_studio_disambiguation.md) 에 따로 있다.

## 원문

| 항목 | 값 |
|---|---|
| 파일 | `novel/DRIFT.md` · `novel/shock.py` · `novel/diffusion.py` · `mathdrift/README.md` · `mathdrift/measure.py` · `mathdrift/ops.py` · `.claude/skills/drift/SKILL.md` |
| 커밋 | `79dab33ccaf8a99720991139a503848e4c351f64` (2026-09-30T16:06:00Z) |
| 발행 주체 | se_new 저장소 (cogito5170). 파일에 개인 저자 이름은 없다 |
| 읽은 정도 | 전문 — 로컬 체크아웃에서 읽었다 |
| 인용 15개 | `se_new_drift.json` 의 `quotes`. `qa.research()` 가 se_new 체크아웃이 있으면 **글자 그대로** 다시 찾는다 |

## 원문이 말하는 것

DRIFT = **D**iffusion(확산) · **R**hythm(리듬) · **I**ntrusion(충격) · **F**reewriting(자유) · **T**ruth(원장).
줄거리 없이 첫 문장에서 이어 쓰는 소설 파이프라인이다.

1. **자유도가 전부다.** "그것들은 전부 출발점이지 각본이 아니다." 꺾이지 않는 것은 둘 — 앞의 것과의 **모순**, 우연이 문제를 푸는 **편의주의**.
2. **수학의 확장 방식.** 앞의 것을 품은 채로 바깥을 넓힌다(보존적 확장). 공리계 = 원장, 무모순성 = 모순 게이트,
   새 공리 = 사건, 미증명 명제 = 열린 것, 분야 사이의 다리 = 연결(접기), 증명의 흐름 = 표류.
3. **확산** = 새것 + 앞엣것을 한 단계 키워 다시 만지기. **식은 소품**(최근엔 없지만 너무 오래되지 않은 것)이 연료다.
4. **충격** = 약 2,000자마다 제3자가 점층을 끊는다. 축(누가 × 어떻게 × 무엇이 남나 × …)을 조합해 뽑고, 씨앗에 묶여 재현된다.
   "사건은 문제를 풀지 않는다."
5. **게이트는 최소.** 자는 재서 숫자를 돌려주되 원고를 죽이지 않는다 — "과잉 기각은 글 자체를 없앤다."
6. **mathdrift** 가 같은 규칙을 탐색공간에 옮긴다: 한 번에 연산자 하나, 부모는 원장에 있어야 한다, 먼 도약은 드물게
   (`JUMP_SHARE = 0.2`), 한 낱말 겹친 것은 물려받은 것이 아니다(`KEEP_MIN = 2`).

## 이 프로젝트가 옮긴 것 (`gentle_monster/magazine/drift.py`)

| 원문 | 매거진 Drift |
|---|---|
| 원장 · 계보 (mathdrift `space.add()`) | `Ledger.add()` 가 원장에 없는 부모를 `LineageError` 로 거절 |
| 한 번에 연산자 하나 · 고정 목록 | detach · refine · associate · invert · revive · fold · leap (뒤의 둘이 먼 걸음, 20%) |
| 확산 두 계수 · 분모는 부모 · KEEP_MIN 2 | `measure()` — new / kept / share, 관찰로만 기록 |
| 식은 소품 · FUEL_AGE 8 | `revive` — 최근 안 쓰였고 너무 오래되지 않은 노드를 다시 부른다 |
| 충격 · 축 조합 · 씨앗 재현 · 문제를 안 푼다 | 4걸음마다 WHO × HOW × MARK, 결과는 "답하지 않는 물음" 이 남는 끼어드는 지면 |
| 하드 게이트 둘 | 계보 + **브랜드에 관한 허구를 사실처럼 쓰지 않기**(`guard_text`) |

## 원문에 없는 것 — 이 프로젝트의 해석

- '모순' 을 "허구를 브랜드 사실로 쓰는 것" 으로 옮긴 것은 이 프로젝트의 읽기다. DRIFT.md 의 문장이 아니다.
- 바깥 분야(발굴 · 보존 · 검안 · 경매 · 지질조사 …)와 그 편집 장치는 이 프로젝트의 어휘다. DRIFT 는 산문용 사건 축을 뽑지 분야를 뽑지 않는다.
- DRIFT 는 산문을 모델(Gemini)로 쓴다. 매거진 Drift 는 **모델로 글을 쓰지 않는다** — 원장에서 조립한다. 이것은 한계다.
- 브리프의 "Research broadly. Extract principles. Let ideas drift across disciplines. Transform the relationships.
  Produce something original." 은 **프로젝트 운영 원칙**이지 SE_NEW 인용문이 아니다.
