# 신세계 VMD 포트폴리오 — 커버 컨셉 이미지 (미드저니 프롬프트)

작성일: 2026-10-15. 프롬프트는 영어로 쓴다(미드저니는 영어 프롬프트를 가장 잘 따른다). 뜻은 각 프롬프트 아래 우리말로 적었다.

## 컨셉: VMD 는 사람을 멈추게 하는 일이다

젠틀몬스터 포트폴리오(SPA)의 동사는 **멈춘다**였다. VMD 에서는 이 말이 비유가 아니라 직무 그 자체다.
쇼윈도의 일은 지나가던 사람의 발걸음을 멈추게 하는 것이다.

> 커버 한 줄 후보: **"I design the reason you stop."** — 나는 당신이 멈추는 이유를 만든다.
> 질문은 SPA 커버와 같게 이어 간다: **"Where did you last stop?"**

그래서 세 안 모두 **쇼윈도 앞에 멈춘 한 사람**을 그린다. 사람은 작게 둔다. Sony 우승작 분석의 "사람이 장소에 크기와 의미를 준다"와 같은 문법이다.

## 공통 규칙

- **이미지 안에 글자 · 로고를 넣지 않는다.** 미드저니는 글자를 뭉개고, 신세계 로고를 그리게 하면 가짜 로고가 된다. 제목 · 로고 · 이름은 인디자인이나 피그마에서 얹는다. 모든 프롬프트에 `--no text, letters, logo, signage, watermark` 를 붙였다.
- **제목 자리를 비운다.** 위쪽 1/3 을 어두운 하늘이나 무지 벽으로 비우게 했다(`negative space in the upper third`).
- **비율은 A4 세로**: `--ar 210:297`. 가로 펼침이면 `--ar 297:210`.
- **내 사진으로 톤을 맞춘다.** 커버의 밤 · 빨간불 사진(또는 다른 내 사진)을 미드저니에 올리고 `--sref <이미지 URL>` 을 붙이면, 생성 이미지가 내 사진의 색과 빛을 따라간다. 포트폴리오 안의 사진과 커버가 한 사람의 눈으로 보인다.
- **버전**: 2026년 10월 기준 V8 계열로 보인다(공식 문서로는 확인 못 함). 웹 설정의 기본 버전을 쓰고 `--v` 는 붙이지 않았다. 사진처럼 담백하게 하려면 Raw 모드를 켠다. 버전에 따라 `--style raw` 또는 `--raw` 다.
- **포트폴리오에 표기**: 커버 안쪽이나 판권 자리에 *"Cover concept image generated with Midjourney, prompt and art direction by Jeong Hyeokju"* 처럼 적는다. 면접에서 물으면 프롬프트와 고른 이유를 설명할 수 있어야 한다.

## A안 · 밤의 쇼윈도 (The Window) — 추천

석조 고전 건물의 쇼윈도 하나만 불이 켜져 있다. 비에 젖은 보도 위에 한 사람이 멈춰 서 있고, 유리에는 도시의 불빛이 비친다.
명동 본점 같은 고전 석조 건물을 떠올리게 하되, 실제 건물이나 로고는 그리지 않는다.

```
a single illuminated department store display window set into a classical stone facade at night, inside the window a minimal sculptural installation of folded red fabric and one pedestal under a warm spotlight, wet pavement reflecting the window light, one small solitary passerby standing still in front of the glass seen from behind, faint reflections of city lights on the glass, quiet empty street, deep navy sky, negative space in the upper third, cinematic street photography, 35mm film, Fujifilm color, soft grain, editorial magazine cover composition --ar 210:297 --s 150 --no text, letters, logo, signage, watermark
```

뜻: 밤, 고전 석조 파사드의 쇼윈도 하나. 안에는 접힌 빨간 천과 받침대 하나뿐인 설치물이 따뜻한 스포트라이트를 받는다. 젖은 보도에 창의 빛이 비치고, 작은 사람 하나가 뒷모습으로 유리 앞에 멈춰 있다. 위쪽 1/3 은 비운다.

변형:
- 빨간색을 커버 사진(빨간불)과 맞춘다: `folded red fabric` 은 그대로 두고 `red traffic light glow at the edge of the frame` 을 더한다.
- 계절(겨울 · 크리스마스 시즌) 판: `inside the window` 뒤를 `a single oversized white paper star suspended in the air` 로 바꾸고 `light snowfall` 을 더한다.

## B안 · 유리 위의 겹침 (Reflection)

쇼윈도 유리를 가까이에서 찍는다. 안쪽 연출(정물처럼 놓인 소품)과 유리에 비친 행인의 모습이 한 장에 겹친다.
"보는 사람이 연출의 일부가 된다" — VMD 의 세 겹(유리 · 소품 · 빛)을 한 장으로 보여 준다.

```
close-up through a department store display window glass, inside a carefully composed still life of a single chair, a vase with one branch, and a folded garment on a plinth, arranged like a gallery installation, warm and precise lighting, on the glass surface a soft reflection of a person who has stopped to look, layered reflections of the street, shallow depth of field, muted beige and charcoal palette with one red accent, quiet and contemplative, editorial still life photography, medium format, negative space in the upper third --ar 210:297 --s 200 --no text, letters, logo, signage, watermark
```

뜻: 유리 너머 안쪽에는 의자 하나, 가지 하나 꽂힌 화병, 받침대 위에 접힌 옷이 전시처럼 놓여 있다. 유리 표면에는 멈춰서 들여다보는 사람이 은은하게 비친다. 베이지 · 차콜에 빨간 강조 하나.

변형:
- 사람을 더 분명히: `soft reflection of a person` → `clear reflection of a young person in a dark coat, face not visible`.
- 흑백 판: 색 문장을 `black and white, high contrast, silver gelatin print` 로 바꾼다.

## C안 · 쇼윈도 모형 (Maquette)

책상 위의 백화점 쇼윈도 건축 모형. 아주 작은 사람 모형 하나가 창 앞에 멈춰 있다.
공간 디자인을 하는 사람이라는 것을 커버에서 바로 보여 준다. 03 ARCHITECTURE(공간)와 이어진다.

```
architectural scale model of a department store facade with three display windows, made of white card, frosted acrylic and thin brass, one window lit from inside with a warm glow, a single tiny human figurine standing still in front of the lit window, placed on a dark matte table, soft studio light from one side, long gentle shadows, macro photography, shallow depth of field, minimal and precise, design studio atmosphere, negative space in the upper third --ar 210:297 --s 120 --no text, letters, logo, signage, watermark
```

뜻: 흰 카드지 · 반투명 아크릴 · 얇은 황동으로 만든 쇼윈도 세 개짜리 파사드 모형. 창 하나만 안에서 불이 켜져 있고, 그 앞에 작은 사람 모형 하나가 멈춰 있다. 어두운 무광 책상, 옆에서 오는 스튜디오 조명.

변형:
- 위에서 내려다보기: `macro photography` 앞에 `top-down view` 를 더한다(2025 Sony 건축 1위처럼 시점을 바꾼다).
- 실제로 모형을 만들어 직접 찍으면 더 강하다. 생성 이미지는 시안으로 쓰고, 최종 커버는 내 손으로 만든 모형 사진으로 바꾸는 길도 있다.

## 만드는 순서

1. A · B · C 를 한 번씩 돌린다(각 4장).
2. 마음에 드는 한 장을 **Vary (Subtle)** 로 다듬는다.
3. 유리에 생긴 이상한 글자 · 간판은 **Vary Region** 으로 그 부분만 지우고 다시 그린다. 프롬프트는 `clean glass, no signage` 로 둔다.
4. **Upscale** 한다. 인쇄용 A4(300dpi)는 긴 변 3,508px 이 필요하다. 업스케일 뒤에도 모자라면 인쇄 크기를 줄이거나 화면용으로만 쓴다.
5. 인디자인 · 피그마에서 위쪽 빈자리에 제목을 얹는다.

```
JEONG HYEOKJU                         VMD PORTFOLIO
I design the reason you stop.
                                      "Where did you last stop?"
```

신세계 이름을 넣는다면 "for SHINSEGAE" 정도로 텍스트만 쓰고, 로고 이미지는 쓰지 않는다.

## 출처

- 미드저니 V8 계열 파라미터(제3자 문서, 공식 문서 아님): [evolink.ai V8.2 가이드](https://evolink.ai/docs/en/api-manual/image-series/midjourney/midjourney-v8-2-prompt-guide.md) · [V8.1 가이드](https://docs.evolink.ai/en/api-manual/image-series/midjourney/midjourney-v8-1-prompt-guide)
