"""Build the self-contained pages the headless browser opens (stills and the walkthrough).

three.js and our modules are inlined as data: URLs in an import map, so a page works from
file:// -- render.py opens `page.as_uri()` and there is no server."""
from __future__ import annotations

import base64
import json
from pathlib import Path

from gentle_monster import paths

_TOUR_CSS = """<style>
#ov{position:fixed;inset:0;pointer-events:none;font-family:"Archivo","Liberation Sans",Arial,sans-serif;color:#f4f4ef}
.card{position:absolute;left:64px;bottom:70px;max-width:600px;opacity:0}
.card .k,.end .k{font-size:12px;letter-spacing:.2em;text-transform:uppercase;opacity:.8}
.card .t{font-size:46px;font-weight:700;letter-spacing:-.02em;line-height:1;margin:8px 0 12px}
.card .l{font-size:15px;line-height:1.5;opacity:.94}
.card .m{font-size:11px;letter-spacing:.08em;margin-top:14px;opacity:.7}
.cap{position:absolute;left:56px;bottom:52px;max-width:720px;opacity:0;border-left:2px solid var(--acc);padding-left:14px}
.cap b{display:block;font-size:21px;font-weight:600;letter-spacing:-.01em}
.cap span{display:block;font-size:13px;opacity:.88;margin-top:4px}
.bug{position:absolute;left:56px;top:34px;font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;opacity:.75}
.mini{position:absolute;right:34px;top:30px;opacity:0;background:rgba(10,10,10,.55);padding:8px;border:1px solid rgba(255,255,255,.25)}
.mini .lb{font-size:9px;letter-spacing:.16em;text-transform:uppercase;opacity:.75;margin-top:4px}
.bar{position:absolute;left:0;bottom:0;height:3px;background:var(--acc)}
.fade{position:absolute;inset:0;background:#000;opacity:0}
.end{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 110px;opacity:0;background:rgba(8,8,8,.74)}
.end .t{font-size:40px;font-weight:700;letter-spacing:-.02em;margin-top:8px}
.end .q{font-size:19px;margin-top:14px}
.end .m{font-size:10.5px;letter-spacing:.1em;margin-top:26px;opacity:.6;text-transform:uppercase}
.shade{position:absolute;inset:auto 0 0 0;height:280px;background:linear-gradient(transparent,rgba(0,0,0,.6))}
</style>
<div id="ov"><div class="shade"></div><div class="bug" id="bug"></div><div class="card" id="card"></div>
<div class="mini" id="mini"></div><div class="cap" id="cap"><b></b><span></span></div>
<div class="end" id="end"></div><div class="fade" id="fade"></div><div class="bar" id="bar"></div></div>"""


def _du(p: Path) -> str:
    return "data:text/javascript;base64," + base64.b64encode(p.read_bytes()).decode()


def _imports() -> dict:
    V, Wb = paths.VENDOR, paths.WEB
    return {"imports": {"three": _du(V / "three.module.min.js"),
                        "three/addons/environments/RoomEnvironment.js": _du(V / "RoomEnvironment.js"),
                        "three/addons/objects/Reflector.js": _du(V / "Reflector.js"),
                        "gm/scene": _du(Wb / "scene.js"), "gm/tour": _du(Wb / "tour.js")}}


def page(job: dict, mode: str, w: int = 1600, h: int = 1000, ss: float = 1.5) -> str:
    """mode: eye | cut (a still, sets window.__done) or tour (ruh2 contract: __ready + renderAt)."""
    head = ('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#000;overflow:hidden}canvas{display:block}</style>'
            '<script type="importmap">' + json.dumps(_imports()) + "</script></head><body>")
    data = json.dumps(job).replace("</", "<\\/")
    if mode == "tour":
        body = _TOUR_CSS + ("<script type=module>import { tour } from 'gm/tour'; try { const T = tour(" + data + "); document.body.prepend(T.canvas);"
                            " window.renderAt = T.renderAt; T.renderAt(0); window.__ready = true; } catch (e) { window.__err = String(e && e.stack || e); }</script>")
    else:
        body = ("<script type=module>import { still } from 'gm/scene'; try { const B = still(" + data + ", " + json.dumps(mode) +
                f", {{w: {w}, h: {h}, ss: {ss}}}); document.body.appendChild(B.renderer.domElement); window.__done = true; }} catch (e) {{ window.__err = String(e && e.stack || e); }}</script>")
    return head + body + "</body></html>"


def write(job: dict, mode: str, out: Path, **kw) -> Path:
    out = Path(out)
    out.write_text(page(job, mode, **kw), encoding="utf-8")
    return out
