# 작업 공간 ↔ 에이전트 전달 규약 (semantic message protocol)

세 역할로 나눠 작업한다.
- **혁주 작업 공간** (메인 세션): 사용자 요구를 받는다. 요구를 메시지로 바꿔 에이전트에게 넘기고, 받은 결과만 사용자에게 보여 준다. 글을 직접 분석하거나 고쳐 쓰지 않는다.
- **analysis agent**: 글을 진단한다. 고쳐 쓰지 않는다.
- **editor agent**: 진단을 받아 고친다. 분석을 다시 하지 않는다.

```
사용자 → 작업 공간 ─analysis_request→ analysis agent
                  ←analysis_result──
         작업 공간 ─edit_request────→ editor agent
                  ←edit_result──────
사용자 ← 작업 공간 (결과만 출력, 파일 기록 · 커밋)
```

- 두 에이전트는 서로 직접 주고받지 않는다. 작업 공간이 메시지를 **고치지 않고** 그대로 전달한다.
- 파일에 쓰는 것과 커밋은 작업 공간만 한다. 에이전트는 메시지만 돌려준다.

## 1. 공통 봉투 `ga_message/1`

모든 메시지는 이 봉투에 담는다. 본문(`payload`)의 형식은 `type`에 따라 정해진다.

```json
{
  "schema": "ga_message/1",
  "message_id": "msg_<번호>",
  "thread_id": "thr_<작업 단위>",
  "reply_to": "msg_<번호> | null",
  "from": "workspace | analysis_agent | editor_agent",
  "to": "workspace | analysis_agent | editor_agent",
  "type": "analysis_request | analysis_result | edit_request | edit_result | error",
  "task": "diagnose | revise | propose_options | verify",
  "payload": {},
  "workspace_rules": "§4를 그대로 넣는다",
  "status": "ok | needs_user_decision | blocked"
}
```

## 2. 본문 형식

### 2-1. `analysis_request` (작업 공간 → analysis)
```json
{
  "document": { "id": "self_intro | cover_letter", "question": "문항 원문", "limit_chars": 1000, "text": "현재 원고 전문" },
  "user_feedback": { "raw": "사용자 말 원문 그대로", "scope": "전체 | 특정 문장 · 문단" },
  "facts": ["사용자가 확인한 사실 목록"],
  "rejected": ["사용자가 거절한 표현 · 소재"]
}
```

### 2-2. `analysis_result` (analysis → 작업 공간)
- 흐름 진단이면 `context_flow_analysis/1`, 고칠 곳까지 정하면 `semantic_edit_context/1` (사용자가 준 형식)을 그대로 쓴다.
- 반드시 들어가는 것:
  - 관찰한 문제(`observed`)와 추정한 원인(`cause`)을 나눠 적는다.
  - 판단마다 `confidence`(0~1)를 단다.
  - 자연스러운 곳은 `natural`로 적는다.
  - 고칠 곳은 3곳 이하로, 심각도(P0/P1/P2)를 단다.

### 2-3. `edit_request` (작업 공간 → editor)
- `analysis_result`의 본문을 그대로 넣는다.
- 여기에 `user_feedback.raw`, `document.text`, `facts`, `rejected`를 붙인다.

### 2-4. `edit_result` (editor → 작업 공간) — `semantic_edit_result/1`
```json
{
  "schema": "semantic_edit_result/1",
  "changes": [
    { "id": "R1", "location": ["A","B"], "operation": "connect | sequence | bridge | clarify_reference | reorder | split | merge | rephrase | remove_redundancy",
      "before": "원문 문장", "after": "고친 문장", "reason": "한 줄", "options": ["대안 문장(선택)"] }
  ],
  "revised_text": "고친 원고 전문",
  "char_count": { "total": 0, "limit": 1000, "remaining": 0, "method": "공백 · 줄바꿈 포함 len()" },
  "untouched": [{ "location": "...", "why": "과한 수정 피하기 | 사용자 판단 필요" }],
  "fact_check": { "new_facts_added": false, "notes": "" },
  "needs_user_decision": ["사용자가 골라야 할 것"]
}
```

### 2-5. `error`
- 에이전트가 작업을 못 할 때 보낸다. 예: 사실이 모자람, 요구가 서로 부딪침.
- `payload`: `{ "reason": "...", "missing": ["사용자에게 물어야 할 것"] }`
- 에이전트는 빈칸을 추측해서 채우지 않는다.

## 3. 요구 종류별 경로

| 사용자 요구 | task | 경로 |
|---|---|---|
| "흐름 봐 줘", "어디가 어색해?" | diagnose | analysis만 |
| "고쳐 줘", "문맥 이어지게" | revise | analysis → editor |
| "대안 문장 n개" | propose_options | editor만 (해당 문장 + 앞뒤 문맥) |
| "n안 채택" | — | 작업 공간이 원고에 반영 · 기록 (에이전트 호출 없음) |
| 고친 원고 점검 | verify | analysis (고친 원고로 다시 진단) |

## 4. workspace_rules (모든 메시지에 그대로 넣는다)

- 사실 · 경험 · 성과 · 동기는 바꾸지 않는다. 사용자가 말하지 않은 것은 지어내지 않는다.
- 합니다체로 쓴다. 저는 · 제가 · 저를 같은 지칭어는 뺀다.
- 추상적이거나 감정적인 말은 피한다. 직관적이고 구체적으로 쓴다.
- 통째로 다시 쓰지 않는다. 부분만 고치고, 대안을 제시한다. 고르는 것은 사용자가 한다.
- 거절된 소재 · 표현은 다시 쓰지 않는다.
  - 홍대점 이야기
  - 설계 프로젝트 내용
  - 이솝
  - 알바 알토 · 아르텍
  - "내 눈은 늘 그 안에 머물렀다"
  - "도전하지 않으면 아쉬울 것 같아"
- 글자 수는 공백 · 줄바꿈을 포함해 `len()`으로 센다. 문항 제한을 넘지 않는다.

## 5. 작업 공간이 사용자에게 보여 주는 것

- 결과만 보여 준다.
  - 고친 문장의 전 · 후
  - 대안 목록
  - 진단 요약
  - 글자 수
  - 사용자가 골라야 할 것
- 에이전트 간 메시지와 진행 과정은 보여 주지 않는다. 원문 메시지는 `docs/portfolio/agent_log/`에 남긴다.
- 에이전트가 `error`나 `needs_user_decision`을 돌려주면 그 질문만 짧게 전한다.
