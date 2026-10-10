# 01 STYLE — 1쪽 가로 띠 이미지 (574 × 172)

1쪽 STYLE 지면 아래쪽 검은 칸(574 × 172, 약 10:3)에 들어갈 사진. 레퍼런스(Grid System Template 001)처럼
**흑백 · 강한 측광 · 천의 결이 보이는 클로즈업 · 얼굴은 드러내지 않음**. 이 칸은 지면 글을 그림 한 장으로 줄인 것이어야 한다.

## 지면 글에서 뽑은 것

| 지면 글 | 그림으로 바꾸면 |
|---|---|
| Q1 "같은 흰 셔츠도 소매를 걷는지, 단추를 어디까지 채우는지에 따라 달라진다. 그 차이가 스타일이다." | 흰 셔츠 소매를 걷는 손 |
| Q2 "무엇을 넣고 무엇을 뺄지 고르는 데서 시작한다." | 화면 대부분을 검정으로 비우고 한 동작만 남긴다 |
| 여는 글 "스타일이 좋은 사람이 지나가면 나는 걸음을 멈춘다." | 흐르는 행인들 사이에 멈춰 선 한 사람 |
| 여는 글 "지나간 뒤에 남은 향에 뒤를 돌아본다." | 돌아서는 코트 깃과 빛 속에 남은 옅은 기척 |
| 풀쿼트 "Anyone can buy the clothes. Only you can make the style." | 옷이 아니라 **옷을 다루는 손** |

## 안 A — 걷어 올린 소매 (추천)

흰 셔츠 소매를 접어 올리는 팔뚝 하나가 화면을 가로지른다. 나머지는 검정. 접힌 커프스의 주름이 빛을 받는다.
누구나 살 수 있는 흰 셔츠가 **한 사람의 손에서 스타일이 되는 순간**. Q1 · Q2 · 풀쿼트를 한 장면이 다 받는다.
172 px 높이에서도 읽히는 형태(가로로 긴 팔 + 밝은 천 덩어리 하나)라서 이 칸에 가장 잘 맞는다.

```
extreme close-up black and white fine art photograph, a forearm rolling up the sleeve of a crisp white cotton shirt, the folded cuff and creases catching hard raking side light, the arm stretches horizontally across the frame, everything else falls into deep black, visible cotton weave and skin texture, cropped tight, anonymous, no face, quiet deliberate gesture, editorial fashion photography, silver gelatin print, high contrast, fine grain --ar 10:3 --style raw --v 7 --s 75 --no text, logo, watermark, color, jewelry, tattoo
```

변형: 단추를 채우는 손(목 아래 첫 단추) — 끝에 `--no` 는 그대로, 앞부분만 `fingers fastening the top button of a white cotton shirt collar` 로 바꾼다.

## 안 B — 멈춘 사람

장노출로 흐려진 행인들 사이에서 검은 오버핏 롱코트의 한 사람만 선명하게 서 있다. 여는 글의 "길 위에서 멈춘다"와
커버의 "I Stop"을 직접 보여준다. 사람이 작게 들어가므로 574 px 에서는 실루엣으로 읽힌다.

```
black and white panoramic street photograph, pedestrians crossing a wide city sidewalk dissolved into long exposure motion blur, one person in an oversized black long coat and wide trousers standing perfectly still and sharp, seen from the side, overcast flat light, grey concrete, generous empty negative space, stillness inside movement, documentary fashion editorial, fine grain --ar 10:3 --style raw --v 7 --s 100 --no text, logo, signage, color, face detail
```

## 안 C — 남은 향

돌아서는 사람의 목덜미와 세운 울 코트 깃, 그 사람이 지나간 자리의 빛줄기 안에 옅은 안개. 향은 찍을 수 없으니
**지나간 뒤의 공기**로 보여준다. 가장 시적이지만 Q1 · Q2 와는 거리가 있다.

```
black and white close-up, the back of a neck and the raised collar of a dark wool coat turning away, a faint veil of mist lingering in a single shaft of hard light where the person just passed, deep shadow, tactile wool texture, intimate and silent, fine art editorial photograph, high contrast, film grain --ar 10:3 --style raw --v 7 --s 100 --no text, face, color, smoke cloud, perfume bottle
```

## 안 D — SECTOR A 의 색 (컬러)

검정 · 올리브 · 베이지 · 오프화이트 · 슬레이트 천이 지층처럼 가로로 겹친 정물. 2쪽 MY STYLE 색을 1쪽에서 미리 보여준다.
레퍼런스의 흑백 톤에서는 벗어난다. 1쪽이 흑백이고 2쪽에 색이 처음 나오게 하려면 쓰지 않는다.

```
abstract still life, heavy fabrics layered in horizontal folds like strata, black wool, olive waxed parka nylon, beige cotton twill, off-white knit, slate blue wool, raking light from the left, deep shadow between the layers, muted earthy palette with no primary colors, tactile macro textile photography, minimal, editorial --ar 10:3 --style raw --v 7 --s 150 --no text, pattern, print, bright color
```

## 미드저니에서

- **비율**: 574 / 172 = 3.34 → `--ar 10:3`. 나온 이미지를 574 × 172 로 줄이면 거의 자를 곳이 없다.
  인쇄 · 레티나용은 2배인 1148 × 344 로 내보낸다(Upscale 후 리사이즈).
- **레퍼런스 톤 맞추기**: 레퍼런스 사진의 흑백 부분만 잘라 미드저니에 올리고, 받은 이미지 주소를 프롬프트 끝에 붙인다.
  `--sref <이미지 주소> --sw 100`. 너무 닮으면(천 모양까지 따라오면) `--sw 50`.
- **고를 때**: 574 × 172 로 줄여서 지면 위에 놓고 본다. 큰 화면에서 좋은 디테일은 이 크기에서 사라진다.
  밝은 덩어리 하나와 검정 여백이 분명한 것을 고른다. 손가락 수 · 단추 위치 같은 손 디테일은 확대해서 확인한다.
- 위 칸의 세 단 글(download now · column grids · modular grids)과 겹치지 않으니 피사체 위치는 자유롭다.
  다만 레퍼런스처럼 밝은 면이 오른쪽으로 갈수록 커지면 왼쪽 큰 제목 STYLE 과 무게가 맞는다.

이 문서의 프롬프트로 만든 이미지는 아직 없다. 미드저니에서 돌린 뒤 고른 이미지만 지면에 넣는다.
