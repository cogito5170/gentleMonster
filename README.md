# gentleMonster
frontEnd Design

공간 디자인 파이프라인 `gentle_monster` — 브리프 한 줄에서 공간 시놉시스, 레이아웃 PDF, 잡지형 무드보드 PDF를 만들고,
요청하면 청사진(A3 도면·실사 렌더)과 동선을 따라 걷는 30초 MP4까지 만든다.

```
<시놉시스>  →  <레이아웃 PDF + 무드보드 PDF>   기본
            →  <청사진 PDF + MP4>             요청할 때만 (영상은 수십 분)
            →  <웹 페이지>                    요청할 때만: frontend engine (1분 안팎)
```

## 설치

```bash
pip install -r requirements.txt
python -m playwright install chromium
export GEMINI_API_KEY=...        # 시놉시스 생성(make)에만 필요. example 은 키 없이 돈다
```

## 쓰기

```bash
python3 -m gentle_monster example gm                       # 번들 시놉시스(gm·tb·ac·ae)로 레이아웃 + 무드보드. 모델 호출 없음
python3 -m gentle_monster make "비 오는 밤의 문턱을 주제로 한 성수 플래그십" --image photos/1.jpg --image photos/ref.png
python3 -m gentle_monster moodboard <작업> --image photos/*.jpg   # 있는 작업의 무드보드를 새 사진·레퍼런스로 다시
python3 -m gentle_monster blueprint <작업> [--then-video]          # 요청 시: 실사 렌더 + A3 도면 PDF
python3 -m gentle_monster video <작업>                             # 요청 시: 30초 1인칭 MP4
python3 -m gentle_monster site <작업> [--rounds 6]                 # 요청 시: 웹 페이지 (frontend engine)
python3 -m gentle_monster list · status <작업> · check <job.json>
```

- 결과물은 `out/<작업>/` 에 쌓인다(git 에 안 들어간다): `job.json` · `synopsis.md` · `layout.pdf` · `moodboard.pdf` · `blueprint.pdf` · `render_*.png` · `*.mp4`.
- 사진과 레퍼런스 레이아웃은 `photos/` 에 둔다. 다른 폴더를 쓰려면 `GENTLE_MONSTER_PHOTO_DIRS` 에 적는다.
- `--image` 는 섞여 있어도 된다. 8x8 블록 중 평평한 것의 비율을 **재서** 사진과 레퍼런스를 가른다
  (실측: 사진 0.000–0.001, 잡지 보드 캡처 0.324, 문턱 0.12). 파일 이름에 `ref`·`참고`·`레퍼런스` 가 있으면 레퍼런스다.

## 무드보드가 정해지는 방식

1. **양식** — 레퍼런스의 종이색·여백 비율·그림 비율을 재서 종이·여백·밀도를 정한다. Gemini 키가 있으면 레퍼런스를
   보고 펼침 순서를 읽는다(목록 밖의 펼침 이름이면 버린다).
2. **사진** — 채도×대비×윤곽이 가장 센 사진이 표지, 가장 어둡거나 흑백인 사진이 풀블리드, 가장 밝은 사진이 뒤표지.
3. **빈자리** — 사진이 3장 미만이면 그 공간의 실사 렌더(눈높이·컷어웨이·첫/끝 정지점)로 채우고 "generated" 라 적는다.
   그래도 모자라면 이미 쓴 그림을 디테일 크롭으로 다시 쓴다. 마지막 펼침에 무엇이 일어났는지 적힌다.

## 프론트엔드 엔진 — 방을 웹 페이지로

**스크롤이 곧 동선이다.** 문설주가 갈라지며 들어가고, 평면 위의 동선이 스크롤에 맞춰 그려지고, 세 정지점이 장면이 된다.
job 의 팔레트·조명·재료가 **디자인 토큰**(W3C DTCG 로 내보냄)이 되고, 토큰이 페이지가 된다.

페이지는 **잰 뒤에** 받아들여진다. 심판은 모델이 아니라 Chromium 이다. 375 px 와 1440 px 에서 대비(토큰 계산과
렌더 측정 두 길로) · 넘침 · 최소 글자 · 외부 요청 0 · 접근 가능한 이름 · 제목 순서 · reduced-motion · 무게를 재고(V),
극적 대비 · 위계 · 행 길이 · 여백 · 강조색 비율 · 리듬을 잰다(J).

무엇을 바꿀지는 **se_new 정책**으로 정한다. `ACCEPT ⟺ 같은 내용 ∧ V ∧ 어떤 J 성분도 안 떨어짐 ∧ ΔJ > ε`.
기본은 REJECT, 거절도 원장에 적고, 그 원장이 연산자 무게 π 를 [0.25, 4] 안에서 배운다.
자세한 것 · 만들면서 잡은 거짓 초록 · 이 심판이 못 잡는 것: [`docs/FRONTEND_ENGINE.md`](docs/FRONTEND_ENGINE.md).

## 앱 — World Trip 화면

`gentle_monster/apps/worldtrip/` 은 [worldTrip](https://github.com/cogito5170/worldTrip) 엔진(세계여행 계획)의 프론트엔드다.
같은 잡지 문법으로 계획 · 경로 · 날짜 · 예산 보드 · 도시 펼침 · 청사진(A3 가로)을 그린다. 엔진 쪽에서 `worldtrip app` 한 줄이면
이 폴더를 받아 붙이고 브라우저를 연다. 화면은 엔진 심판의 V 를 지킨다 -- `python3 -m gentle_monster.apps.check`.
자세한 것: [`gentle_monster/apps/worldtrip/README.md`](gentle_monster/apps/worldtrip/README.md).

`gentle_monster/apps/worldplan/` 은 [worldplan](https://github.com/cogito5170/worldplan) 엔진(여러 시간대 회의 배치)의
프론트엔드다. 같은 갈래로 `worldplan app` 이 받아 붙인다. 토큰은 이 엔진이 짓고(`apps/worldplan_tokens.py`),
화면 검사는 `python3 -m gentle_monster.apps.check --app worldplan`. 자세한 것: [`gentle_monster/apps/worldplan/README.md`](gentle_monster/apps/worldplan/README.md).

## 편집 시스템 — 연구에서 매거진까지

```bash
python3 -m gentle_monster magazine "Gentle Monster의 브랜드 세계관을 중심으로, 미래의 유물과 인간의 감각을 주제로 한 실험적 매거진, HTML과 PDF"
```

연구 원장(`research/sources.json`: 출처 93 · 주장 63, 각자 **읽은 정도**와 종류) → **Drift**(se_new 의 DRIFT 규칙을 개념에
옮긴 것: 원장 · 한 걸음에 연산자 하나 · 물려받음을 재고 · 식은 것을 다시 부르고 · 4걸음마다 끼어들기) → 방향 4개 비교 →
쪽별 계획 → HTML + PDF(230 × 300 mm) → QA(PASS / WARNING / FAIL / NOT_CHECKED). 모델 호출 없음.
권리가 확인 안 된 이미지는 싣지 않고 출처로만 적는다. 자세한 것: [`docs/MAGAZINE_SYSTEM.md`](docs/MAGAZINE_SYSTEM.md) ·
조사: [`docs/REPOSITORY_AUDIT.md`](docs/REPOSITORY_AUDIT.md) · Drift 원문: [`research/drift/SE_NEW_DRIFT.md`](research/drift/SE_NEW_DRIFT.md).

## 디스코드 봇에 붙이기 (선택)

`gentle_monster.discord_cmd.run(text, images=[첨부 경로])` 는 `!젠몬 <아무 말>` 을 자연어로 읽는다(모델 호출 없음):

    !젠몬 비 오는 밤의 문턱을 주제로 한 성수 플래그십          → 시놉시스 + 레이아웃 + 무드보드
    !젠몬 (사진 + 레퍼런스 첨부) 이 레이아웃처럼 무드보드 다시   → 최근 작업 무드보드 다시
    !젠몬 방금 거 청사진 · !젠몬 방금 거 영상도                  → 요청 시 단계
    !젠몬 방금 거 웹 사이트로 · !젠몬 <브리프>, 웹페이지까지       → 웹 페이지 (frontend engine)
    !젠몬 탬버린즈 예제로 무드보드 · !젠몬 목록 · !젠몬 상태 <작업>

`!젠몬` 으로 시작하지 않는 말에는 `None` 을 돌려준다. 오래 걸리는 일은 분리된 프로세스로 띄우고 `logs/` 에 적는다.

## 구성

| 파일 | 하는 일 |
|---|---|
| `gentle_monster/spec.py` | job 형식과 검사 — 치수·모양·재료·문·겹침·**동선 여유 0.3 m**·정지점이 동선 위에 있는가 |
| `gentle_monster/synopsis.py` | 브리프 → Gemini → JSON → 검사. 실패하면 규칙 이름이 아니라 배치에 대한 사실을 돌려주고 최대 3바퀴 |
| `gentle_monster/llm.py` | Gemini 직접 호출(HTTPS). 키가 없으면 못 돈다고 말한다 — 다른 모델로 대신하지 않는다 |
| `gentle_monster/documents.py` | 평면 · 레이아웃 PDF(A3 세로 한 장) · 청사진 PDF(A3 가로) |
| `gentle_monster/photos.py` | 사진 분위기 측정 · 레퍼런스 판별 · 레퍼런스 양식 측정 |
| `gentle_monster/moodboard.py` | 잡지형 무드보드(A3 펼침 8장): 표지·목차·세로 선언·짝·풀블리드·보드·콜라주·시퀀스 |
| `gentle_monster/intent.py` | `!젠몬` 자연어 → 할 일 · 작업("방금 거" = 최근) · 브랜드 · 요청 단계 |
| `gentle_monster/web/scene.js` · `tour.js` | three.js r170 PBR 장면 · 도면 동선을 따라 걷는 30초 워크스루 |
| `gentle_monster/render.py` | 스틸, 그리고 프레임을 ffmpeg(libx264)로 잇는 영상 |
| `gentle_monster/engine/` | frontend engine: `tokens`(genome → 토큰 · DTCG) · `compose`(페이지) · `judge`(브라우저 심판 V · J) · `policy`(se_new 개선결정 · π) |
| `gentle_monster/apps/worldtrip/` | World Trip 앱 화면(정적 PWA) — worldTrip 엔진에 붙는다 · `apps/check.py` 가 엔진 심판의 V 를 이 앱에 건다 |
| `gentle_monster/apps/worldplan/` | worldplan 앱 화면(정적) — worldplan 엔진에 붙는다 · 토큰은 `apps/worldplan_tokens.py` · 같은 `apps/check.py --app worldplan` |
| `render3d/` | 2D 평면도(matplotlib) — gentle_monster 가 쓰는 부분만 |

## 테스트

```bash
python3 tests/test_gentle_monster.py      # 브라우저가 없으면 브라우저 부분은 '건너뜀'
python3 tests/test_engine.py              # 엔진: 정책 분기 · RED(깨뜨린 페이지가 그 검사만 실패) · GREEN
python3 tests/test_worldtrip_app.py       # World Trip 화면: 정적 검사 · V GREEN(고정 응답) · RED 여섯
python3 tests/test_worldplan_app.py       # worldplan 화면: 정적 검사(토큰이 엔진과 같나 포함) · V GREEN · RED 여섯
python3 tests/test_magazine.py            # 편집 시스템: 원장 · Drift 규칙 · 권리 · QA RED 아홉 · 빌드(HTML·PDF)
```

## 한계

- 치수는 가정이지 실측이 아니다.
- 실사는 실시간 PBR 렌더(three.js)이지 경로추적 사진이 아니다.
- 레퍼런스를 "따른다" 는 것은 잰 양식과 읽은 펼침 순서다. 레퍼런스의 격자를 픽셀 단위로 복제하지는 않는다.
- 공간 파이프라인의 PDF 와 웹 페이지 글은 영문이다. 매거진(`magazine`)은 한국어다(출처 원문 인용은 영어 그대로).
- 웹 페이지 심판은 그림 위에 겹친 글의 대비와 움직임의 질을 못 잰다. J 의 여백 목표(0.6)는 선언한 취향이다.
