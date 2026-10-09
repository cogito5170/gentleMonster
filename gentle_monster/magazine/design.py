"""Design system: tokens -> CSS. One content spec, two renderings (screen and print), kept in separate blocks.

Tokens
    colour      paper / ink / accent come from the chosen hypothesis (its discipline's palette); muted and rule
                are mixed from them, so a new palette never needs hand-tuning
    type        modular scale, ratio 1.25, base 10pt (print) / 16px (screen); serif body, grotesk display,
                mono for numbers (find numbers, folios, timecodes) -- only fonts installed here (Liberation)
    grid        12 columns, gutter 5 mm, margins 16/14/18/20 mm (top/outer/bottom/inner) on a 230 x 300 mm page
    baseline    14 pt; block spacing in baseline units
Page types: cover · single_column · multi_column · asymmetric · full_bleed · image_essay · product_study ·
catalogue · typographic · intrusion · references · colophon
"""
from __future__ import annotations

PAGE_W, PAGE_H = 230, 300            # mm
MARGIN = {"top": 16, "outer": 14, "bottom": 18, "inner": 20}
COLS, GUTTER = 12, 5                 # mm
BASELINE = 14                        # pt
RATIO = 1.25
PAGE_TYPES = ("cover", "single_column", "multi_column", "asymmetric", "full_bleed", "image_essay", "product_study",
              "catalogue", "typographic", "intrusion", "references", "colophon")
FONTS = {"serif": '"Liberation Serif","DejaVu Serif",Georgia,serif',
         "sans": '"Liberation Sans","DejaVu Sans",Arial,sans-serif',
         "mono": '"Liberation Mono","DejaVu Sans Mono",monospace'}


def _hex(c):
    c = c.lstrip("#"); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    x, y = _hex(a), _hex(b)
    return "#" + "".join(f"{round(x[i] + (y[i] - x[i]) * t):02x}" for i in range(3))


def luminance(c):
    def ch(v):
        v /= 255; return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = _hex(c); return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def tokens(palette: dict) -> dict:
    paper, ink, accent = palette["paper"], palette["ink"], palette["accent"]
    t = {"color": {"paper": paper, "ink": ink, "accent": accent, "muted": mix(ink, paper, 0.38), "rule": mix(ink, paper, 0.75),
                   "plate": mix(paper, ink, 0.06)},
         "scale": [round(10 * RATIO ** i, 2) for i in range(-2, 7)],      # pt: 6.4 .. 38.1
         "grid": {"cols": COLS, "gutter_mm": GUTTER, "margin_mm": MARGIN, "page_mm": [PAGE_W, PAGE_H]},
         "baseline_pt": BASELINE, "fonts": FONTS}
    # accent text must stay legible on paper; if not, use it for rules and fills only
    t["accent_text"] = accent if contrast(accent, paper) >= 4.5 else ink
    t["contrast"] = {"ink/paper": contrast(ink, paper), "muted/paper": contrast(t["color"]["muted"], paper),
                     "accent/paper": contrast(accent, paper)}
    return t


def print_rules(pre: str, s=None) -> str:
    """Print geometry. Emitted twice: inside @media print, and under html.print-sim so the QA browser can
    measure overflow at print size without a print dialog (Chromium's --dump-dom has no print emulation)."""
    m = MARGIN
    return (f"{pre}.page{{width:{PAGE_W}mm;height:{PAGE_H}mm;aspect-ratio:auto;margin:0;break-after:page;"
            f"padding:{m['top']}mm {m['outer']}mm {m['bottom']}mm {m['inner']}mm;font-size:{s:.2f}pt;column-gap:{GUTTER}mm}}"
            f"{pre}.page:nth-of-type(even){{padding-left:{m['outer']}mm;padding-right:{m['inner']}mm}}"
            f"{pre}.pt-full_bleed{{padding:0!important}}")


def css(t: dict) -> str:
    c, s = t["color"], t["scale"]
    pr = lambda pre: print_rules(pre, s[2])  # noqa: E731 -- bind the scale once
    col = f"calc((100% - {GUTTER * (COLS - 1)}mm) / {COLS})"
    return f"""
:root{{--paper:{c['paper']};--ink:{c['ink']};--accent:{c['accent']};--accent-text:{t['accent_text']};--muted:{c['muted']};
--rule:{c['rule']};--plate:{c['plate']};--serif:{FONTS['serif']};--sans:{FONTS['sans']};--mono:{FONTS['mono']};
--b:{BASELINE}pt;--g:{GUTTER}mm}}
*{{box-sizing:border-box}}
html{{background:#8a8a86}}
body{{margin:0;color:var(--ink);font-family:var(--serif);-webkit-font-smoothing:antialiased}}
.page{{position:relative;background:var(--paper);overflow:hidden;margin:0 auto 28px;width:min(100% - 32px, 920px);
  aspect-ratio:{PAGE_W}/{PAGE_H};padding:4.2% 4.6% 5.4% 6.1%;display:grid;grid-template-columns:repeat({COLS},1fr);
  column-gap:2.2%;align-content:start;font-size:clamp(12px,1.55vw,15px);line-height:1.5}}
.page.dark{{background:var(--ink);color:var(--paper)}}
.rh{{grid-column:1/-1;display:flex;justify-content:space-between;font:600 .68em/1 var(--mono);letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--rule);padding-bottom:.7em;margin-bottom:1.6em}}
.dark .rh{{color:var(--paper);border-color:var(--muted)}}
.folio{{position:absolute;bottom:2.4%;font:600 .7em var(--mono);color:var(--muted)}}
.folio.l{{left:6.1%}} .folio.r{{right:4.6%}}
h1,h2,h3{{font-family:var(--sans);margin:0;line-height:1.05;letter-spacing:-.01em}}
h1{{font-size:{s[8] / 10:.2f}em;font-weight:700}} h2{{font-size:{s[6] / 10:.2f}em;font-weight:700;margin-bottom:.5em}}
h3{{font-size:{s[3] / 10:.2f}em;margin:0 0 .3em}}
p{{margin:0 0 .75em;hyphens:auto}}
.tag{{display:inline-block;font:700 .62em/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;padding:.45em .6em;
  border:1px solid currentColor;margin-bottom:1em}}
.tag.exp{{color:var(--accent-text);border-color:var(--accent)}}
.kind{{font:600 .62em var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}}
sup a{{color:var(--accent-text);text-decoration:none;font:600 .7em var(--mono)}}
figure{{margin:0}} figure img{{display:block;width:100%;height:auto;background:var(--plate)}}
figcaption{{font:.68em/1.45 var(--sans);color:var(--muted);margin-top:.6em;overflow-wrap:anywhere}}
figcaption b{{color:var(--ink);font-weight:700}} .dark figcaption b{{color:var(--paper)}}
.lede{{font-size:1.18em;line-height:1.42}}
.span-12{{grid-column:1/-1}} .span-8{{grid-column:span 8}} .span-7{{grid-column:span 7}} .span-6{{grid-column:span 6}}
.span-5{{grid-column:span 5}} .span-4{{grid-column:span 4}} .start-5{{grid-column:5/-1}} .start-6{{grid-column:6/-1}}
.cols-2{{columns:2;column-gap:var(--g)}} .cols-3{{columns:3;column-gap:var(--g)}}
.cols-2 > *,.cols-3 > *{{break-inside:avoid}}
.claim{{margin-bottom:1em}}
/* cover */
.pt-cover{{align-content:space-between}}
.pt-cover .mast{{grid-column:1/-1;font:700 5.4em/0.86 var(--sans);letter-spacing:-.04em;text-transform:uppercase}}
.pt-cover .q{{grid-column:1/9;font-size:1.5em;line-height:1.2;font-family:var(--serif);font-style:italic}}
.pt-cover figure{{grid-column:3/-1}}
.pt-cover .disclaimer{{grid-column:1/-1;font:.66em var(--mono);color:var(--muted);border-top:1px solid var(--rule);padding-top:.8em}}
/* full bleed */
.pt-full_bleed{{padding:0}} .pt-full_bleed figure{{grid-column:1/-1;height:100%;position:absolute;inset:0}}
.pt-full_bleed figure img{{height:100%;object-fit:cover}}
.pt-full_bleed .over{{position:absolute;left:6.1%;bottom:6%;right:30%;background:var(--paper);padding:1.2em 1.4em;color:var(--ink)}}
.pt-full_bleed .rh{{position:absolute;top:4.2%;left:6.1%;right:4.6%;z-index:2;background:var(--paper);padding:.6em}}
/* catalogue */
.entries{{grid-column:1/-1;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--g)}}
.entries.four{{grid-template-columns:repeat(4,minmax(0,1fr))}}
.entry{{border-top:1px solid var(--ink);padding-top:.5em;font-size:.82em}}
.entry .no{{font:700 1.1em var(--mono);color:var(--accent-text)}}
.withheld{{aspect-ratio:4/3;overflow-wrap:anywhere;border:1px dashed var(--muted);display:flex;align-items:center;justify-content:center;
  text-align:center;font:.75em/1.3 var(--mono);color:var(--muted);padding:.6em}}
/* typographic / intrusion */
.pt-typographic .chart{{grid-column:1/-1;text-align:center;font-family:var(--sans);font-weight:700;line-height:1.05}}
.pt-intrusion{{align-content:center}} .pt-intrusion .who{{grid-column:2/12;font:700 2.6em/1.05 var(--sans)}}
.pt-intrusion .mark{{grid-column:2/12;font:1.1em var(--mono);margin-top:2em;border-top:1px solid currentColor;padding-top:1em}}
/* tables */
table{{width:100%;border-collapse:collapse;font-size:.78em}} th,td{{text-align:left;vertical-align:top;padding:.4em .5em .4em 0;
  border-bottom:1px solid var(--rule)}} th{{font:700 .85em var(--mono);text-transform:uppercase;letter-spacing:.05em}}
td.n{{font-family:var(--mono);white-space:nowrap}}
.refs{{grid-column:1/-1;columns:2;column-gap:var(--g);font-size:.68em;line-height:1.35}}
.refs li{{break-inside:avoid;margin-bottom:.5em}} .refs a{{color:inherit;word-break:break-all}}
ol.chain{{padding-left:1.4em}} ol.chain li{{margin-bottom:.5em}}
.small{{font-size:.8em}}
@media (max-width:700px){{
  .page{{aspect-ratio:auto;min-height:0;width:calc(100% - 32px);padding:22px 18px 40px;font-size:15px;display:block}}
  .page > *{{margin-bottom:14px}} .cols-2,.cols-3,.refs{{columns:1}} .entries,.entries.four{{grid-template-columns:repeat(2,minmax(0,1fr))}}
  .pt-cover .mast{{font-size:3.2em}} .pt-full_bleed figure{{position:relative;height:auto}}
  .pt-full_bleed .over,.pt-full_bleed .rh{{position:relative;inset:auto;left:auto;right:auto;bottom:auto;top:auto}}
}}
@page{{size:{PAGE_W}mm {PAGE_H}mm;margin:0}}
@media print{{ html{{background:none}} html .nav{{display:none}} *{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
{pr("")} }}
{pr("html.print-sim ")}
html.print-sim .nav{{display:none}} html.print-sim body{{width:{PAGE_W}mm}}
.nav{{position:sticky;top:0;z-index:5;background:var(--ink);color:var(--paper);font:12px var(--mono);padding:10px 16px;
  display:flex;gap:14px;overflow-x:auto;margin-bottom:24px}} .nav a{{color:var(--paper);white-space:nowrap}}
"""
