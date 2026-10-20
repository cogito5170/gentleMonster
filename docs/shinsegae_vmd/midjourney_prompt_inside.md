# FROM THE INSIDE — 미드저니 프롬프트 (커버)

생성 도구는 미드저니다 (2026-10-20 정정). 무대는 백화점 실내다.
참고 장면은 서점 안에서 유리 너머 손님을 보는 영화 스틸이고, 구도와 빛만 빌린다.

## 방향 (2026-10-20 재설정)

'극장 · 강물 · 돌 · 불이 들어온 신호' 비유는 철회한다. 스토리에 없는 뜻을 더했기 때문이다.
특히 '진열이 맞았다는 신호'는 판정이고, 스토리는 판정이 아니라 **관찰**이다.

원칙은 이렇다. **스토리 문장이 곧 화면 지시서다. 문장에 있는 것만 그리고, 문장에 없는 것은 뺀다.**

### 기준 문장

> 사람들은 쇼윈도를 밖에서 본다. 나는 안에서 본다. 안에서 보면 가게 이름은 거꾸로 읽히고, 진열은 등을 보인다.
> 대신 유리 너머로 사람들의 얼굴이 보인다. 대부분은 그냥 지나간다. 가끔 누군가 걸음을 멈추고, 들여다보고, 웃는다.
> 나는 그 사람이 무엇을 보고 웃었는지 본다. 상품의 진열에만 신경쓰느라 밖에서 안만 바라보는 것이 아니라,
> 사람들의 표정과 반응을 살피기 위해 안에서 밖으로 쳐다보는 VMD가 되겠다.

### 한 장의 구조: 유리 위에서 엇갈리는 두 시선

- **그 사람의 시선 (밖 → 안):** 진열을 들여다본다. 그 끝에 진열품 하나가 있다.
- **나의 시선 (안 → 밖) = 카메라:** 그 사람의 얼굴을 본다.

마지막 문장 "밖에서 안만 바라보는 것이 아니라 안에서 밖으로"를 그대로 그림으로 옮긴 것이다.
그래서 초점은 진열이 아니라 **얼굴**에 둔다. 진열은 어둡고 등을 보인다.

### 문장 → 화면

| 문장 | 지금 이미지 | 방향 |
|---|---|---|
| 나는 안에서 본다 | 안쪽이 어둡다 | 유지 |
| 가게 이름은 거꾸로 읽히고 | 'ƎЯ' 조각뿐이라 안에서 본 유리인지 모른다 | **강조.** 뒤집힌 이름을 유리 위쪽에 또렷하게. 후보정에서 좌우반전해 얹는다 |
| 진열은 등을 보인다 | 아래 띠가 계산대나 난간처럼 보인다 | **강조.** 진열이라고 읽히게. 마네킹의 등과 어깨, 진열대의 뒷면을 실루엣으로 |
| 유리 너머로 사람들의 얼굴이 보인다 | 밝은 실내 통로, 흐린 사람들 | 유지 |
| 대부분은 그냥 지나간다 | 사람들이 흐리지만 서 있는 것처럼 보인다 | 걷는 방향으로 번지게 |
| 걸음을 멈추고, 들여다보고, 웃는다 | 멈추고 웃지만 카메라를 본다 | **고침.** 진열 쪽으로 몸을 기울여 들여다본다. 시선은 카메라가 아니라 진열로 |
| 무엇을 보고 웃었는지 본다 | 빨간 점이 떠 있는 불빛 같다 | **고침.** 빨강은 불빛이 아니라 그 사람이 보는 진열품 하나. 예: 마네킹 어깨에 걸린 빨간 스카프 끝 |
| 안에서 밖으로 쳐다보는 VMD | — | 나는 그리지 않는다. 카메라가 나의 눈이다 |

### 우선순위

1. **시선:** 카메라를 보면 "그 사람이 나를 본다"가 되어 스토리가 뒤집힌다. 가장 먼저 고친다.
2. **진열의 등:** 마네킹 실루엣 하나만 있어도 "쇼윈도 안쪽"이 바로 읽힌다.
3. **거꾸로 읽히는 이름:** 안에서 본 유리라는 증거다.

## 프롬프트 — 새로 생성

```
view from inside a department store display window looking out through the glass, the shop name painted on the glass reads backwards, in the dark foreground the back of a mannequin and the backs of display stands in silhouette, a red scarf end hanging from the mannequin's shoulder, beyond the glass a bright indoor department store aisle, passers-by walking past in motion blur, one woman has stopped, leaning toward the window, looking into the display at the red scarf, gentle smile, her face in sharp focus, black and white with the red scarf as the only colour, 35mm film grain, cinematic, minimal --ar 297:210 --style raw --stylize 100 --no street, people reflected in glass, logo
```

## 지금 이미지 고치기 (에디터 · Vary Region)

- **얼굴과 눈:** `woman leaning toward the window, looking down into the display, gentle smile, face in sharp focus`
- **아래 검은 띠 왼쪽:** `back of a mannequin's shoulders in dark silhouette, seen from inside the window`
- **빨간 점 자리 (마네킹 어깨 쪽으로):** `a red scarf end hanging from the mannequin's shoulder, matte, not glowing`
- **왼쪽 행인들:** `passers-by walking past, motion blur in the walking direction`
- **글자:** 유리의 'ƎЯ' 는 `plain bright glass` 로 지우고, 이름은 후보정에서 좌우반전해 얹는다.
- **이미지 프롬프트로 다시 뽑기:** 이미지 URL 을 앞에 두고 위 프롬프트를 붙인다. `--iw 1.0~1.5`.

## 표지 글자

스토리의 문장을 그대로 쓴다. 새 문구를 만들지 않는다.

- **유리 위:** 뒤집힌 이름 (`JEONG HYEOKJU`).
- **아래 검정 띠:** `사람들은 쇼윈도를 밖에서 본다. 나는 안에서 본다.` 와 `FROM THE INSIDE — VISUAL MERCHANDISER`.

## 매개변수

- `--ar 297:210`: A4 가로.
- `--style raw` · `--stylize 100`: 꾸밈을 줄이고 지시를 따르게.
- `--no`: 빼고 싶은 것. 글자가 남으면 에디터로 지운다.
- `--sref <커버 URL>`: 커버가 정해지면 다른 페이지 이미지의 톤을 맞춘다.

## 주의

- 영화 스틸을 이미지 프롬프트로 쓰면 배우나 서점이 닮게 나올 수 있다. 구도만 참고하고, 닮게 나오면 버린다.
- 생성된 인물은 가상 인물이다. 포트폴리오에는 AI 생성 이미지라고 표기한다.

## 웃는 사람을 '특정 인물'에서 '누군가'로 (2026-10-20)

스토리는 "가끔 **누군가** 걸음을 멈추고 … 웃는다"이다. 그 사람이 누구인지는 중요하지 않고, 어떻게 반응했는지가 중요하다.
그래서 **정체(누구)는 지우고 반응(미소)은 남긴다.** 얼굴 없는 초상처럼 얼굴 전체를 지우면 미소도 사라진다.
"표정과 반응을 살핀다"는 문장과 부딪치므로, 그 방식은 웃는 사람에게는 쓰지 않는다.

### 방법 비교

| 방법 | 지우는 것 | 남는 것 | 판단 |
|---|---|---|---|
| A. 거꾸로 된 가게 이름이 눈을 가린다 | 눈 (정체) | 입가의 미소 | **권장.** 스토리에 이미 있는 요소가 얼굴을 가린다 |
| B. 지나가는 사람만 얼굴 없이 | 행인의 얼굴 | 멈춘 한 사람의 미소 | **권장 (A와 함께).** 지나가는 사람은 반응이 없으니 얼굴도 없다 |
| C. 성별 · 나이를 흐리게 | 앞머리 · 화장 · 긴 웨이브 머리 | 중립적인 실루엣 | **권장 (A와 함께).** 단발 또는 묶은 머리, 무채색 코트 |
| D. 얼굴을 매끈하게 지우고 미소만 | 이목구비 | 미소 | 강렬하지만 섬뜩하게 읽힐 위험 |
| E. 역광 실루엣 | 얼굴 전체 | 윤곽 | 미소가 읽히지 않아 스토리가 약해진다 |
| F. 여러 사람의 얼굴을 겹친 다중노출 | 한 사람 | '누구나' | 개념은 좋으나 커버에서 복잡해진다 |

### 수정 방향 (A + B + C)

1. **눈 높이에 거꾸로 된 이름:** 유리의 뒤집힌 글자 띠를 그 사람의 눈 높이로 내린다.
   글자가 눈을 가리고 입가의 미소만 보인다. 후보정에서 글자 레이어로 얹으면 위치가 정확하다.
   지금 유리에는 'SHOP NAME' 이 그대로 쓰여 있으니 반드시 이름으로 바꾼다.
2. **행인은 얼굴 없이:** 뒤의 사람들은 이목구비가 없는 매끈한 얼굴로, 걷는 방향으로 흐리게.
3. **중립적인 인물:** 앞머리 · 화장 · 긴 웨이브 머리를 뺀다. 무채색 코트를 입고, 흰 목도리도 뺀다 (빨간 스카프와 겹친다).
4. **크기를 줄인다:** 지금은 그 사람이 커서 인물 사진처럼 읽힌다. 화면의 1/4 정도로 줄이고 진열(마네킹)이 앞에 오게.
5. **앞의 검은 울타리를 뺀다:** 진열이 아니라 난간으로 읽힌다. 진열대 뒷면이나 빈 어둠으로 바꾼다.
6. **유지:** 마네킹의 등, 빨간 스카프, 진열을 향한 시선, 흑백에 빨강 한 점.

### 미드저니

새로 생성:

```
view from inside a department store display window, the back of a dark mannequin with a red scarf in the foreground, backwards lettering on the glass running across at eye level, beyond the glass a bright indoor aisle, faceless passers-by with smooth blank faces walking past in motion blur, one androgynous person in a plain dark coat with short hair has stopped, leaning toward the window, their eyes hidden behind the backwards lettering, only a faint smile visible, looking at the red scarf, black and white with the red scarf as the only colour, 35mm film grain, minimal --ar 297:210 --style raw --stylize 100 --no makeup, jewelry, street, logo, fence
```

지금 이미지 에디터 (Vary Region):

- **인물 머리와 상체:** `androgynous person with short hair in a plain dark coat, leaning toward the window, faint smile`
- **뒤의 행인들:** `faceless passers-by with smooth blank faces, motion blur`
- **검은 울타리:** `dark empty display interior`
- **흰 목도리:** `plain dark coat collar`
- 눈을 가리는 글자 띠는 후보정에서 좌우반전한 이름 레이어로 얹는다.

## 기존 이미지 수정 프롬프트 (미드저니 에디터, 2026-10-20)

청사진: `docs/shinsegae_vmd/edit_blueprint/cover_edit_blueprint.pdf` · 원본: `edit_blueprint/source_midjourney.jpg`.
도구: 미드저니 웹 Editor → 이미지 업로드 → 영역 지우기(선택) → 프롬프트 교체 → Submit. Discord 라면 Vary (Region).

영역 프롬프트는 장면 전체를 짧게 앞에 두고 바꿀 내용을 뒤에 붙인다. 영역 밖과 톤이 맞는다.

공통 앞부분:

```
view from inside a department store display window, black and white film photograph, the red scarf on the mannequin is the only colour, 35mm grain,
```

| # | 영역 | 뒤에 붙일 내용 |
|---|---|---|
| 1 | 앞의 검은 울타리 | `dark empty display interior seen from behind, soft shadow, no railing --no fence` |
| 2 | 인물의 흰 목도리 | `plain dark wool coat collar, no scarf --no white scarf` |
| 3 | 뒤의 행인 (좌 · 우 두 번) | `faceless passers-by with smooth blank faces, walking past, long motion blur` |
| 4 | 유리 위 'SHOP NAME' | `plain bright glass, soft blurred lights of the indoor aisle --no text, letters` |
| 5 | 인물 머리 · 얼굴 · 어깨 | `androgynous person with short dark hair in a plain dark coat, no makeup, leaning toward the window, looking down at the red scarf, faint smile --no makeup, long hair, bangs, earrings` |
| 6 | (선택) Zoom Out 1.5× | 인물 사진처럼 읽히면 쓴다. 유리와 통로의 여백이 늘고 인물이 작아진다 |
| 7 | 후보정 | 좌우반전한 `JEONG HYEOKJU` 를 눈 높이(위에서 약 30%)에. 마네킹 뒤로 마스크, 불투명도 70%, 흐림 1px. 커브로 검정을 누르고 통로를 밝힌다 |

순서: 배경 → 소품 → 인물. 인물(5)은 가장 많이 다시 뽑으므로 마지막에 한다.
5에서 영역은 머리카락 끝까지 넉넉히 잡는다. 좁게 잡으면 긴 머리가 남는다.
이름(7)은 생성하지 않는다. 미드저니는 글자를 깨뜨린다.

## 유리 글자만 'HYEOK JU' 로 바꾸기 (2026-10-20)

미드저니는 뒤집힌 글자를 잘 못 쓴다. 그래서 이미지를 좌우반전해 글자가 바로 읽히게 만든 뒤 고치고, 다시 뒤집는다.

1. 이미지를 좌우반전한다. 유리 글자가 `SHOP NAME` 으로 바로 읽힌다.
2. 미드저니 Editor 에 올리고 **글자 띠만** 칠한다 (위쪽 약 16%). 마네킹 머리와 인물의 머리카락에 닿지 않게 한다.
3. 프롬프트:
   ```
   large semi-transparent warm beige vinyl lettering "HYEOK JU" on the shop window glass, same bold rounded sans-serif font, same size, colour and position as the original lettering, bright blurred department store aisle lights behind the glass, film grain --style raw
   ```
4. 철자가 맞는 결과가 나올 때까지 다시 뽑는다.
5. 다시 좌우반전한다. 안에서 보면 거꾸로 읽히는 `HYEOK JU` 가 된다.

확실한 대안은 포토샵이다. 생성형 채우기로 글자를 지우고 비슷한 글꼴로 `HYEOK JU` 를 쓴 뒤 좌우반전한다.
색은 원래 글자에서 스포이트로 따고, 불투명도 60~70%, 흐림 0.5~1px, 노이즈를 조금 넣어 그레인을 맞춘다.
