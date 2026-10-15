# 신세계 VMD 포트폴리오 — 장면별 이미지 (미드저니 프롬프트, v2)

[storyline.md](storyline.md) 의 순서대로. 미드저니는 영어를 가장 잘 따르므로 영어로 쓰고 뜻을 우리말로 붙였다.

## 공통 규칙

- **A4 가로**: `--ar 297:210`.
- **글자 · 로고 금지**: 모든 프롬프트 끝에 `--no text, letters, logo, signage, watermark`. 유리 글자 · 행택 글자 · 제목은 인디자인 · 피그마에서 얹는다. 신세계 · paloma wool · COS 이름을 프롬프트에 넣지 않는다.
- **레퍼런스 사진을 스타일로**: 받은 paloma wool · COS 창 사진을 미드저니에 올려 `--sref <URL1> <URL2>` 로 붙이면 흰 무대 · 반투명 · 절제된 색이 따라온다. 표지를 고른 뒤에는 **표지 URL 을 `--sref` 로** 나머지 장에 붙여 한 권처럼 맞춘다.
- **Raw 모드**를 켠다(버전에 따라 `--style raw` 또는 `--raw`, 웹 설정에서 켜는 편이 안전).
- **표기**: 판권 자리에 *"Concept images generated with Midjourney. Concept, prompts and art direction by Jeong Hyeokju. Personal proposal, not affiliated with Shinsegae."*

공통 꼬리말(모든 프롬프트에 이미 붙여 둠):

```
editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

---

## ① 표지 · WINDOW — 나를 진열한 창

공통: 매장 밖 보도에서 정면으로 본 쇼윈도. 흰 무대. 유리에 맞은편 석조 건물과 따뜻한 가로등이 **희미하게** 비친다.

### ①-A 입히다 · 보다 · 짓다 — 마네킹 하나에 셋을 겹친다 (추천)

```
front view from the sidewalk of a minimal boutique display window, off-white backdrop and a white plinth, one headless matte white mannequin styled in an oversized black wool long coat over a grey knit and wide-leg beige trousers, a vintage silver film camera hanging from the mannequin's hand by a leather strap, the mannequin standing on a white architectural scale model base with tiny cut-out walls, a small blank paper hang tag tied to the coat sleeve, two narrow spotlights from above, faint reflection of a classical stone building facade and warm street lights on the glass, calm and precise, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

뜻: 흰 배경 · 흰 받침. 머리 없는 흰 마네킹이 검은 오버핏 롱코트 · 회색 니트 · 통 넓은 베이지 바지를 입었다. 손에 가죽 스트랩으로 은색 필름 카메라가 걸려 있고, 발밑은 작은 벽이 세워진 흰 건축 모형 받침이다. 소매에 빈 행택 하나. 유리에 석조 건물 정면과 가로등이 희미하게 비친다.

### ①-B 세 단위 — COS 처럼 셋을 나란히

```
front view from the sidewalk of a minimal boutique display window, three tall translucent fabric panels hanging from the ceiling in a row with equal spacing, behind the left panel the silhouette of a long black coat on a hanger, behind the middle panel a vintage film camera on a slim plinth, behind the right panel a white architectural scale model on a plinth, each panel softly backlit by a warm spotlight, white floor plinth running across the window, faint reflection of a classical stone building facade and warm street lights on the glass, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

뜻: 반투명 천 세 폭이 같은 간격으로 걸려 있고, 그 뒤로 왼쪽부터 검은 롱코트 · 필름 카메라 · 흰 건축 모형의 실루엣이 비친다.

### ①-C 반투명 필름 — paloma wool 처럼, 유리에 붙은 것만 또렷하게

```
front view from the sidewalk of a boutique display window covered with frosted translucent film, behind the film a black long coat and a grey knit hung casually on a single white rail, a blurred white architectural scale model on the floor, only one object pressed against the glass is sharp: a vintage film camera with its strap, everything further away softly blurred, diffused white light, faint reflection of a classical stone building facade on the glass, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

뜻: 창 전체에 반투명 필름. 레일에 무심히 걸린 롱코트와 니트, 바닥의 흐린 건축 모형. 유리에 붙은 카메라 하나만 또렷하다 — "보는 사람"이 가장 앞에 있다.

변형:
- 요소를 C안(코트 · 향 · 빛)으로: `vintage silver film camera` → `an unlabeled amber glass perfume bottle`, `architectural scale model base` → `a single bare filament light bulb hanging above`.
- 요소를 B안(도구)으로: 카메라 → `a red pin cushion with dressmaker pins`, 모형 받침 → `a yellow cloth tape measure unrolled down to the floor`.

### ①-D 보다 · 집다 · 챙기다 — 유리를 지나 밖으로 나온 행택

설명: [see_pick_keep.md](see_pick_keep.md).

```
front view from the sidewalk of a minimal boutique display window, off-white backdrop, one headless matte white mannequin in an oversized black wool long coat and wide-leg beige trousers, a vintage film camera hanging from its hand, a blank paper hang tag on a thin cotton string tied to the coat sleeve, the string stretching forward and passing through the glass so the tag dangles outside the window on the viewer's side, close to the camera, slightly in focus, a folded white paper shopping bag with tissue paper waiting at the mannequin's feet, two narrow spotlights, faint reflection of a classical stone building facade on the glass, surreal but quiet, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 200 --no text, letters, logo, signage, watermark
```

뜻: 마네킹 소매의 행택 실이 유리를 지나 밖으로 나와, 행택이 보는 사람 앞에 매달려 있다. 발밑에는 티슈지가 든 흰 쇼핑백.
유리를 지나는 실이 어색하면 창 사진과 행택 사진을 따로 만들어 포토샵에서 합친다.

### ①-E 보다 · 집다 · 챙기다 — 세 컷

세 장을 따로 만들어 한 쪽에 COS 처럼 같은 간격으로 놓는다(각 `--ar 1:2`). 세 장 모두 같은 `--sref`.

```
SEE:  close-up of a boutique display window glass, the faint reflection of a young person's eyes and face on the glass, behind the glass a black wool coat on a white mannequin softly out of focus, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 1:2 --s 150 --no text, letters, logo, signage, watermark

PICK: close-up of a hand reaching to pick up a neatly folded grey knit from the top of a triangular stack of knitwear in black, olive and beige on a pale oak table, soft side light, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 1:2 --s 150 --no text, letters, logo, signage, watermark

KEEP: close-up of two hands placing a grey knit wrapped in white tissue paper into a plain white paper shopping bag with a slate inner lining, a small blank hang tag resting on top, soft side light, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 1:2 --s 150 --no text, letters, logo, signage, watermark
```

손 · 얼굴이 들어가는 컷은 미드저니가 어색하게 그리기 쉽다. **직접 찍으면 더 좋다**(지원자의 손 · 지원자의 니트).

## ② WINDOWS OF TIME · CONCEPT — 재료 무드보드

```
top-down flat lay material board on a pale granite slab, arranged in a precise grid: white paper sprouts on fine sand, three small cobalt blue acrylic cylinders in a shallow tray of still water, an oak wood block with a long amber shadow, a brass filament light bulb, one red silk ribbon, fabric swatches in black wool, olive cotton, beige linen and slate knit, a few dressmaker pins, soft daylight from one side, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

## ③–⑥ WINDOWS OF TIME · 네 계절 창 (마네킹 착장 + 소품)

네 장이 같은 창으로 보이도록 **틀 문장을 그대로** 쓴다:

```
front elevation of a single tall arched display window set into a granite neo-classical department store facade, centered and symmetrical, eye level, blue hour, the window glowing from inside
```

### ③ SPROUT (봄)

```
front elevation of a single tall arched display window set into a granite neo-classical department store facade, centered and symmetrical, eye level, blue hour, the window glowing from inside, inside two headless matte white mannequins in spring looks: a pale green light trench coat over a white shirt, and a beige knit vest with wide cream trousers, standing on a bed of pale sand where hundreds of small white paper sprouts are growing, one taller sprout under a narrow spotlight, fresh and calm, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

### ④ PUDDLE (여름)

```
front elevation of a single tall arched display window set into a granite neo-classical department store facade, centered and symmetrical, eye level, blue hour, the window glowing from inside, inside two headless matte white mannequins in summer looks: a loose white linen shirt with cobalt blue wide shorts, and a sleeveless navy dress, standing barefoot in a shallow still pool of water like a mirror, three cobalt blue cylinders of different heights beside them with perfect reflections, one narrow spotlight from above, cool and clear, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

### ⑤ DUSK (가을)

```
front elevation of a single tall arched display window set into a granite neo-classical department store facade, centered and symmetrical, eye level, blue hour, the window glowing from inside, inside two headless matte white mannequins in autumn looks: a camel wool coat with an olive knit and brown wide trousers, and a rust suede jacket over a cream turtleneck, one seated on a simple oak bench, a single glowing amber horizon line across the back wall like a sunset, low raking warm light casting long shadows, calm and nostalgic, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

### ⑥ BULB (겨울 · 크리스마스 피날레)

```
front elevation of a single tall arched display window set into a granite neo-classical department store facade, centered and symmetrical, eye level, blue hour, the window glowing from inside, inside two headless matte white mannequins in winter looks: an oversized black wool long coat with a charcoal scarf, and an ivory shearling jacket with slate trousers, hundreds of warm filament light bulbs hanging on thin vertical wires like falling snow, at their feet a small white paper sprout, a cobalt blue cylinder and an oak bench gathered together, one red silk ribbon tied around a gift box on the bench, festive but restrained, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

착장 문장(`in spring looks: ...`)은 예시다. 실제로 제안할 룩이 정해지면 그 착장으로 바꾼다 — 이 부분이 지원자의 실력이 보이는 곳이다.

## ⑦ SPREAD — VP 에서 PP 로

```
interior of a refined department store floor with stone floors and soft daylight, at the base of a marble column a point display on a low white pedestal: one headless mannequin in a loose white linen shirt and cobalt blue wide shorts beside three cobalt blue cylinders in a shallow tray of still water, behind it a rail of the same garments arranged by color, shoppers passing softly blurred, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

## ⑧ DISPLAY RULES — 직접 찍은 사진이 없을 때만

원칙마다 한 장. 예: 삼각 구성.

```
minimal retail table display on a pale oak table against an off-white wall, folded knitwear in black, olive, beige and slate stacked in a clear triangular composition with the tallest stack in the middle, one pair of horn-rimmed glasses and a vintage watch as accents, soft side light, editorial retail window photography, Fujifilm medium format, soft grain, quiet and precise, off-white with black, olive, beige and slate --ar 297:210 --s 150 --no text, letters, logo, signage, watermark
```

다른 원칙은 `stacked in a clear triangular composition` 을 `arranged in color blocks from dark to light` · `repeated in a rhythm of three identical units` 등으로 바꾼다.

---

## 미드저니로 만들지 않는 것

- **LOOKBOOK · STYLING**: 지원자 본인 사진, 직접 입힌 마네킹 사진.
- **READING SHINSEGAE**: 본점 · 더 헤리티지 · 신세계스퀘어를 직접 가서 찍는다.
- **도면 · 스펙 표 · 영수증(RECEIPT)**: 일러스트레이터 · 캐드 · 이 저장소의 공간 도구로 그린다.

## 만드는 순서

1. 레퍼런스 두 장을 `--sref` 로 붙여 ①-A · B · C 를 돌린다 → 요소 세 가지와 표지 형식을 함께 고른다.
2. 고른 표지를 Upscale 하고, 그 URL 을 `--sref` 로 ③–⑥ 을 같은 날 한 번에 돌린다.
3. 유리의 이상한 글자 · 간판은 Vary Region 으로 지운다(`clean glass, no signage`).
4. 인쇄용이면 긴 변 3,508px(A4 300dpi) 이상인지 확인한다.
