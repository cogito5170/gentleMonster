---
name: codex-image
description: 렌더링이 아닌 이미지(컨셉 · 무드 · 히어로 · 표지 · 인물 · 제품 · 실사 사진풍 공간 · 일러스트 등)가 필요할 때 항상. Claude 는 짧은 의미 스펙만 쓰고, 상세 프롬프트와 생성은 사용자 VM 의 Codex 가 한다. three.js · 평면도 · PDF 같은 코드 렌더링에는 쓰지 않는다.
---

# Codex 이미지 생성 (VM 인박스)

이 세션에는 Codex 로그인이 없고 api.openai.com 도 막혀 있다. 이미지는 git 을 우편함으로 써서 사용자 VM 의
Codex 가 만든다. Claude 는 **무엇을 그릴지**만 JSON 으로 쓴다. 긴 프롬프트를 직접 쓰지 않는다.
설계: https://github.com/cogito5170/effiency/blob/main/docs/image-pipeline.md · docs/vm-inbox.md

## 1. 스펙 쓰기

`.relay/tasks/<번호>-<짧은-이름>/image-spec.json` (번호는 기존 폴더 다음 번호, 예 `012-rain-threshold`):

```json
{
  "subject": "비 오는 밤 성수 플래그십 입구, 젖은 콘크리트 문턱",
  "purpose": "무드보드 히어로",
  "style": "실사 건축 사진",
  "mood": "고요, 긴장",
  "composition": "낮은 시점, 문턱이 화면 하단 1/3",
  "palette": "차가운 회색, 나트륨등 주황 한 점",
  "lighting": "젖은 바닥 반사",
  "text": "",
  "size": "1536x1024",
  "avoid": ["사람 얼굴", "로고"]
}
```

`subject` 만 필수. 허용 필드는 위의 것과 `notes` 뿐이고 (그 밖의 키는 거부된다), 필드당 600자 이내.
`size` 는 `1024x1024` · `1536x1024` · `1024x1536`.

## 2. 요청 보내고 푸시

```bash
T=012-rain-threshold
relay request "$T" image   # request.json 작성. relay 가 없으면 아래 한 줄로 직접 써도 된다
# printf '{"action": "image", "id": "%s"}\n' "$(date +%Y%m%dT%H%M%S)" > .relay/tasks/$T/request.json
git add .relay/tasks/$T && git commit -m "relay request $T: image" && git push -u origin HEAD
```

브랜치는 이 세션의 `claude/...` 브랜치여야 한다 (VM 워커는 `claude/*` 만 본다).

## 3. 결과 받기

VM 워커가 30초마다 확인하고, 생성에 1~3분 걸린다. 결과 커밋이 올 때까지 기다린다:

```bash
B=$(git branch --show-current)
for i in $(seq 40); do
  git fetch -q origin "$B"
  git log -1 --format=%s "origin/$B" | grep -q "^relay inbox: $T" && break
  sleep 15
done
git pull -q origin "$B"
cat .relay/tasks/$T/response.json
```

- `status: done` → `.relay/tasks/$T/image.png` (그리고 `image-prompt.md`: Codex 가 펼친 프롬프트).
  이미지를 사용자에게 보여주고, 파이프라인 입력으로 쓸 거면 `photos/` 로 복사해 `--image` 로 넘긴다.
- `status: failed` → `output_tail` 의 이유를 사용자에게 그대로 전한다 (예: Codex 사용 한도).
- 10분이 지나도 커밋이 없으면 VM 워커가 꺼져 있을 수 있다. 사용자에게 VM 에서
  `systemctl --user status relay-inbox.timer` 확인을 부탁하고 기다리지 않는다.

같은 스펙을 다시 생성하려면 `relay request` 를 다시 실행한다 (`id` 가 바뀌어 새 요청이 된다).
스펙을 고친 경우도 마찬가지로 request.json 을 새로 쓴다.

## 청사진 표지 (실사 렌더 커버)

청사진의 실사 커버는 스펙을 손으로 쓰지 않는다. `gentle_monster/cover.py` 가 three.js 장면 데이터와 도면 데이터로 쓴다:

```bash
python3 -m gentle_monster cover <작업|gm|tb|ac|ae>     # .relay/tasks/<번호>-cover-<작업>/ 에 스펙 + 요청
# 위처럼 commit + push, 결과를 받은 뒤
python3 -m gentle_monster cover <작업> --attach .relay/tasks/<번호>-cover-<작업>
python3 -m gentle_monster blueprint <작업>             # 1쪽 Codex 커버 + 2쪽 three.js 도면
```

`--print` 는 스펙만 보여 준다. three.js 렌더는 그대로 남고, 커버가 없으면 청사진은 예전처럼 한 장이다.
