# 펼친 잡지 목업에 AR-07 · AR-08 넣기 — 미드저니 생성 (2026-10-23)

- 바탕: 초록빛 펼친 잡지 사진(다른 출판물, 시안 전용).
- 왼쪽 쪽: AR-07 거실 · 식당 실내 모형.
- 오른쪽 쪽: AR-08 빨간 주방 실내 모형.
- B6 의 08쪽 'A room'(AR-07 크게 + AR-08 겹쳐)과 같은 두 장이다.

## 첨부 (웹 Imagine, `--ow` 없는 버전)

| 칸 | 이미지 |
|---|---|
| Image Prompt ① | 잡지 이미지 (먼저) |
| Image Prompt ② | AR-07 거실 |
| Image Prompt ③ | AR-08 주방 |
| Style Reference | 잡지 이미지 |

## 프롬프트

```
close-up photograph of an open magazine held by a hand at the right edge, soft green ambient light over the whole scene, the left page is filled with a large printed photograph of an architectural model interior, a warm living and dining room with a light wooden floor, a wooden table with dark blue chairs, an arched floor lamp, a tall green plant, a dark green wall panel and a black sofa, the right page is filled with a large printed photograph of an architectural model kitchen, a red steel worktable with a stainless top, a large red hanging hood, a white fridge and white benches, the red stays vivid, both photos printed on matte paper and bending with the pages, soft shadow in the gutter, shallow depth of field, film grain --iw 1.2 --ar 16:9 --style raw --no text, letters, words
```

## 조절

| 결과 | 바꿀 것 |
|---|---|
| 두 모형이 한 방으로 섞인다 | `--iw` 0.8, 또는 잡지 이미지를 Image Prompt 에서 빼고 Style Reference 에만 |
| 쪽 속 사진이 모형과 다르다 | `--iw` 1.8 |
| 초록이 빨강을 덮는다 | 맨 뒤에 `--sw 50` |
| 원래 잡지의 원 · 점선을 살리고 싶다 | `--no` 앞에 `thin green circles and dotted guide lines lightly printed in the page margins,` 를 넣는다 |

미드저니는 세 이미지를 섞어서 다시 그린다. 모형이 원본과 똑같아야 하면 생성 결과를 바탕으로 쓰고 두 사진을 포토샵으로 합성한다.

## 같은 방식: FA-02 (왼쪽) · FA-01 (오른쪽) (2026-10-23)

첨부: Image Prompt ① 잡지 이미지 · ② FA-02 바닷가 카페 · ③ FA-01 밤 강변 · Style Reference 잡지 이미지. Weird · Chaos 0.

```
close-up photograph of an open magazine held by a hand at the right edge, soft green light over the whole scene, a deep center fold clearly splits two separate full-page printed photographs, the left page shows a young man in a white short-sleeve shirt and navy trousers sitting on a low cushioned bench inside a seaside cafe, looking out through a tall window at green grass, straw parasols, black volcanic rocks and the sea under a cloudy sky, a small green wooden table with two iced drinks and a woven tray, colourful patterned rugs, the right page shows a night photograph of a young man in a white face mask and a long olive parka over a black shirt and white tee, standing by a river, a lit bridge and city lights reflected in the water behind him, dark grey sky, the two photos do not connect across the fold, matte paper bending with the pages, soft shadow in the gutter, shallow depth of field, film grain --iw 2 --ar 16:9 --style raw --stylize 50 --no text, letters, words, single continuous scene
```

## 같은 방식: FA-02 (왼쪽) · FA-03 (오른쪽) (2026-10-23)

첨부: Image Prompt ① 잡지 이미지 · ② FA-02 바닷가 카페 · ③ FA-03 바위에 웅크린 뒷모습 · Style Reference 잡지 이미지. Weird · Chaos 0.

```
close-up photograph of an open magazine held by a hand at the right edge, soft green light over the whole scene, a deep center fold clearly splits two separate full-page printed photographs, the left page shows a young man in a white short-sleeve shirt and navy trousers sitting on a low cushioned bench inside a seaside cafe, looking out through a tall window at green grass, straw parasols, black volcanic rocks and the sea under a cloudy sky, a small green wooden table with two iced drinks and a woven tray, colourful patterned rugs, the right page shows a high angle photograph of a young man seen from behind, crouching on wet black volcanic rocks at the edge of the sea, wearing an oversized greige ribbed knit sweater and light blue denim, short dark hair, head bowed toward the rocks, white foam and waves around the rocks, low late afternoon sun, the two photos do not connect across the fold, matte paper bending with the pages, soft shadow in the gutter, shallow depth of field, film grain --iw 2 --ar 16:9 --style raw --stylize 50 --no text, letters, words, single continuous scene
```

## 같은 방식: FA-02 (왼쪽) · FA-04 (오른쪽), 왜곡을 줄인 판 (2026-10-23)

첨부: Image Prompt ① 잡지 이미지 · ② FA-02 바닷가 카페 · ③ FA-04 MUNCHIES AND GOODIES 가게 앞 · Style Reference 잡지 이미지. Weird · Chaos 0.
왜곡 줄이기: 책을 거의 평평하게 펴고 정면 가까이서 본다 · 두 세로 사진이 들어가는 비율 3:2 · `--iw 2.5` · `--stylize 20`.

```
photograph of an open magazine lying almost flat, seen from nearly straight above with only a slight tilt, a hand holding the right edge, pale green surface, soft even green light, each page carries one full-page printed photograph reproduced faithfully with its original framing, proportions and colours, pages almost flat with very little curve, a thin straight center fold between the two photographs, the left page shows a young man in a white short-sleeve shirt and navy trousers sitting on a low cushioned bench inside a seaside cafe, looking out through a tall window at green grass, straw parasols, black volcanic rocks and the sea under a cloudy sky, a small green wooden table with two iced drinks and a woven tray, colourful patterned rugs, the right page shows a young man in a white face mask, a long black wool coat, navy trousers and grey sneakers standing in front of a small lit shop at dusk, a white awning with a dark lettered sign, a glass door and a large window with wooden shelves of jars, bottles and plants, a worn concrete wall, the two photos do not connect across the fold, matte paper, film grain --iw 2.5 --ar 3:2 --style raw --stylize 20 --no headline typography, captions, single continuous scene, warped pages
```

간판 글자는 깨질 수 있다. 실제 간판은 원본 사진으로 합성하거나 지면에서 고친다.

## 같은 방식: FA-02 (왼쪽) · FA-04 (오른쪽), 이전 방식 그대로 (2026-10-23)

'왜곡을 줄인 판'은 쓰지 않는다 (사용자 결정). 첨부 · 설정은 앞의 판들과 같다.

```
close-up photograph of an open magazine held by a hand at the right edge, soft green light over the whole scene, a deep center fold clearly splits two separate full-page printed photographs, the left page shows a young man in a white short-sleeve shirt and navy trousers sitting on a low cushioned bench inside a seaside cafe, looking out through a tall window at green grass, straw parasols, black volcanic rocks and the sea under a cloudy sky, a small green wooden table with two iced drinks and a woven tray, colourful patterned rugs, the right page shows a young man in a white face mask, a long black wool coat, navy trousers and grey sneakers standing in front of a small lit shop at dusk, a white awning with a dark lettered sign, a glass door and a large window with wooden shelves of jars, bottles and plants, a worn concrete wall, the two photos do not connect across the fold, matte paper bending with the pages, soft shadow in the gutter, shallow depth of field, film grain --iw 2 --ar 16:9 --style raw --stylize 50 --no text, letters, words, single continuous scene
```

## 책 배치가 바뀐 원인과 다시 쓴 판 (2026-10-23)

윗줄(FA-04) 결과는 3:2 비율이다. 책을 위에서 평평하게 본 구도로 나왔고, '왜곡을 줄인 판' 프롬프트에서 나온 것이다.
아랫줄(FA-03)은 16:9 이고 잡지 이미지처럼 비스듬하다.
배치를 바꾼 말: `lying almost flat, seen from nearly straight above` · `pages almost flat with very little curve` ·
`thin straight center fold` · `reproduced faithfully with its original framing` · `--ar 3:2` · `--stylize 20` · `--no warped pages`.

다시 쓴 판은 이전 방식에 아랫줄 구도를 글로 적어 고정한다 (비스듬한 낮은 각도, 대각선 접힘, 멀어지며 흐려지는 오른쪽 쪽).

```
close-up photograph of an open magazine seen from a low oblique angle, the book tilted diagonally across the frame, the left page curving up toward the top left corner, the center fold running diagonally from the top middle to the bottom right, the right page receding and slightly out of focus, a hand holding the right page edge, pale green background, soft green light over the whole scene, two separate full-page printed photographs, the left page shows a young man in a white short-sleeve shirt and navy trousers sitting on a low cushioned bench inside a seaside cafe, looking out through a tall window at green grass, straw parasols, black volcanic rocks and the sea under a cloudy sky, a small green wooden table with two iced drinks and a woven tray, colourful patterned rugs, the right page shows a young man in a white face mask, a long black wool coat, navy trousers and grey sneakers standing in front of a small lit shop at dusk, a white awning with a dark lettered sign, a glass door and a large window with wooden shelves of jars, bottles and plants, a worn concrete wall, the two photos do not connect across the fold, matte paper bending with the pages, soft shadow in the gutter, shallow depth of field, film grain --iw 2 --ar 16:9 --style raw --stylize 50 --no text, letters, words, single continuous scene, flat lay, top view
```

구도를 가장 확실히 고정하는 법: 마음에 든 아랫줄 결과 한 장을 잡지 이미지 대신 Image Prompt ① 과 Style Reference 에 넣는다.

## 오른쪽 쪽(FA-04)이 다시 그려질 때 (2026-10-23)

원인:
1. 오른쪽 설명이 짧고 일반적이었다 (`a small lit shop`, `wooden shelves of jars`). 미드저니가 빈 곳을 자기 가게로 채웠다.
2. `--no text, letters, words` 가 간판을 지우고, `a dark lettered sign` 과 부딪쳤다.
3. `the right page receding and slightly out of focus` 가 오른쪽을 흐리게 다시 그리게 했다.
4. 오른쪽 설명이 프롬프트 뒤쪽에 있었다. 미드저니는 앞쪽 말을 더 무겁게 본다.

고침: 오른쪽을 먼저, 원본 사진의 배치대로 왼쪽 → 가운데 → 오른쪽 → 위 → 아래 순서로 적는다. 흐림을 빼고, `--no` 에서 글자를 뺀다.

```
close-up photograph of an open magazine seen from a low oblique angle, the book tilted diagonally across the frame, the left page curving up toward the top left corner, the center fold running diagonally from the top middle to the bottom right, a hand holding the right page edge, pale green background, soft green light over the whole scene, two separate full-page printed photographs, the right page shows a sharp full-length evening photograph of a white-framed shop front, a long white awning across the top with dark capital letters, on the left an open glass door into a bright warm interior with a small caged ceiling lamp above it, on the right a large two-pane display window with shelves of ceramic jugs, cups, two wine bottles and a small plant, rough grey concrete wall around the shop, in the middle a young man in a white face mask stands with hands in the pockets of a long black wool coat, navy trousers and grey sneakers, looking to the left, grey asphalt at the bottom with a white painted line on the left and a metal sawhorse bench on the right, the left page shows a young man in a white short-sleeve shirt and navy trousers sitting on a low cushioned bench inside a seaside cafe, looking out through a tall window at green grass, straw parasols, black volcanic rocks and the sea under a cloudy sky, a small green wooden table with two iced drinks and a woven tray, colourful patterned rugs, the two photos do not connect across the fold, matte paper bending with the pages, soft shadow in the gutter, film grain --iw 2 --ar 16:9 --style raw --stylize 50 --no headline typography, captions, single continuous scene, flat lay, top view
```

그래도 다시 그려지면: Image Prompt 에서 FA-04 를 ② 로, FA-02 를 ③ 으로 바꾼다.
