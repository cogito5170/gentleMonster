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
