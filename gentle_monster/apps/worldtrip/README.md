# World Trip — 화면

[worldTrip](https://github.com/cogito5170/worldTrip) 엔진(세계여행 계획)의 프론트엔드. 엔진은 계산과 판정을, 이 폴더는
**어떻게 보이는가** 를 맡는다. gentle_monster 의 잡지 문법을 그대로 쓴다: 종이 · 잉크 · 머리카락 선 · 자간 넓은 대문자
캡션 · 격자로 잘린 스텐실 마스트헤드 · 하나의 뜨거운 강조색(GM red). **청사진**은 `documents.blueprint_pdf` 의 A3 가로
도면(평면 | 렌더 | 표제란)을 여행으로 옮겼다: 경로 평면 | 날짜 시퀀스 | 표제란·예산 프로그램. 화면에서 보고 PDF 로 인쇄한다.

빌드가 없다. 정적 파일 여섯 개(`index.html` · `app.css` · `app.js` · `manifest.webmanifest` · `sw.js` · `icon.svg`)이고,
설치 가능한 PWA 다(서비스 워커는 껍데기만 캐시하고 판정 `/api` 는 절대 캐시하지 않는다).

## 엔진에 붙이기

```bash
# 엔진 쪽에서 -- 이 폴더를 받아 와서 붙이고 브라우저를 연다
pip install git+https://github.com/cogito5170/worldTrip   # 또는 그 저장소에서
worldtrip app
# 이 저장소를 이미 받아 두었으면
worldtrip app --frontend gentle_monster/apps/worldtrip
```

다른 곳(예: GitHub Pages)에 올린 화면이 엔진을 부르게 하려면 엔진 주소를 준다:
`index.html?api=https://엔진주소` 또는 `<meta name="worldtrip-api" content="https://...">`. 그 엔진은
`WORLDTRIP_ALLOWED_ORIGINS` 에 이 화면의 출처를 넣어야 한다(CORS). 엔진에 못 닿으면 화면이 그렇게 말하고 주소를 묻는다.

## 무엇을 지키나 — 엔진 심판의 V 를 이 앱에

`python3 -m gentle_monster.apps.check` 가 `engine/judge.py` 의 측정 코드를 **결과가 다 그려진 화면**에 건다.
계획 ACCEPT · 거절 REJECT · 탐색 세 상태 × 375 · 1440 px. 넘침 · 대비(렌더된 색) · 폰 최소 글자 12 px ·
외부 요청 0 · JS 오류 0 · 접근 가능한 이름 · 제목 순서 · reduced-motion · 무게.

그래서 이 앱은 웹 글꼴을 불러오지 않는다(Archivo 는 깔려 있을 때만 쓰고, 아니면 대체 글꼴). 그래서 캡션이 12 px 이다.

엔진 없이 돌 때는 `tests/fixtures/worldtrip/` 의 응답을 끼운다 -- worldTrip 엔진 0.1.0 이 실제로 낸 것을 적어 둔 것이다.
`tests/test_worldtrip_app.py` 는 그 GREEN 과 함께, 한 가지씩 깨뜨린 화면(외부 글꼴 · 9 px · 옅은 회색 · h1 두 개 ·
JS 오류 · 900 px 상자)이 **바로 그 검사**를 실패하는 RED 여섯 개를 돌린다.

## 이 화면이 하지 않는 것

- 값을 만들지 않는다. 모든 수는 엔진이 낸 것이고, 옆에 확인수준(조각 · 사용자 · 원문)을 단다.
- 식당·후기가 엔진 원장에 없으면 "없다 — 지어내지 않는다" 라고 쓴다.
- 이 검사는 표시하는 값이 **맞는지** 보지 않는다. 그것은 엔진 심판(T0–T7)의 몫이다.
