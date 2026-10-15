# gentleMonster — Claude Code 메모

## 이미지는 모두 Codex 로 만든다 (2026-10-15 사용자 결정)

- 새 **이미지**는 종류를 가리지 않고 `.claude/skills/codex-image/SKILL.md` 를 따른다: 컨셉 · 무드 · 히어로 · 표지 · 인물 ·
  제품 · 실사 사진풍 공간 · 일러스트 · 아이콘 · 포스터 등. 짧은 `image-spec.json` 만 쓰고 푸시하면 사용자 VM 의 Codex 가
  이미지를 만들어 같은 브랜치에 올린다.
- 이 세션에서 이미지를 직접 그리지 않는다: PIL · matplotlib · SVG · HTML 캔버스로 그림을 "만들어" 대신하지 않고,
  OpenAI · Gemini 등 다른 이미지 모델을 직접 부르지 않고, 긴 이미지 프롬프트를 쓰지 않는다.
- **렌더링은 이미지가 아니다** — 지금처럼 코드가 만든다: 작업 데이터에서 결정적으로 나오는 three.js 스틸 · 30초 영상,
  평면도, 레이아웃 · 무드보드 · 청사진 PDF, 웹 페이지, 차트 · 다이어그램, 스크린샷.
- 둘이 만나는 곳: 청사진 표지처럼 렌더 데이터로 실사 이미지를 만들 때는 `python3 -m gentle_monster cover <작업>` 이
  스펙을 쓴다 (스킬 문서의 "청사진 표지").
- VM 이 응답하지 않거나 Codex 가 실패하면 다른 방법으로 이미지를 만들지 말고, `response.json` 의 이유를 사용자에게 그대로 전한다.

## 워크스페이스 (2026-10-15)

- 이 저장소는 effiency 와 함께 워크스페이스 `workspace:gentlemonster-effiency` 로 묶여 있다. 세션 구성, 허브(클라우드 `gmg-net`)와
  사용자 VM(Codex · agy, `relay inbox`)의 역할, **context biasing 방지 정책**은 effiency `docs/workspace.md` 를 따른다.
- 요지: 세션 사이에는 대화가 아니라 파일을 넘긴다. 넘기는 줄에는 출처(사용자 · 도구출력 · 추론·미검증)를 단다.
  확정은 파일에서 읽는다. 도메인이나 역할이 바뀌면 앞 작업의 결정을 적용하지 않는다.
