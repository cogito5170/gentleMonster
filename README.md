# gentleMonster
frontEnd Design

공간 디자인 파이프라인 `gentle_monster` — 브리프 한 줄에서 공간 시놉시스, 레이아웃 PDF, 잡지형 무드보드 PDF를 만들고,
요청하면 청사진(A3 도면·실사 렌더)과 동선을 따라 걷는 30초 MP4까지 만든다.

```
<시놉시스>  →  <레이아웃 PDF + 무드보드 PDF>   기본
            →  <청사진 PDF + MP4>             요청할 때만 (영상은 수십 분)
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

## 디스코드 봇에 붙이기 (선택)

`gentle_monster.discord_cmd.run(text, images=[첨부 경로])` 는 `!젠몬 <아무 말>` 을 자연어로 읽는다(모델 호출 없음):

    !젠몬 비 오는 밤의 문턱을 주제로 한 성수 플래그십          → 시놉시스 + 레이아웃 + 무드보드
    !젠몬 (사진 + 레퍼런스 첨부) 이 레이아웃처럼 무드보드 다시   → 최근 작업 무드보드 다시
    !젠몬 방금 거 청사진 · !젠몬 방금 거 영상도                  → 요청 시 단계
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
| `render3d/` | 2D 평면도(matplotlib) — gentle_monster 가 쓰는 부분만 |

## 테스트

```bash
python3 tests/test_gentle_monster.py      # 브라우저가 없으면 브라우저 부분은 '건너뜀'
```

## 한계

- 치수는 가정이지 실측이 아니다.
- 실사는 실시간 PBR 렌더(three.js)이지 경로추적 사진이 아니다.
- 레퍼런스를 "따른다" 는 것은 잰 양식과 읽은 펼침 순서다. 레퍼런스의 격자를 픽셀 단위로 복제하지는 않는다.
- PDF 의 글은 영문이다.
