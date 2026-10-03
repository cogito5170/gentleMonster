# user_questions — semantic data of the real user questions

`questions.semantic.json` (schema `gm-user-questions/1`) holds every question and request the user sent in the gentleMonster work session: **44 turns**, verbatim, in order.
It adds what the verbatim list (`docs/portfolio/questions.md`) does not have: the question form, attached images and what they show, photo requests, question lists embedded in a turn, added constraints, and links to earlier turns.

Numbering is the same 1–44 as `docs/portfolio/questions.md` and baseline `GM_QUESTIONS.md`.

## Fields (per question)

| field | meaning |
|---|---|
| `text` | verbatim user text (Korean) |
| `channel` | `direct` · `sent_while_agent_working` (queued while the agent was running) · `choice_answer` (picked from options the agent offered) |
| `form` | question form, closed list in `taxonomy.form` (16 forms) |
| `group` | `writing_curation` · `artifact` · `ops_context` (same split as GM_QUESTIONS §1) |
| `task` | what was asked, as a short label |
| `refers_to` | earlier question ids this turn depends on |
| `context_dependent` | true when the turn cannot be read without earlier turns |
| `constraints` | conditions the turn adds |
| `embedded_questions` | questions or numbered steps written inside the turn |
| `attachments` | image files attached to this turn (see `images`) |
| `photo_request` | what the turn asks to do with photos: `classify` · `select` · `compare` · `arrange` · `generate` · `render` · `reference` · `context` |
| `expected_output` · `delivered` | what kind of answer was wanted, and what was given |
| `gm_tool` | GM_QUESTIONS §3 tool candidate T1–T9, or `out_of_scope` (host agent work) |
| `split` | `design` (1–31) · `eval_seen` (32–42, already seen per BD-186) · `ops` (40 · 43 · 44) |

## Images

14 images in 9 turns. For each image: role (`photo` · `reference_layout` · `notes` · `draft_page` · `draft_spread` · `case_study`), a description, subjects, the text inside the image (the notes in `8.jpg` are transcribed in full; they are themselves a list of self-asked questions), which images contain which (`7.jpg` and `10.jpg` reuse photo `3.webp`), size, sha256, and measured values (brightness · contrast · dark share · saturation · warmth · focus · palette · reference score, from `gentle_monster/photos.py`).

**The image files are not uploaded.** This repository is public and the photos show the applicant and real places. The sha256 identifies each file; upload only on the user's decision.

## Counts

| | |
|---|---|
| channels | direct 34 · sent while the agent was working 8 · choice answers 2 |
| forms | imperative task 11 · constraint append 8 · rewrite 5 · ops 4 · short contextual selection 3 · choice answer 2 · approval-continue 2 · one each: recommend options, combine variants, review opinion, compare-choose, feedback correction, retry, failure report, clarification hint, pasted material |
| turns with images / images | 9 / 14 |
| turns with a photo request | 12 |
| turns with embedded questions | 10 |
| context-dependent turns | 17 |
| median length | 51 characters |

Correction: the commit message of `questions.md` (gentleMonster#7) said 9 turns were sent while the agent was working. The count is **8** (6–9, 12, 15–17).
