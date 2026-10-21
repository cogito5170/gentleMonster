# v5 — 얼굴은 보는 사람이 가져온다 (THE FACE IS YOURS)

2026-10-21. 이전 스토리(FROM THE INSIDE)는 두고 새로 쓴다.
출발점은 지원자의 일 자체다. 마네킹에 착장을 조합하는 VMD 이고, 건축으로 공간 감각을 익혔다.
보류했던 얼굴 없는 초상의 개념은 마네킹으로 들어온다. 마네킹은 원래 얼굴 없는 사람이다.

## 한 줄

나는 얼굴 없는 사람을 만든다. 얼굴은 보는 사람이 가져온다.

## 스토리 (공백 포함 255자 · 제외 188자)

마네킹에는 얼굴이 없다. 나는 그 빈자리를 채우지 않는다. 대신 그 아래를 짓는다. 어깨에 맞춰 코트를 고르고,
니트의 결을 맞추고, 스카프 하나로 색을 정한다. 건축이 사람이 들어설 자리를 남겨 두듯, 나는 한 벌의 옷에
사람이 들어설 자리를 남긴다. 그 자리에 얼굴을 넣는 것은 유리 앞에 선 사람이다. 걸음을 멈춘 누군가가 웃는다면,
그는 마네킹이 아니라 그 옷을 입은 자신을 본 것이다. 나는 얼굴 없는 사람을 만든다. 얼굴은 보는 사람이 가져온다.

다짐형으로 끝낼 때: 마지막 두 문장을 "나는 얼굴이 들어설 자리를 짓는 VMD가 되겠다." 로 바꾼다.

## 지원자와의 연결

| 문장 | 지원자 |
|---|---|
| 그 아래를 짓는다 · 코트 · 니트 · 스카프 | 착장을 조합하는 VMD |
| 건축이 사람이 들어설 자리를 남겨 두듯 | 건축으로 익힌 공간 감각 |
| 유리 앞에 선 사람이 얼굴을 넣는다 | 진열의 완성은 손님의 몫이라는 태도 |
| 그 옷을 입은 자신을 본 것이다 | 상품이 아니라 '입은 나'를 파는 진열 |

## 커버 이미지: 강제 원근 한 장

- **장면:** 머리 없는 드레스폼 (지금 이미지의 마네킹). 코트 · 니트 · 빨간 스카프로 조합해 입혔다.
- **결정적 순간:** 유리 밖의 사람이 걸음을 멈춘다. 카메라 위치에서 보면 그 사람의 얼굴이 드레스폼의 빈 목 위에
  정확히 올라온다. 옷을 입은 자신을 본 순간이고, 그 사람이 웃는다.
- **유리:** 뒤집힌 흰 `HYEOK JU` 는 서명으로 남긴다.
- **흑백 + 빨강 한 점, 필름 그레인**은 지금 이미지 그대로.

### 지금 이미지에서 바꿀 것

1. 인물을 드레스폼의 목 위로 옮긴다. 같은 높이, 얼굴이 빈 목에 맞물리게.
2. 드레스폼은 스카프 하나가 아니라 코트 · 니트 · 스카프의 조합으로.
3. 앞의 검은 울타리는 뺀다.
4. 인물은 '누군가'로: 앞머리 · 화장을 빼고 무채색 옷.

### 미드저니 (새로 생성)

```
view from inside a department store display window, a headless dress form in the foreground seen from a three-quarter back angle, styled in a charcoal coat, grey knit and a red scarf, beyond the glass a person has stopped outside and from this viewpoint their smiling face sits exactly on top of the headless form's empty neck, as if they are wearing the outfit, forced perspective, bright indoor aisle, passers-by in motion blur, mirrored white lettering on the glass, cinematic film photograph, cool teal tones, the red scarf is the only strong colour --ar 297:210 --style raw --stylize 100 --no street, fence, makeup
```

미드저니는 얼굴과 목을 정확히 맞추지 못할 수 있다. 실제 촬영이 쉽고 정확하다.
드레스폼 뒤에 삼각대를 두고, 밖의 사람이 얼굴이 목 위에 올 때까지 움직이면 된다.

## 주의

- 생성된 인물은 가상 인물이다. 포트폴리오에는 AI 생성 이미지라고 표기한다.

## 청사진 (2026-10-21)

`docs/shinsegae_vmd/blueprint/the_face_is_yours_blueprint.pdf` (`node tools/face_blueprint/build.mjs`).
이미지는 Codex `.relay/tasks/010-the-face-is-yours-cues`. 첫 결과 009 는 실제 사람이 뒤돌아본 사진으로 읽혀서 쓰지 않았다.
착시의 단서로 드레스폼의 지지대 · 받침 · 빈 목 테두리, 바깥 사람의 베이지 코트 어깨를 넣었다.

촬영 값: 카메라 → 드레스폼 4.0 m, 드레스폼 → 얼굴 1.2 m, 렌즈 높이 1.49 m, XF56mm f/5.6, 초점 4.6 m, 1/30 s, 삼각대.
바깥 사람의 머리는 드레스폼 위 머리의 0.77배로 보인다. 카메라가 멀수록 1에 가까워진다.
