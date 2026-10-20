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
