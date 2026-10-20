# FROM THE INSIDE — 미드저니 프롬프트 (추상 · 컨셉 · 커버)

2026-10-20 정정: 생성 도구는 Gemini 가 아니라 미드저니다. 미드저니는 대화로 고치지 않으므로
수정은 이미지 프롬프트 · 에디터(Vary Region) · 후보정으로 나눈다.

참고 장면: 서점 안에서 유리 너머 손님을 보는 영화 스틸. 구도와 빛만 빌린다. 무대는 백화점 실내다.

## 커버 스토리 ('컨셉적 · 강렬한'을 직관적인 말로)

- **컨셉적이다:** 설명 없이 한 문장으로 읽힌다. "나는 안에 있고, 밖에서 한 사람이 웃는다."
- **강렬하다:** 대비가 한 점에 모인다. 어둠과 빛, 흐림과 선명, 무채색과 빨강이 얼굴과 빨간 점에서 만난다.

불 꺼진 진열창 안은 극장 객석이다. 유리 밖은 스크린처럼 밝고, 사람들은 강물처럼 흘러간다.
한 사람이 돌처럼 멈춘다. 그 사람이 웃는 순간 진열 위 빨간 점 하나에 불이 들어온다. 진열이 맞았다는 신호다.
나는 그 장면을 객석에서 본다.

| 말 | 바꿀 것 |
|---|---|
| 극장 | 안은 완전한 검정, 밝은 띠는 얇고 하얗게 |
| 강물 | 지나가는 사람은 가로로 길게 번져 형체가 없다 |
| 돌 | 멈춘 한 사람만 선명, 얼굴에 역광 |
| 불이 들어온 점 | 그 사람의 시선이 닿는 자리. 카메라가 아니라 점을 본다 |
| 거꾸로 읽히는 이름 | 생성하지 않고 편집 프로그램에서 좌우반전해 얹는다 |

## A안 — 새로 생성 (권장)

```
view from inside a dark shop display window looking out through the glass, foreground pure black, backs of display pieces as blunt featureless silhouettes, a thin bright white band of an indoor department store aisle beyond the glass like a cinema screen, passers-by dissolved into long horizontal motion blur streaks, one woman stopped and sharp, soft rim light on her face, faint private smile, eyes looking down at a single small glowing red light in the dark display, black and white with one red accent, 35mm film grain, cinematic, minimal, vast negative space --ar 297:210 --style raw --stylize 100 --no text, letters, logo, street, people reflected in glass
```

## B안 — 더 추상

```
abstract minimal composition, a sheet of glass seen from a dark interior, below pure black with blunt shapes seen from behind, beyond a pale luminous band of light, people as vertical columns of blurred light passing by, one column stopped and becoming a woman with a faint smile, a tiny red glow where her gaze lands, the only colour in the frame, monochrome, fine film grain, gallery photograph, quiet and poetic --ar 297:210 --style raw --stylize 250 --no text, letters, logo, street
```

## 지금 이미지를 커버로 다듬기

1. **이미지 프롬프트로 다시 뽑기:** 이미지를 올리고 그 URL 을 맨 앞에 둔 뒤 A안을 붙인다.
   `--iw 1.5` 는 구도를 많이 지키고 `--iw 0.8` 은 새로 많이 바꾼다.
2. **에디터 (Vary Region) 로 부분 고치기:** 영역을 고르고 그 영역의 프롬프트만 바꾼다.
   - 얼굴 · 눈: `woman looking down toward a small glowing red light, faint smile, rim light on her face`
   - 지금 빨간 점 자리: `plain dark display surface`
   - 그 사람 시선 아래의 진열 자리: `a single small soft glowing red light`
   - 왼쪽 행인들: `long horizontal motion blur streaks of passers-by, no shapes`
   - 유리 글자 'ƎЯ': `plain bright blurred glass`
3. **후보정 (Lightroom · 포토샵):** 검정을 완전한 검정으로 누르고 밝은 띠를 하얗게 올린다. 커브 하나로 충분하다.
   미드저니로 하는 것보다 정확하다.
4. **글자:** 뒤집힌 이름을 밝은 띠 위에 가늘게 얹는다. 바로 읽히는 제목은 아래 검정 띠에 작게 둔다.
   예: `FROM THE INSIDE — JEONG HYEOKJU, VISUAL MERCHANDISER`

## 매개변수

- `--ar 297:210`: A4 가로.
- `--style raw`: 미드저니 특유의 꾸밈을 줄이고 프롬프트에 가깝게.
- `--stylize`: 낮을수록 지시를 따르고 높을수록 미드저니가 해석한다. A안 100, B안 250.
- `--no`: 빼고 싶은 것. 글자는 완전히 막히지 않으니 남으면 에디터로 지운다.
- `--sref <커버 URL>`: 커버가 정해지면 다른 페이지 이미지에도 붙여 톤을 맞춘다.
- `--chaos 20`: 네 장의 차이를 키우고 싶을 때.

## 주의

- 영화 스틸을 이미지 프롬프트로 쓰면 배우나 서점이 닮게 나올 수 있다. 구도만 참고하고, 닮게 나오면 버린다.
- 생성된 인물은 가상 인물이다. 포트폴리오에는 AI 생성 이미지라고 표기한다.
