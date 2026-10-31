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
