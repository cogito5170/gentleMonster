# 01 STYLE — 1쪽 가로 띠 이미지 (574 × 172)

1쪽 STYLE 지면 아래쪽 검은 칸(574 × 172, 약 10:3)에 들어갈 사진. 레퍼런스(Grid System Template 001)처럼
**흑백 · 강한 측광 · 천의 결이 보이는 클로즈업 · 얼굴은 드러내지 않음**. 이 칸은 지면 글을 그림 한 장으로 줄인 것이어야 한다.

## 정한 샷 — 「반쯤 걷은 소매」

**한 줄:** 흰 셔츠 소매를 두 번째로 접어 올리다 멈춘 손. 접힌 커프스 아래로 빈티지 시계가 반쯤 드러난다.

**왜 이 샷인가**
- **Q1 그대로다.** "같은 흰 셔츠도 소매를 걷는지에 따라 달라진다." 누구나 살 수 있는 흰 셔츠가 한 사람의 손에서 스타일이 된다.
- **Q2 를 화면이 한다.** 화면 대부분을 검정으로 비우고 동작 하나만 남긴다. 무엇을 넣고 무엇을 뺄지 고른 결과다.
- **화자 본인의 스타일이다.** MY STYLE 의 ACCESSORY(빈티지 시계)가 소매를 걷어야 보인다. 소매를 걷는 일은 무엇을 드러낼지 고르는 일이다.
- **멈춘 순간이다.** 다 걷은 소매가 아니라 **걷는 중에 멈춘** 소매. 책 전체의 동사 "멈춘다"를 동작으로 보여준다.
- **시리즈가 된다.** 화자의 역할이 보는 사람 → 찍는 사람 → 만드는 사람으로 바뀌므로([storytelling.md](storytelling.md)) 같은 문법(흑백 · 검정 여백 · 손 하나 · 멈춘 동작)으로 다음 섹션을 잇는다.
  02 PICTURE 는 셔터 위에 멈춘 검지, 03 ARCHITECTURE 는 문틀을 짚은 손과 그 너머로 들어오는 빛.

**샷 설계**

| 항목 | 정한 것 |
|---|---|
| 피사체 | 맨 팔뚝 하나 + 흰 코튼 포플린 셔츠 소매(살짝 입은 흔적). 얼굴 · 몸통 없음 |
| 동작 | 반대 손 손가락이 두 번째 접힘을 잡고 멈춰 있다. 커프스 가장자리 밑으로 낡은 가죽 줄 시계의 일부 |
| 구도 | 팔이 왼쪽 끝에서 들어와 가로로 뻗는다(팔꿈치는 잘림). 접힌 소매 · 손은 오른쪽 1/3 지점(가로 60–70%). 위아래 여백은 검정 |
| 빛 | 오른쪽 위에서 거의 스치듯 들어오는 단단한 빛 하나. 천의 짜임과 주름 골이 보이고, 나머지는 빛이 닿지 않아 검정으로 떨어진다 |
| 렌즈 · 초점 | 100 mm 매크로 느낌, 팔 높이에서 수평. 초점은 접힌 천 가장자리, 손끝 쪽은 살짝 흐림 |
| 톤 | 흑백 · 은염 인화 느낌. 배경은 지면의 검은 칸과 이어질 만큼 깊은 검정, 셔츠 하이라이트는 날리지 않음. 고운 입자 |
| 172 px 에서 읽히는 것 | 오른쪽으로 커지는 밝은 천 덩어리 하나 + 시계 유리의 작은 반짝임 하나. 왼쪽 위 큰 제목 STYLE 과 무게가 맞는다 |
| 빼는 것 | 글자 · 로고 · 색 · 반지와 팔찌 · 타투 · 시계 브랜드 표시 |

**작가 컨셉 프롬프트 (물성은 따로 정의)**

이미지의 물성(재질 · 빛 · 톤 · 렌즈)은 따로 정한다. 아래는 작가의 컨셉만 담은 프롬프트이고, 물성 프롬프트를 뒤에 붙여 쓴다.
그 아래의 확정 프롬프트는 물성까지 적어 둔 이전 버전이다.

```
01 STYLE         a sleeve being rolled up, paused halfway, the quiet moment an ordinary white shirt becomes someone's own style, something personal half revealed at the wrist, a single gesture held still, much left unsaid --ar 10:3
02 PICTURE       a finger resting just before the shutter, the held breath before a passing moment becomes a photograph, the world about to be kept --ar 10:3
03 ARCHITECTURE  a hand at the edge of a doorway, pausing at the threshold, a quiet space beyond waiting to be entered, the moment before stepping in --ar 10:3
```

**미드저니 프롬프트 (확정)**

```
extreme close-up black and white fine art photograph, a bare forearm stretches horizontally into the frame from the left edge, the other hand's fingers pause mid-gesture while rolling up the sleeve of a crisp white cotton poplin shirt for the second fold, the folded cuff half reveals a vintage watch with a worn leather strap, the cuff and hand sit at the right third of the frame, a single hard raking light grazes from the upper right, cotton weave and fold creases sharply visible, everything else falls into deep black, anonymous, no face, quiet deliberate pause, editorial fashion photography, silver gelatin print, high contrast, fine grain --ar 10:3 --style raw --v 7 --s 75 --no text, logo, watermark, color, ring, bracelet, tattoo, brand name on watch
```

레퍼런스 톤을 맞추려면 끝에 `--sref <레퍼런스 흑백 사진 주소> --sw 100`.
시계가 너무 커지거나 소매를 가리면 `vintage watch` 부분을 `the edge of a vintage watch strap` 으로 줄인다.

**같은 문법의 시리즈 (02 · 03 띠 이미지가 필요할 때)**

02 PICTURE — 셔터 위에 멈춘 검지:
```
extreme close-up black and white fine art photograph, an index finger pauses just above the shutter button of a worn black film camera, not yet pressing, the camera body and hand stretch horizontally across the frame, the finger and shutter sit at the right third, a single hard raking light grazes from the upper right, knurled metal, leatherette and skin texture sharply visible, everything else falls into deep black, anonymous, no face, the held breath before a photograph, editorial photography, silver gelatin print, high contrast, fine grain --ar 10:3 --style raw --v 7 --s 75 --no text, logo, brand name, color, ring, tattoo
```

03 ARCHITECTURE — 문틀을 짚은 손과 그 너머의 빛:
```
black and white fine art photograph, a hand rests on the edge of a raw board-formed concrete door frame at the left of the frame, paused at the threshold, beyond the opening an empty quiet room where a single shaft of hard daylight falls across the floor at the right third, deep black shadow everywhere else, concrete texture sharply visible, anonymous, no face, the moment before stepping in, architectural editorial photography, silver gelatin print, high contrast, fine grain --ar 10:3 --style raw --v 7 --s 75 --no text, logo, color, furniture, people, ring, tattoo
```

아래 A–D 는 이 샷을 정하기 전에 검토한 안이다.

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
