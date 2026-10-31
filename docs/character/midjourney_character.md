# 캐릭터화된 지원자 이미지 — 미드저니 (2026-10-31)

- 구도: 첫 번째 사진(안경원 안 정면 셀카, 머리와 어깨, 노출콘크리트 천장 · 철골 보 · 빛나는 선반).
- 얼굴 · 머리 · 안경 · 옷: 사진 다섯 장을 캐릭터 레퍼런스로 쓴다.
- 이 버전은 `--ow` 를 지원하지 않으므로 Character Reference (`--cref`, V6.1) 를 쓴다.

## 첨부

| 칸 | 이미지 |
|---|---|
| Image Prompt | 1번 (구도) |
| Character Reference | 1번 · 3번 (정면) · 2번 (상반신). 옆모습 4 · 5번은 머리 모양이 흔들리면 더한다 |

## 프롬프트

```
stylized 3D animated character portrait of a young East Asian man, close-up selfie framing from a slightly low angle, head and shoulders centred, looking straight into the camera with a calm neutral expression, dark brown hair parted in the middle and swept to both sides with a few flyaway strands on top, translucent grey rectangular acetate glasses, light stubble on the upper lip and chin, navy and white small check zip-up shirt jacket over a dark navy tee, black backpack straps, behind him an eyewear store with an exposed concrete ceiling, a grey steel beam, backlit white shelves with rows of sunglasses and a curved mirror panel on the left, warm daylight, soft clay-like shading, clean simple shapes, recognisable likeness --cref --cw 100 --iw 1.5 --ar 3:4 --stylize 150 --v 6.1 --no text, logo
```

`--cref` 뒤의 칸은 웹에서 Character Reference 칸에 이미지를 넣으면 자동으로 채워진다. 칸에 넣었다면 글에서는 `--cref` 를 지운다.

## 화풍 바꾸기 (맨 앞 문구만 바꾼다)

| 화풍 | `stylized 3D animated character portrait` 대신 |
|---|---|
| 2D 일러스트 | `flat 2D illustration portrait with clean outlines and soft flat colours` |
| 애니메이션 | `Japanese anime style portrait with clean cel shading` |
| 피규어 | `collectible vinyl toy figure portrait, glossy plastic finish` |

## 조절

- 본인과 덜 닮았다: Character Reference 에 정면 사진만 남기고 `--cw 100` 그대로.
- 옷까지 너무 똑같다 / 옷을 바꾸고 싶다: `--cw 30` (얼굴과 머리 위주로 따른다).
- 구도가 첫 번째 사진과 다르다: `--iw 2`.
- 배경의 선반 · 철골이 사라진다: 배경 묘사를 프롬프트 앞쪽으로 옮긴다.

`--cref` 는 미드저니가 만든 인물에서 가장 잘 맞고, 실제 사진에서는 닮음이 덜할 수 있다.

## 얼굴 특징이 드러나는 강한 판 (2026-10-31)

첫 결과는 얼굴이 갸름하고 눈이 큰 '잘생긴 일반 캐릭터'로 바뀌었다. 미드저니가 얼굴을 다듬었기 때문이다 (`--stylize 150`, 화풍 문구).
고침: 실제 특징을 하나씩 적고 다듬기를 막는다 (`--style raw`, `--stylize 50`, `--no` 에 미화를 넣는다). 강하게 보이도록 얼굴이 화면을 채우는 근접 · 정면 플래시 · 정면 응시로 간다.
Character Reference 에는 정면 사진 1 · 3번만 넣는다.

```
extreme close-up semi-realistic stylized 3D character portrait of a young East Asian man, his face fills the whole frame, slightly low wide-angle selfie view, deadpan stare straight into the lens, broad round face with full cheeks and a wide soft jaw, dark brown hair parted in the middle falling in heavy curtains over the temples with thin flyaway strands standing up on top, straight thick eyebrows, narrow single-lidded eyes, wide nose with a rounded tip and visible pores, full pink lips slightly parted, thin stubble on the upper lip and chin, a few small moles on the cheeks, grey translucent rectangular acetate glasses with lavender reflections on the lenses, navy check shirt collar at the bottom edge, harsh direct on-camera flash, deep shadows, cool blue shelf light behind, exaggerate his real features slightly like a caricature, sculpted detailed skin --cw 100 --iw 1.5 --ar 3:4 --style raw --stylize 50 --v 6.1 --no idealized face, slim face, big eyes, pretty, smooth skin, text, logo
```

## 더 실사에 가까운 판 (2026-10-31)

바꾼 것: 3D 캐릭터 · 캐리커처 · 조각 같은 피부 문구를 빼고, 실제 사진 용어(카메라 · 렌즈 · 플래시 · 필름 질감)로 바꾼다. `--no` 에 3D · CGI · 일러스트를 넣는다.

```
photorealistic extreme close-up portrait photograph of a young East Asian man, his face fills the whole frame, slightly low wide-angle selfie view, deadpan stare straight into the lens, broad round face with full cheeks and a wide soft jaw, dark brown hair parted in the middle falling in heavy curtains over the temples with thin flyaway strands standing up on top, straight thick eyebrows, narrow single-lidded eyes, wide nose with a rounded tip and visible pores, full pink lips slightly parted, thin stubble on the upper lip and chin, a few small moles on the cheeks, grey translucent rectangular acetate glasses with lavender reflections on the lenses, navy check shirt collar at the bottom edge, harsh direct on-camera flash, deep shadows, cool blue shelf light behind, natural skin texture with pores and fine hairs, shot on a 28mm lens, editorial fashion photography, subtle film grain --cw 100 --iw 1.5 --ar 3:4 --style raw --stylize 30 --v 6.1 --no 3D render, CGI, cartoon, illustration, plastic skin, idealized face, slim face, big eyes, smooth skin, text, logo
```

## 참고 이미지의 그래픽 스타일로 (2026-10-31)

참고 이미지(은빛 단발, 투명 바이저 안경, 주황 · 분홍 · 파랑 빛, 젖은 듯한 피부, 비닐 옷)의 스타일만 가져오고, 얼굴은 지원자 사진에서 가져온다.

첨부: Style Reference 참고 이미지 · Character Reference 지원자 사진 2장(정면 · 옆) · Image Prompt 지원자 정면 사진.

```
photorealistic futuristic beauty editorial close-up portrait of a young East Asian man, face filling the frame, head slightly tilted, calm half-lidded gaze, broad round face with full cheeks and a wide soft jaw, dark hair parted in the middle falling in heavy curtains over the temples, recoloured glossy metallic silver blue, straight thick eyebrows, narrow single-lidded eyes, wide nose with a rounded tip, full lips slightly parted, light stubble, a wraparound clear acrylic visor glasses with a thin frame and a translucent holographic interface panel over one eye, a vertical orange light streak reflected on the visor, magenta and electric blue light spilling across the cheek, dewy glossy skin with visible pores and freckles, high neck clear PVC top wrapping the neck and shoulders, pale lavender grey studio background, shot on 85mm, shallow depth of field, crisp detail --sw 200 --cw 100 --iw 1.2 --ar 9:16 --style raw --stylize 100 --v 6.1 --no slim face, big eyes, makeup, text, logo
```

머리를 지원자 그대로 검은 머리로 두려면 `recoloured glossy metallic silver blue` 를 `with a glossy wet sheen` 으로 바꾼다.

## 코트 이미지에 안경만 씌우기 (2026-10-31)

- 바탕: 적갈색 코트를 입은 지원자 이미지 (흰 벽, 흐린 양옆).
- 안경: 셀카 속 안경. 연기 낀 회갈색 반투명 아세테이트, 모서리가 둥근 직사각형, 중간 두께, 앞면 양 끝의 작은 은색 핀, 연보라 반사 코팅 렌즈.
- 이 세션의 이미지는 Codex 로만 만들고, Codex 는 사진을 입력으로 받지 않는다. 얼굴 · 배경을 그대로 두는 편집은 Gemini (편집에 가장 강함) 또는 미드저니 Editor 로 한다.

### Gemini (권장) — 첨부: 1 코트 이미지 · 2 셀카

```
Edit the first image. Add only a pair of glasses to the man's face. Keep everything else in the first image exactly the same: his face, features, expression, skin, hair, head angle, the rust wool coat, the black top, the white background, the blur at the sides, the framing, the light and the film grain. Do not redraw or retouch the face.

The glasses are the ones worn in the second image: a smoky grey-brown translucent acetate frame, soft rectangular shape with rounded corners, medium-thick rims, a keyhole-free straight bridge, small silver rivets at the outer front corners, and clear lenses with a faint lavender anti-reflective sheen. Fit them naturally to his face at the right size and angle, resting on the nose with the temples going back over the ears, with soft shadows on the cheeks and a slight reflection of the white room in the lenses. His eyes stay visible through the lenses. Take nothing else from the second image.
```

같은 대화에서 고치는 말:
- 얼굴이 바뀌었다 → `The face changed. Restore the exact face from the first image and only add the glasses.`
- 안경이 다르다 → `Make the frame smoky grey-brown translucent acetate with rounded rectangular lenses, exactly like the second image.`
- 렌즈가 너무 반사된다 → `Make the lenses clearer so his eyes are fully visible, keep only a faint lavender sheen.`

### 미드저니 Editor — 1 코트 이미지를 올리고 눈 주변(눈썹 ~ 광대, 귀 앞)만 칠한다

```
smoky grey-brown translucent acetate glasses with soft rectangular rounded lenses, medium-thick rims, small silver rivets at the front corners, clear lenses with a faint lavender sheen, resting naturally on the nose, eyes visible through the lenses, same face, same lighting, film grain --style raw
```

## 카메라를 살짝 위에서 찍은 각도로 (2026-10-31)

지금 이미지는 아래에서 올려다본 셀카 각도다(턱 · 콧구멍이 크게, 이마 · 천장이 보인다). 살짝 위(눈높이보다 15~20° 위)에서 내려다본 각도로 바꾼다.

### Gemini — 첨부: 지금 이미지

```
Change only the camera angle of this image. Re-shoot the same moment from slightly above his eye level, about 15 to 20 degrees higher, with the camera tilted gently down toward his face, like a selfie held a little above the head. He keeps looking straight into the lens, so his eyes look slightly upward.

Keep everything else the same: his face and features, the round face with full cheeks, the middle-parted hair with flyaway strands, the stubble, the moles, the expression, the grey translucent glasses with lavender reflections, the navy check shirt, the eyewear store behind him, the light, the colours and the painted, cel-shaded illustration style with sharp light patches on the skin.

From this higher angle the forehead and the top of the hair look a little larger, the chin and the nostrils look smaller and partly hidden, the jaw line looks a little slimmer, the glasses sit slightly lower on the face, and more of the floor and the lower shelves show in the background while the ceiling mostly leaves the frame. Same vertical framing, head and shoulders.
```

같은 대화에서 고치는 말:
- 얼굴이 바뀌었다 → `The face changed. Keep the exact face and features from the original, only the camera angle changes.`
- 각도가 충분하지 않다 → `Raise the camera more, so we look clearly down onto his face.`
- 화풍이 실사로 바뀌었다 → `Keep the same painted cel-shaded illustration style as the original.`

### 미드저니 (대안) — Image Prompt: 지금 이미지

```
same young man, slightly high angle selfie looking down on him from just above eye level, he looks up into the lens, round face with full cheeks, middle-parted dark hair with flyaway strands, light stubble, grey translucent glasses with lavender reflections, navy check shirt, eyewear store with lit white shelves behind, painted cel-shaded illustration style with sharp highlights on the skin --iw 2 --ar 3:4 --style raw --stylize 50 --no low angle, nostrils
```

## 브랜드 웹 히어로 컷의 스타일로 (2026-10-31)

참고(1번)에서 가져오는 것: 실사 사진 · 얼굴을 화면 가득 자른 극단적 근접 · 3/4 옆으로 돌린 얼굴과 비껴 보는 시선 · 옆에서 드는 강한 햇빛 · 따뜻한 필름 톤 · 어두운 배경 · 가로로 긴 화면.
가져오지 않는 것: 로고 · 메뉴 · 글자, 참고 속 인물, 참고 속 실제 제품.
1번은 상단 로고 · 메뉴를 잘라 내고 Style Reference 에 넣는다. Character Reference 는 2번보다 실제 셀카(정면 · 옆)가 실사에 맞다.

첨부: Image Prompt 2번 · Style Reference 1번(잘라 낸 것) · Character Reference 실제 셀카 정면 · 옆.

```
photorealistic extreme close-up editorial portrait of a young East Asian man, the frame cuts through his forehead and chin, face turned three-quarters to the left, eyes looking down and away past the camera, broad round face with full cheeks, dark middle-parted hair falling over the temples with loose strands catching the light, light stubble, a small mole on the cheek, grey translucent rectangular acetate glasses filling the upper part of the frame, lenses reflecting warm light, strong low sunlight from the side, warm skin tones, natural skin texture with pores, dark soft background, shallow depth of field, 35mm film look, quiet confident mood --sw 150 --cw 80 --iw 1 --ar 16:9 --style raw --stylize 50 --v 6.1 --no text, logo, menu, letters, cel shading, illustration
```

안경을 참고처럼 큰 타원형 선글라스로 바꾸려면 `grey translucent rectangular acetate glasses filling the upper part of the frame, lenses reflecting warm light,` 를
`oversized oval dark tortoiseshell sunglasses with thick rims and smoky brown lenses,` 로 바꾸고 `--cw 50` 으로 내린다 (가상의 안경, 실제 제품을 따라 그리지 않는다).

## 잡지 커버 촬영처럼 — 얼굴 · 머리 · 안경은 그대로 (2026-10-31)

조건: 1번 같은 모델 잡지 커버 촬영 · 2번의 얼굴 · 머리 · 안경은 바꾸지 않는다 · 배경은 바꿔도 된다.
미드저니 생성은 얼굴을 매번 다시 그리므로, 바꾸지 않으려면 Editor 에서 얼굴 · 머리 · 안경을 칠하지 않고 남겨야 한다.

### A. Editor (권장, 얼굴 · 머리 · 안경 그대로)

2번을 Editor 에 올리고 배경과 옷(목 아래)만 칠한다. 머리카락 가장자리와 안경 다리는 칠하지 않는다. Style Reference 칸에 1번(로고 · 메뉴를 잘라 낸 것).

```
high fashion magazine cover photo shoot, extreme close-up of a male model, dark warm-toned studio backdrop softly falling into shadow, strong low warm sunlight raking in from the side, golden rim light along the hair and jaw, black fine-knit high neck top, shallow depth of field, 35mm film grain, editorial luxury eyewear campaign --sw 150 --style raw --no text, logo, letters, store, shelves
```

### B. 생성 (커버 느낌을 더 강하게, 얼굴은 조금 달라질 수 있음)

Image Prompt 2번 · Character Reference 2번 · Style Reference 1번(잘라 낸 것).

```
high fashion magazine cover photo shoot of a young East Asian male model, the same face, hair and glasses as the reference, broad round face with full cheeks, dark middle-parted hair with loose flyaway strands, grey translucent rectangular acetate glasses with lavender reflections, light stubble, face turned slightly to the left, eyes looking past the camera, extreme close-up with the frame cropping the top of the hair and the chin, strong low warm sunlight from the side, golden rim light, dark warm backdrop, black fine-knit high neck top, shallow depth of field, 35mm film grain, editorial luxury eyewear campaign --cw 100 --iw 2 --sw 150 --ar 16:9 --style raw --stylize 50 --v 6.1 --no text, logo, letters, store, shelves
```
