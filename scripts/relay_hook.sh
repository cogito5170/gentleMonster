#!/usr/bin/env bash
# Claude Code hook -> relay(cogito5170/effiency) 컨텍스트 보관소.
#   session    : /clear · 자동 압축 뒤 "이전 대화는 .relay/archive 에 있다" 한 줄 (내용은 안 넣는다)
#   prompt     : 컨텍스트가 크면 대화를 보관하고, 보관 기록과 겹치는 요청이면 같은 도메인의 한 줄 요약만 붙인다
#   precompact : 자동 압축 직전에 원문을 보관한다
# relay 가 없으면 세션 시작 때 한 번 설치를 시도한다. 무엇이 실패해도 세션을 막지 않는다(항상 0 으로 끝난다).
event="${1:-}"
if ! command -v relay >/dev/null 2>&1; then
  [ "$event" = "session" ] || exit 0
  src="git+https://github.com/cogito5170/effiency.git@main"
  python3 -m pip install -q --disable-pip-version-check "$src" </dev/null >/dev/null 2>&1 \
    || python3 -m pip install -q --disable-pip-version-check --user "$src" </dev/null >/dev/null 2>&1
  hash -r
  command -v relay >/dev/null 2>&1 || exit 0
fi
relay hook "$event" 2>/dev/null || true
exit 0
