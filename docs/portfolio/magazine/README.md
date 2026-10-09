# SPA 잡지 — 디자인 시안 (design_variant/1)

확정 원고(`docs/portfolio/*.md`)를 그대로 지면에 앉힌 잡지 디자인 시안. 시안마다 폴더 하나, 같은 원고 · 같은 사진 번호(IMG-xx)를 쓴다.
비교와 최종 선택은 이 폴더 밖(비평 · 오케스트레이터)에서 한다.

| 시안 | 가설 | 결과물 |
|---|---|---|
| [variant_a_stopline](variant_a_stopline/) | 빨간 **정지선** 하나만 반복 — 섹션이 멈추는 문장 아래에만. 읽는 쪽은 그림 20 % 미만, 멈추는 쪽(다리)은 60 % 이상 | `magazine.pdf` · `render/spread_*.png` · `design_variant.json` · `render/checks.json` |

## 다시 그리기

```bash
NODE_PATH=$(npm root -g) node docs/portfolio/magazine/render.js docs/portfolio/magazine/variant_a_stopline
```

Chromium 에서 PDF · 펼침 PNG 를 만들고 잰다: 재단선 · 판면 · 넘침 · 블록 겹침 · 최소 6.5 pt · 대비(WCAG) · 쪽수.
18 pt 이상 디스플레이 활자는 자동 판정하지 않고 `manual_visual_checks` 로 남긴다 — PNG 를 눈으로 본다.

## 지금 상태

- **사진은 한 장도 없다.** 모든 그림 칸은 빗금 · 점선의 자리표시(IMG-xx, 피사체, 잰 값)다. 원본을 넣으면 다시 그리고 다시 잰다.
- 한글은 교정용 WenQuanYi Zen Hei 로 찍혔다. 인쇄용 한글 서체(Pretendard / Noto Sans KR)는 정해지지 않았다.
- 03 ARCHITECTURE 는 원고가 없어 설계하지 않았다.
