# worldplan — 화면

[worldplan](https://github.com/cogito5170/worldplan) 엔진(여러 시간대 회의 배치 · 판정)의 프론트엔드. 엔진은 계산과 판정을,
이 폴더는 **어떻게 보이는가** 를 맡는다. worldTrip 과 같은 갈래다 — 화면은 여기 한 벌뿐이고, 엔진이 받아 가서 붙인다.

빌드가 없다. 정적 파일(`index.html` · `app.css` · `app.js` · `tokens.css` · `tokens.json`).
색 · 글자 크기 · 간격은 이 저장소의 엔진이 지었다: `python3 -m gentle_monster.apps.worldplan_tokens` → `tokens.css`(CSS 변수) ·
`tokens.json`(W3C DTCG). 손으로 고치지 않는다 — `tests/test_worldplan_app.py` 가 엔진이 지금 짓는 값과 같은지 본다.

## 엔진에 붙이기

```bash
pip install git+https://github.com/cogito5170/worldplan
worldplan app                                   # 이 폴더를 받아(처음 한 번) 붙이고 브라우저를 연다
worldplan app --frontend gentle_monster/apps/worldplan   # 이 저장소를 이미 받아 두었으면
```

엔진 주소는 같은 출처가 기본이다. 바꾸려면 `index.html?api=http://엔진주소` 또는 `<meta name="worldplan-api">`.

## 화면

- **요청 짓기** — 사람(시간대 · 일하는 시간 · 선호 시간) · 일정(길이 · 필수/선택 · 선후) · 기간. 폼과 요청 JSON 은 한 벌이다
- **판정** — 엔진 심판의 ACCEPT/REJECT, 비용, 시간축, 참가자별 현지 시각, 이 판정이 무효가 되는 조건, 심판이 재지 않은 것
- **물어보기** — 엔진의 `/api/assistant`. 시각 변환은 앞단이 바로, 나머지는 엔진에 설정된 LLM(Claude 또는 Gemini)이 worldplan 도구로
- 위에는 요청 속 사람들의 시간대 시계(브라우저 안에서)

## 무엇을 지키나 — 엔진 심판의 V 를 이 앱에

`python3 -m gentle_monster.apps.check --app worldplan` 이 worldtrip 과 **같은 판정 함수**로 잰다.
계획 ACCEPT · 거절 REJECT · 물어보기 답 세 상태 × 375 · 1440 px. 넘침 · 대비(렌더된 색) · 폰 최소 글자 12 px ·
외부 요청 0 · JS 오류 0 · 접근 가능한 이름 · 제목 순서 · reduced-motion · 무게 · 결과가 실제로 그려졌나.

이 검사가 처음 잡은 결함: 폰(375 px)에서 계획 표가 옆으로 밀려 '비고' 칸이 화면 밖 1,093 px 까지 나갔다
(한 장짜리 정적 검사로는 결과 표가 없어서 안 보였다). 지금은 폰에서 표를 칸 이름이 붙은 카드로 편다.
`tests/test_worldplan_app.py` 의 RED 여섯이 깨뜨린 화면마다 **바로 그 검사**가 실패하는지 본다.

## 이 화면이 하지 않는 것

- 값을 만들지 않는다. 계획 · 비용 · 판정은 전부 엔진의 것이다.
- 웹 글꼴을 부르지 않는다(Archivo 는 깔려 있을 때만, 아니면 대체 글꼴).
