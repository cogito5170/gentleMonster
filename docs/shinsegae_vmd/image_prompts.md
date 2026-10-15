# 신세계 VMD 포트폴리오 — 장면별 이미지 (미드저니 프롬프트)

[storyline.md](storyline.md) 의 페이지 지도 순서대로 ①–⑧. 미드저니는 영어 프롬프트를 가장 잘 따르므로 영어로 쓰고, 뜻을 우리말로 붙였다.

## 공통 규칙

- **비율 A4 가로**: `--ar 297:210`. 세로 판형이면 `--ar 210:297`.
- **글자 · 로고 금지**: 모든 프롬프트 끝에 `--no text, letters, logo, signage, watermark`. 제목 · 이름은 인디자인 · 피그마에서 얹는다. 신세계 이름이나 로고를 프롬프트에 넣지 않는다 — 가짜 로고가 나온다.
- **연작으로 보이게**:
  1. ① 표지를 먼저 만든다.
  2. 고른 표지 이미지의 주소를 ②–⑧ 에 `--sref <표지 URL>` 로 붙인다. 색 · 빛 · 질감이 한 권처럼 맞는다.
  3. ③–⑥ 네 계절 창은 **같은 틀 문장**(아래 `WINDOW FRAME`)을 그대로 쓰고 안의 내용만 바꾼다. 같은 창이 1년을 사는 것처럼 보인다.
- **Raw 모드**를 켜면 사진처럼 담백해진다(버전에 따라 `--style raw` 또는 `--raw`, 웹 설정에서 켜는 편이 안전).
- **표기**: 판권 자리에 *"Concept images generated with Midjourney. Concept, prompts and art direction by Jeong Hyeokju. This is a personal proposal, not affiliated with Shinsegae."*

공통 꼬리말(모든 프롬프트 뒤에 이미 붙여 둠):

```
editorial architectural photography, Fujifilm medium format, soft grain, quiet and precise, muted palette --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

`WINDOW FRAME` (③–⑥ 공통):

```
front elevation of a single tall arched display window set into a granite neo-classical department store facade, centered and symmetrical, eye level, blue hour, the window glowing from inside
```

---

## ① 표지 — 계절이 어긋난 창

바깥은 가을 해 질 녘인데, 불 켜진 창 안에서는 눈이 내린다. 창 하나가 다른 시간을 품고 있다. "WINDOWS OF TIME"을 한 장으로 말한다.

```
a granite neo-classical department store facade at autumn dusk, warm amber sky and a few fallen leaves on the pavement, one tall arched display window glowing, inside the window it is quietly snowing over a small white landscape, a single bare tree inside, the season inside the glass does not match the season outside, wide symmetrical composition, negative space in the upper third for a title, editorial architectural photography, Fujifilm medium format, soft grain, quiet and precise, muted palette --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

변형: 창 안을 봄으로 — `it is quietly snowing over a small white landscape, a single bare tree inside` → `fresh pale green sprouts are growing from white sand`.

## ② CONCEPT — 재료 무드보드

네 계절의 사물과 재료를 돌판 위에 한 번에 펼친다.

```
top-down flat lay material board on a pale granite slab, arranged in a precise grid: white paper sprouts on fine sand, three small cobalt blue acrylic cylinders in a shallow tray of still water, an oak wood block with a long amber shadow, a brass filament light bulb, one red silk ribbon, small fabric swatches in pale green, cobalt, amber and warm white, soft daylight from one side, editorial architectural photography, Fujifilm medium format, soft grain, quiet and precise, muted palette --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

## ③ CHAPTER 1 · SPROUT (봄)

창 바닥의 흰 모래에서 종이 새싹 수백 개가 돋고, 가장 큰 새싹 하나만 좁은 빛을 받는다. 옆에 연두색 봄옷 한 벌.

```
front elevation of a single tall arched display window set into a granite neo-classical department store facade, centered and symmetrical, eye level, blue hour, the window glowing from inside, inside the window hundreds of small white paper sprouts growing out of a bed of pale sand, one taller sprout under a narrow spotlight, a single pale green spring garment on a minimal brass stand, fresh and calm, editorial architectural photography, Fujifilm medium format, soft grain, quiet and precise, muted palette --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

## ④ CHAPTER 2 · PUDDLE (여름)

창 바닥 전체가 얕은 물(거울)이다. 코발트 블루 원통 셋이 물에 그대로 비친다.

```
front elevation of a single tall arched display window set into a granite neo-classical department store facade, centered and symmetrical, eye level, blue hour, the window glowing from inside, inside the window the floor is a shallow still pool of water like a mirror, three cobalt blue cylindrical objects of different heights standing in the water with perfect reflections, a light summer garment hanging above the water, one narrow spotlight from above, cool and clear, editorial architectural photography, Fujifilm medium format, soft grain, quiet and precise, muted palette --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

## ⑤ CHAPTER 3 · DUSK (가을)

창 뒷벽에 노을빛 수평선 하나. 낮게 들어오는 앰버 빛이 나무 벤치와 코트의 그림자를 길게 늘인다.

```
front elevation of a single tall arched display window set into a granite neo-classical department store facade, centered and symmetrical, eye level, blue hour, the window glowing from inside, inside the window a single glowing amber horizon line across the back wall like a sunset, low raking warm light, a simple oak bench and a wool coat on a stand casting long shadows across the floor, calm and nostalgic, editorial architectural photography, Fujifilm medium format, soft grain, quiet and precise, muted palette --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

## ⑥ CHAPTER 4 · BULB (겨울 · 크리스마스 피날레)

필라멘트 전구가 눈처럼 세로로 늘어진다. 봄의 새싹, 여름의 파란 원통, 가을의 벤치가 한 창에 모인다. 빨간 리본 하나.

```
front elevation of a single tall arched display window set into a granite neo-classical department store facade, centered and symmetrical, eye level, blue hour, the window glowing from inside, inside the window hundreds of warm filament light bulbs hanging on thin vertical wires like falling snow, gathered together below them a small white paper sprout, a cobalt blue cylinder and an oak bench, one red silk ribbon tied around a gift box on the bench, festive but restrained, editorial architectural photography, Fujifilm medium format, soft grain, quiet and precise, muted palette --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

## ⑦ SPREAD — 창에서 매장으로

창의 사물이 매장 아트리움의 작은 연출로 이어진다. 예시는 여름(파란 원통).

```
interior of a refined department store atrium with stone floors and soft daylight, at the base of a marble column a small display on a low pedestal repeating the window motif: three cobalt blue cylinders standing in a shallow tray of still water, a few shoppers passing softly blurred in the background, a plain paper shopping bag with a cobalt blue inner lining resting beside the pedestal, editorial architectural photography, Fujifilm medium format, soft grain, quiet and precise, muted palette --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

계절을 바꾸려면 `three cobalt blue cylinders standing in a shallow tray of still water` 를 각 계절의 사물로 바꾼다.

## ⑧ 뒤표지 — SEE YOU NEXT SEASON

1년이 끝난 파사드. 네 창이 나란히 켜지고 창마다 계절의 색이다.

```
wide symmetrical view of a granite neo-classical department store facade at night with four tall arched display windows in a row, each window glowing in a different season color from left to right: pale green, cobalt blue, warm amber, warm white with one red accent, quiet empty street with a wet pavement reflecting the four colors, negative space in the upper third, editorial architectural photography, Fujifilm medium format, soft grain, quiet and precise, muted palette --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

---

## 미드저니로 만들지 않는 것

- **ABOUT · READING SHINSEGAE 의 사진**: 본점 · 더 헤리티지 · 신세계스퀘어는 **직접 가서 찍는다.** 생성 이미지로 실제 건물을 흉내 내면 분석의 신뢰가 떨어진다.
- **도표 · 1년 달력 · 입면 · 평면 도면**: 일러스트레이터 · 캐드나 이 저장소의 공간 도구로 그린다. 미드저니 도면은 치수가 맞지 않는다.

## 만드는 순서

1. ① 표지를 4장 × 몇 번 돌려 하나 고른다 → **Upscale**.
2. 표지 주소를 `--sref` 로 붙여 ③ → ④ → ⑤ → ⑥ 을 같은 날 한 번에 돌린다(같은 틀 문장 · 같은 sref).
3. 유리에 생긴 이상한 글자 · 간판은 **Vary Region** 으로 그 부분만 지운다(`clean glass, no signage`).
4. ② · ⑦ · ⑧ 을 돌린다.
5. 인쇄용이면 긴 변 3,508px(A4 300dpi) 이상인지 확인한다.

결과 이미지를 보내 주면 연작으로 맞는지 보고, 어긋나는 장의 프롬프트를 고친다.
