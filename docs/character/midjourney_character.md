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
