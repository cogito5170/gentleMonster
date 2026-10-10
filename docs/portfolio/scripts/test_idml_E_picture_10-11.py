"""idml_E_picture_10-11.py 검사 — 다른 파일 없이 혼자 돈다.

python3 docs/portfolio/scripts/test_idml_E_picture_10-11.py

10–11쪽 펼침(E)과 8–9쪽 펼침(D)이 든 작은 IDML 을 코드로 지어서 스크립트를 걸고 본다:
E 는 원고대로 바뀌고, D 와 그 스토리는 한 바이트도 바뀌지 않고(독립), 두 번 돌려도 같다(멱등).
"""
import contextlib
import importlib.util
import io
import os
import re
import tempfile
import unittest
import zipfile
import xml.dom.minidom

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("idml_e", os.path.join(HERE, "idml_E_picture_10-11.py"))
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

W, H = 841.8897637795276, 1190.5511811023623
NS = 'xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="21.5"'


def story(sid, lines, size=9, style="Bold", font="Helvetica Neue"):
    body = "<Br />".join(f"<Content>{t}</Content>" for t in lines)
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<idPkg:Story {NS}>\n'
            f'\t<Story Self="{sid}">\n\t\t<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle">\n'
            f'\t\t\t<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" FontStyle="{style}" PointSize="{size}">\n'
            f'\t\t\t\t<Properties>\n\t\t\t\t\t<AppliedFont type="string">{font}</AppliedFont>\n\t\t\t\t</Properties>\n'
            f'\t\t\t\t{body}\n\t\t\t</CharacterStyleRange>\n\t\t</ParagraphStyleRange>\n\t</Story>\n</idPkg:Story>\n')


def path(box):
    x0, y0, x1, y1 = box
    pts = "".join(f'<PathPointType Anchor="{x} {y}" LeftDirection="{x} {y}" RightDirection="{x} {y}" />'
                  for x, y in ((x0, y0), (x0, y1), (x1, y1), (x1, y0)))
    return f'<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>{pts}</PathPointArray></GeometryPathType></PathGeometry></Properties>'


def frame(fid, sid, box, nxt="n", prev="n"):
    return (f'\t\t<TextFrame Self="{fid}" ParentStory="{sid}" PreviousTextFrame="{prev}" NextTextFrame="{nxt}" ContentType="TextType" '
            f'ItemTransform="1 0 0 1 0 0">{path(box)}<TextFramePreference TextColumnCount="1" /></TextFrame>\n')


def rect(rid, box, stroke):
    return (f'\t\t<Rectangle Self="{rid}" ContentType="GraphicType" StrokeWeight="{stroke}" ItemTransform="1 0 0 1 0 0">{path(box)}'
            f'<Image Self="{rid}i" ItemTransform="1 0 0 1 0 0" /></Rectangle>\n')


def spread(sid, names, items):
    pages = "".join(f'\t\t<Page Self="{sid}p{n}" Name="{n}" GeometricBounds="0 0 {H} {W}" ItemTransform="1 0 0 1 {x} {-H / 2}" />\n'
                    for n, x in zip(names, (-W, 0)))
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<idPkg:Spread {NS}>\n'
            f'\t<Spread Self="{sid}" PageCount="2" ItemTransform="1 0 0 1 0 2000">\n{pages}{"".join(items)}\t</Spread>\n</idPkg:Spread>\n')


# 10쪽 = x -W..0, 11쪽 = x 0..W, y -H/2..H/2
OLD_BODY = ("빛, 색, 사람, 장소가 한순간에 맞아떨어질 때가 있다. 그때 나는 카메라를 꺼낸다. 앞 페이지의 사진도 그랬다. "
            "헤드폰을 쓴 사람, 체크 셔츠와 슬리퍼, 그리고 그 뒤의 화분과 사람, 장소가 함께 맞아떨어진 순간이었다.")


def build(dst, split_title=False):
    stories = {
        "d1": story("d1", ["I stop for people whose style is their own."], 60),
        "d2": story("d2", ["download now", "www.template.systems"]),            # D 의 템플릿 글: 건드리면 안 된다
        "t1": story("t1", ["MOMENT", "PHOTOGR"] if split_title else ["MOMENT LIKE A", "PHOTOGRAPH"], 150),
        "n1": story("n1", ["(002)"], 120),
        "c1": story("c1", ["download now", "www.template.systems"]),
        "r1": story("r1", ["Template Systems", "Grid Systems Series"]),
        "x1": story("x1", ["download now", "www.template.systems"]),            # 왼쪽 재단선 밖으로 잘린 상자
        "b1": story("b1", [OLD_BODY, "그래서 내 두 번째 이야기는 사진이다."], 13, "Regular", "AppleGothic"),
        "l1": story("l1", ["Experimental Grid Exploration"], 14),
    }
    e_items = [
        frame("ft1", "t1", (-800, -500, -200, -260)),
        frame("fn1", "n1", (-300, 100, -60, 220)),
        frame("fc1", "c1", (-500, 400, -300, 430)),
        frame("fr1", "r1", (-300, 300, -60, 330)),
        frame("fx1", "x1", (-900, 540, -820, 570)),
        frame("fb1", "b1", (100, -100, 500, 100)),
        frame("fl1", "l1", (100, 450, 500, 480)),
        rect("pt1", (100, -400, 400, -200), 3),
    ]
    if split_title:
        stories["t2"] = story("t2", ["LIKE A", "APH"], 150)
        e_items.insert(1, frame("ft2", "t2", (40, -500, 700, -260)))
    files = {
        "Spreads/Spread_sd.xml": spread("sd", ("8", "9"), [frame("fd1", "d1", (-800, -100, 800, 100)), frame("fd2", "d2", (-500, 400, -300, 430))]),
        "Spreads/Spread_se.xml": spread("se", ("10", "11"), e_items),
    }
    for sid, xt in stories.items():
        files[E.story_path(sid)] = xt
    files["designmap.xml"] = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Document {NS} Self="d" StoryList="{" ".join(stories)}">\n'
        '\t<idPkg:Spread src="Spreads/Spread_sd.xml" />\n\t<idPkg:Spread src="Spreads/Spread_se.xml" />\n'
        + "".join(f'\t<idPkg:Story src="{E.story_path(s)}" />\n' for s in stories) + "</Document>\n")
    with zipfile.ZipFile(dst, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.adobe.indesign-idml-package", compress_type=zipfile.ZIP_STORED)
        for n, b in files.items():
            z.writestr(n, b, compress_type=zipfile.ZIP_DEFLATED)


def read(p):
    z = zipfile.ZipFile(p)
    return {n: z.read(n) for n in z.namelist()}, z.namelist()


def texts(files):
    return {n: E.norm(E.story_text(b.decode())) for n, b in files.items() if n.startswith("Stories/")}


def run(src, dst):
    with contextlib.redirect_stdout(io.StringIO()):
        return E.main(src, dst)


class SpreadE(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = lambda n: os.path.join(self.tmp.name, n)

    def tearDown(self):
        self.tmp.cleanup()

    def fix(self, split_title=False):
        build(self.p("in.idml"), split_title)
        log, missing, warn, left = run(self.p("in.idml"), self.p("out.idml"))
        return read(self.p("in.idml"))[0], read(self.p("out.idml")), log, missing, warn, left

    def test_manuscript(self):
        before, (after, order), log, missing, warn, left = self.fix()
        t = texts(after)
        self.assertEqual(missing, [])
        self.assertEqual(left, [])
        self.assertEqual(order[0], "mimetype")
        self.assertEqual(t["Stories/Story_t1.xml"], "PICTURE")
        self.assertEqual(t["Stories/Story_n1.xml"], "(002)")
        self.assertEqual(t["Stories/Story_r1.xml"], "A Moment like A Photograph")
        self.assertEqual(t["Stories/Story_l1.xml"], "I stop for a scene. (My second story is about pictures.)")
        self.assertEqual(t["Stories/Story_b1.xml"], E.norm(" ".join(E.OPENING_KO)))
        body = after["Stories/Story_b1.xml"].decode()
        self.assertIn("화분과 칠판. 사람과 장소가", body)
        self.assertEqual(body.count("<Br />"), 2)  # 세 단락
        self.assertIn("AppleGothic", body)        # 본문 글꼴은 그대로
        for gone in ("c1", "x1"):
            self.assertNotIn(E.story_path(gone), after)
        # 둘째 줄은 Regular
        label = after["Stories/Story_l1.xml"].decode()
        self.assertEqual(re.findall(r' FontStyle="(\w+)"', label), ["Bold", "Regular"])

    def test_title_like_style(self):
        _, (after, _), *_ = self.fix()
        title = after["Stories/Story_t1.xml"].decode()
        self.assertIn(f'PointSize="{E.STYLE_SIZE}"', title)
        self.assertIn('FontStyle="Bold"', title)
        self.assertIn(">Helvetica<", title)
        sp = after["Spreads/Spread_se.xml"].decode()
        m = re.search(r'<TextFrame Self="ft1".*?</TextFrame>', sp, re.S).group(0)
        xs, ys = zip(*[map(float, a.split()) for a in re.findall(r'Anchor="([^"]*)"', m)])
        self.assertAlmostEqual(min(xs), -W + E.STYLE_BOX[0], places=2)
        self.assertAlmostEqual(min(ys), -H / 2 + E.STYLE_BOX[1], places=2)

    def test_split_title(self):
        _, (after, _), log, missing, *_ = self.fix(split_title=True)
        self.assertEqual(missing, [])
        self.assertNotIn(E.story_path("t2"), after)
        self.assertNotIn('Self="ft2"', after["Spreads/Spread_se.xml"].decode())
        self.assertEqual(texts(after)["Stories/Story_t1.xml"], "PICTURE")

    def test_photo(self):
        _, (after, _), *_ = self.fix()
        sp = after["Spreads/Spread_se.xml"].decode()
        self.assertIn('<Rectangle Self="pt1" ContentType="GraphicType" StrokeWeight="0"', sp)
        caps = [n for n, t in texts(after).items() if t == E.CAPTION]
        self.assertEqual(len(caps), 1)
        sid = caps[0][len("Stories/Story_"):-4]
        dm = after["designmap.xml"].decode()
        self.assertIn(f'<idPkg:Story src="{caps[0]}" />', dm)
        self.assertRegex(dm, rf'StoryList="[^"]*\b{sid}\b')
        m = re.search(rf'<TextFrame Self="\w+" ParentStory="{sid}".*?</TextFrame>', sp, re.S).group(0)
        ys = [float(a.split()[1]) for a in re.findall(r'Anchor="([^"]*)"', m)]
        self.assertAlmostEqual(min(ys), -200 + E.CAPTION_GAP)  # 사진 아래 끝 + 간격

    def test_independent(self):
        before, (after, _), *_ = self.fix()
        for n in ("Spreads/Spread_sd.xml", "Stories/Story_d1.xml", "Stories/Story_d2.xml"):
            self.assertEqual(before[n], after[n], n)
        self.assertIn("d2", re.search(r'StoryList="([^"]*)"', after["designmap.xml"].decode()).group(1).split())
        for n, b in after.items():
            if n.endswith(".xml"):
                xml.dom.minidom.parseString(b)

    def test_idempotent(self):
        build(self.p("in.idml"))
        run(self.p("in.idml"), self.p("once.idml"))
        log, missing, warn, left = run(self.p("once.idml"), self.p("twice.idml"))
        once, twice = read(self.p("once.idml"))[0], read(self.p("twice.idml"))[0]
        self.assertEqual(missing, [])
        self.assertEqual(texts(once), texts(twice))
        self.assertEqual(once["Spreads/Spread_se.xml"], twice["Spreads/Spread_se.xml"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
