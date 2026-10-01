# gentle_monster frontend engine

방(job)을 웹 페이지로 만든다. **스크롤이 곧 동선이다.** 페이지는 짓고 끝나는 것이 아니라 브라우저에서
**잰 뒤에** 받아들여진다. 무엇을 바꿀지는 se_new 의 개선 정책(`policy.py` · `개선결정`)을 디자인에
옮겨 결정한다.

```
job.json ─▶ genome ─▶ tokens ─▶ compose ─▶ index.html ─▶ judge (Chromium) ─▶ V · J
              ▲                                                            │
              └──── operator (π 가 고름) ◀── ACCEPT / REJECT ◀── policy ◀───┘
                                              └─▶ ledger.jsonl (거절도 적는다)
```

```bash
python3 -m gentle_monster site <작업> [--rounds 6]     # 있는 작업을 웹 페이지로
python3 -m gentle_monster example gm --site            # 예제 + 웹 페이지
!젠몬 방금 거 웹 사이트로                                # 디스코드
```

결과물은 `out/<작업>/site/` 에 쌓인다: `index.html`(잰 그 페이지 그대로) · `tokens.json`(W3C DTCG 형식) ·
`report.json`(V · J · 사실 · π) · `ledger.jsonl`(모든 결정). 전역 π 원장은 `out/_engine/policy.jsonl`.

## 1. 젠틀몬스터의 철학 → 프론트엔드 도구가 지녀야 할 것

| 철학 | 엔진이 지녀야 할 것 | 어디서 |
|---|---|---|
| 공간이 곧 이야기다 | 내용은 job 에서만 온다. 후보는 **어떻게 말하는가**만 바꾸고 **무엇을 말하는가**는 못 바꾼다 | `compose` · judge `content` 해시 |
| 문턱 · 동선 | 스크롤 = 걷기. 문설주가 갈라지고(스크롤 구동), 평면 위 동선이 스크롤에 맞춰 그려진다 | `compose` threshold · walk |
| 빈 공간 한가운데 하나의 주인공 | 크기의 극적 대비 · 여백 — **잰다** | judge `drama` · `air` |
| 극단까지 민 재료 | 재료 프리셋에서 그린 절차적 표면(사진인 척하지 않는다) | `tokens.matter` · `_TEX_JS` |
| 하나의 뜨거운 강조색 | 강조색 픽셀 0.3–4 % | judge `accent` |
| 숨 쉬는 키네틱 오브제 | 움직임은 유전자다. reduced-motion 에서는 **절대** 안 움직인다 | `tokens.motion` · judge V |
| 장식이 아니라 실험 | genome + 연산자 + 잰 수용 | `policy` |

취향과 무관하게 프론트엔드 도구라면 지녀야 할 것: 디자인 토큰(DTCG 내보내기) · 유동 타이포(375–1440 px) ·
그리드 · 대비(WCAG) · 폰 폭 · 접근 가능한 이름 · 제목 순서 · 오프라인(외부 요청 0) · 페이지 무게.

## 2. 유전자 (genome)

| 유전자 | 값 | 무엇을 바꾸나 |
|---|---|---|
| `ratio` | 1.2 … 1.618 | 모듈러 타입 스케일 |
| `air` | 0.8 … 1.8 | 8 px 단위 × air = 여백 |
| `cols` | 6 · 8 · 12 | 데스크톱 그리드 |
| `tension` | 0 · 1 · 2 | 읽기 단이 축에서 벗어난 정도 |
| `mast` | stencil · solid · outline · split | 마스트헤드 처리 |
| `voice` | grotesk · serif | 본문 글꼴 |
| `motion` | still · breath · drift | 움직임 |
| `order` | walk-first · matter-first · intent-first | 섹션 순서 |

첫 genome 은 job 에서 읽는다(`room.light` = dark_gallery → 어두운 페이지, stencil 마스트헤드).
연산자 12개가 한 유전자를 한 칸씩 옮긴다. 끝을 넘는 걸음은 감싸지 않고 no-op 이다.

## 3. 심판 — 코드다, 모델이 아니다

**V (불변조건)**: 하나라도 안 서면 받아들이지 않는다. 모르는 것은 통과가 아니다.
overflow-375/1440 · contrast-rendered · contrast-tokens · min-font-375 · offline · js-errors · names ·
headings · reduced-motion · weight. 대비는 **두 길로** 잰다. 토큰 쌍을 계산으로 한 번, 렌더된 페이지의
computed style 을 배경까지 합성해 한 번. 두 값은 일치한다(gm: 4.51 = 4.51).

**J (품질, 0..1, 0.01 단위)**: drama · hierarchy · measure · air · accent · rhythm. 취향은 숨기지 않고
`judge.py` 첫머리에 적었다.

## 4. 정책 — se_new `개선결정` 을 디자인에

```
ACCEPT  ⟺  같은 내용  ∧  V(후보)  ∧  어떤 J 성분도 안 떨어짐  ∧  J(후보) > J(바탕) + ε
```

- **불변조건이 목적함수보다 먼저다.** 내용이 다르거나 V 가 안 서면 ΔJ 를 아예 계산하지 않는다.
- **퇴행은 조건이지 항이 아니다.** 평균이 올라도 성분 하나가 떨어지면 REJECT.
- **같으면 안 바꾼다.** 동점 · 같은 HTML → REJECT. **기본은 REJECT.**
- **거절도 적는다.** 그 바탕에서 거절된 연산자는 다시 고르지 않는다(바탕이 바뀌면 풀린다).
- **π** = 연산자별 (수용+1)/(시도+2) ÷ 평균, [0.25, 4] 로 자른다. 어떤 연산자도 버려지지 않고(다시 증명할
  기회가 사라지므로) 독차지하지도 않는다. π0 는 균등하다. 똑똑한 π 보다 공정한 π 가 먼저다.

## 5. 만들면서 잡은 것 — 사소한 설명부터 죽였다

| 실측 | 무엇이었나 | 고친 것 |
|---|---|---|
| 첫 실행이 `scale-down` 을 ACCEPT (ΔJ +0.0005, air 0.737→0.740) | 같은 페이지에서 **스크린샷 축소만** 바꿔도 air 가 0.733→0.795 로 움직였다. 0.003 은 이 심판이 못 가르는 차이였다 | 원해상도로 재고 J 를 0.01 단위로 비교. 그 아래는 동점이고 동점은 REJECT |
| `drama` 가 네 예제 모두 1.0 | "본문" 을 가장 많은 글자의 크기로 잡았더니 13 px 캡션이 본문이 됐다 | 본문 = `<p>` 글자가 가장 많은 크기. drama 는 6–14 배 띠 |
| `measure` 감점 | 콜로폰 한 줄이 약 120자였다 | 진짜 결함이었다. `max-width: 34em` |
| 900 px 줄을 폰에서 통과시켰다 | `body{overflow-x:clip}` 이 넘침을 잘라 `scrollWidth` 가 못 봤다. 글은 잘려 있었다 | 글 상자마다 뷰포트 밖인지 잰다. body clip 은 뺐다 |

검사는 RED 로 증명했다(`tests/test_engine.py`): 대비·넘침·외부 요청·움직임·이름·제목·JS 오류를 하나씩 깨뜨린
페이지가 **정확히 그 검사 하나만** 실패한다. 엔진 페이지 48 변형(4 방 × 3 움직임 × 4 마스트헤드)은 V 를 전부 지킨다.

## 6. 이 심판이 **못** 잡는 것

- 이미지·캔버스 **위에 겹친** 글의 대비. 조상의 배경만 합성하기 때문이다. 그래서 compose 는 글을 그림 위에 두지
  않는다. 이 규칙은 compose 가 지키는 것이지 심판이 보는 것이 아니다.
- stencil 마스트헤드의 줄무늬가 글자를 얼마나 가리는지(가상 요소는 재지 않는다).
- 움직임의 질. J 는 reduced-motion 상태에서 잰다. `motion` 연산자는 J 를 거의 못 움직이고, 그래서 대개 동점 REJECT 다.
- J 의 상당 부분이 이미 포화다(hierarchy · accent · rhythm 이 대개 1.0). 지금 루프가 실제로 움직이는 축은 주로
  air 와 drama 다.
- air 의 목표 0.6 은 **선언한 취향**이다. 지금 페이지는 이보다 여백이 많아서 루프는 페이지를 조이는 쪽으로 간다.
  "빈 공간" 을 더 원하면 목표를 올려야 한다. 그것은 사실이 아니라 선택이다.

## 7. 선행 도구 — 빌린 것과 다른 것

기억에서 적은 것이다. 이 세션에서 원문을 다시 읽지 않았다 **[출처:기억]**.

- 디자인 토큰: W3C Design Tokens Community Group 형식(`$type`/`$value`)으로 내보낸다. Style Dictionary 류
  변환기와 같은 자리에 들어갈 수 있다.
- 유동 타입: Utopia 식 `clamp(min, a + b·vw, max)` 를 375–1440 px 사이에 쓴다.
- 접근성 검사: axe-core · Lighthouse 가 하는 일 중 대비 · 이름 · 제목 · 언어만 직접 잰다. 그 도구들을 대체하지 않는다.
- 스크롤 구동 애니메이션: CSS `animation-timeline: view()/scroll()`. `@supports` 와 reduced-motion 안에만 둔다.

다른 점: 생성자와 심판을 분리하고, 심판이 **렌더된 페이지를 재서** 개선을 받아들일지 정한다. 결정은 원장에 쌓이고
그 원장이 다음에 무엇을 시도할지를 바꾼다. 비슷한 "측정 기반 디자인 진화" 도구가 있는지는 **아직 조사하지 않았다.**
