# 파트 2 /02 Match. 8–11쪽 레이아웃 (2026-10-23)

사용자: "이후 파트 2를 새로운 커버 이미지와 적합한 디자인으로 다음 페이지를 구성하라. 포트폴리오의 사례를 참고하라.
옷을 다루는 기존 파트 3를 새로운 파트 2로 새롭게 제작한다."
→ `layout/part2_match.pdf`(4쪽) · `indesign/part2_match/part2_match.idml`(쪽 번호 8–11) · `python3 tools/jaju_layout/indd_part2.py`
글: 2-2 세션의 파트 2 '맞추다' 확정 스토리(사용자 지시로 보냄) — 안에서 밖으로, 한 벌 → 아이템 → 장소.

## 표지에서 이어 받은 디자인 말
- 납작한 색 면 셋: 파란 벽 #86A7D0 · 흰 벽 · 살구색 바닥 #E2AA88, 바닥 사선. 사진 속 사람은 바닥선 위에 선다.
- 좁은 굵은 대문자 제목(Instrument Sans Bold 장평 74%) · 작은 굵은 대문자 줄(자간 90–100) · 먹색 #1B1B1A.
- 책의 기준선 · 십자 · 바닥 줄(B18 값)은 먹색으로 그대로. 바닥 줄 왼쪽은 'FROM THE INSIDE — PART 2 MATCH'.

## 쪽별
| 쪽 | 무엇을 맞추나 | 구성 | 사례 |
|---|---|---|---|
| 8 /02 Match. | 표지 | 사용자 표지 이미지 + 글(`cover_match.md`) | Politics + Partnerships |
| 9 Front, or back? | 한 벌 | 표지의 방을 그대로: 파란 벽에 제목 · 리드 · 큰 인용 · 끝 줄 · 영어, 흰 벽 앞 바닥선에 (A) 앞 FA-04 · (B) 뒤 FA-03. 앞은 HAIR · COAT · TROUSERS · SHOES, 뒤는 SHOULDER · KNIT 지시선 | 6 Desjobert 지시선 |
| 10 Selection—06. | 아이템끼리 | 위 흰 벽: 번호 제목 + 리드 + 데이터 줄 + 견본 여섯. 가운데 파란 진열 벽: 여섯 아이템이 선반(바닥선)에 선다, 사진마다 출처 상자 N°FA-0x. 아래 살구색 바닥: COLOR · MATERIAL · FIT 세 줄, 끝 줄 · 영어 | 5 VERLAG 번호 제목 · 6 Desjobert CMF |
| 11 Four places, \| four outfits. | 장소에 | 접는 선 양쪽 제목. 방 넷 — 벽 = 장소에서 잰 색, 바닥 = 옷에서 잰 색, 그 안에 착장 사진. 아래 캡션(굵은 첫 낱말 + 줄표) · 색 짝 줄. 선언(가장 큰 글) · 영어, 오른쪽 다리 글(파트 3 로) | 1 ETÉREO 캡션 · 2 Galatasaray 색 짝 |

## 잰 색 (사진 픽셀 평균)
| 아이템 | HEX | 장소(잰 자리, 사진 비율) | HEX |
|---|---|---|---|
| 01 OLIVE PARKA | #29230D | Riverside — 물빛 x 0–0.35 · y 0.68–0.80 | #514A3A |
| 02 BLACK COAT | #070B12 | Shop front — 문 안 불빛 x 0.18–0.34 · y 0.30–0.60 | #B69B73 |
| 03 GREY KNIT | #61676E | Seaside rocks — 바위 x 0–0.35 · y 0.55–0.95 | #2B3949 |
| 04 WHITE SHIRT · WATCH | #8F8D88 | | |
| 05 BEIGE JACKET | #646776 | Park — 바닥 x 0.25–0.60 · y 0.82–0.97 | #4E5F6F |
| 06 GREY SNEAKERS | #3A3D3D | | |
아이템 색은 B20 Items 와 같은 자리 · 같은 값.

## 사용자 확인 필요
- 베이지 재킷 #646776 은 그늘진 자리의 회청색 — 다시 잴지(2-2 도 같은 질문).
- 데이터 줄 '4 COLOURS — BLACK · OLIVE · BEIGE · GREY' 에 흰 셔츠(#8F8D88, 그늘)가 들어가는지. 지금은 2-2 글 그대로.
- MATERIAL · FIT 은 사진에서 본 눈대중(예: 스니커즈 '스웨이드 · 메시'). 실제와 다르면 고친다.
- 표지 이미지 파일이 이 세션에 없어 8쪽은 자리 표시. 파일을 올려 주면 합친다.

## 변환 도구
- html2idml: SVG polygon(색 면 · 사선)을 InDesign Polygon 으로. 장평은 문단 위 상자의 transform 에서도 찾는다.
- 색 견본은 글과 따로 한 상자로 둔다(InDesign 에서 글 사이 틈이 사라지지 않게).
