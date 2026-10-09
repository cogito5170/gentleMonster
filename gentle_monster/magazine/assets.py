"""Asset catalogue. Finding an image and being allowed to publish it are two different facts, kept in two fields.

Every asset carries the full metadata set (FIELDS). publishable() is the only door to the page:
  rights_status in CLEARED  and  the file is really on disk  and  verification_status == 'verified'.
Everything else is a research reference: it may be cited (title, URL) but its picture is not printed -- the
page shows a 'withheld' slot with the citation instead. Nothing is approved automatically.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

FIELDS = ("asset_id", "source_title", "source_url", "direct_image_url", "creator", "publication_date", "asset_type",
          "license", "attribution", "local_path", "dimensions", "retrieval_status", "rights_status",
          "verification_status", "related_research_items")
CLEARED = ("own", "generated", "licensed", "public_domain", "cc0", "cc-by")
RETRIEVAL = ("retrieved", "generated", "provided", "not_attempted", "blocked", "failed")
TYPES = ("official_campaign", "editorial", "independent_photography", "reference_page", "generated_plate", "user_photo")


def _id(*parts) -> str:
    return "A-" + hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:10]


def blank(**kw) -> dict:
    a = {f: None for f in FIELDS}
    a["related_research_items"] = []
    a.update(kw)
    return a


def publishable(a: dict) -> bool:
    return (a.get("rights_status") in CLEARED and a.get("verification_status") == "verified"
            and bool(a.get("local_path")) and Path(a["local_path"]).is_file())


def problems(a: dict) -> list[str]:
    bad = [f"{a.get('asset_id')}: missing field {f}" for f in FIELDS if f not in a]
    if a.get("retrieval_status") not in RETRIEVAL:
        bad.append(f"{a.get('asset_id')}: retrieval_status '{a.get('retrieval_status')}'")
    if a.get("asset_type") not in TYPES:
        bad.append(f"{a.get('asset_id')}: asset_type '{a.get('asset_type')}'")
    if a.get("rights_status") in CLEARED and not a.get("attribution"):
        bad.append(f"{a.get('asset_id')}: cleared but no attribution line")
    return bad


def from_sources(cat: dict) -> list[dict]:
    """Every catalogued source page becomes a reference asset. Its image was not fetched (the network here
    blocks the brand and magazine sites), so rights are 'unknown' and it is never printed as a picture."""
    out = []
    for s in cat["sources"]:
        official = s.get("kind") == "official"
        out.append(blank(
            asset_id=_id("src", s["id"]), source_title=s.get("title"), source_url=s.get("url"), direct_image_url=None,
            creator=s.get("publisher"), publication_date=s.get("date"),
            asset_type="official_campaign" if official else ("editorial" if s.get("kind") == "press" else "reference_page"),
            license=None, attribution=s.get("publisher"), local_path=None, dimensions=None,
            retrieval_status="blocked", rights_status="unknown", verification_status="unverified",
            related_research_items=[s["id"]] + [c["id"] for c in cat["claims"] if s["id"] in c.get("source_ids", [])]))
    return out


def _dims(p: Path):
    if not p.is_file():
        return None
    b = p.read_bytes()[:64 * 1024]
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", b[16:24]); return [w, h]
    if b[:2] == b"\xff\xd8":
        i = 2
        while i < len(b) - 9:
            if b[i] != 0xFF:
                i += 1; continue
            m = b[i + 1]
            if m in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", b[i + 5:i + 9]); return [w, h]
            i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    if p.suffix == ".svg":
        import re
        m = re.search(rb'viewBox="0 0 (\d+) (\d+)"', b)
        if m:
            return [int(m.group(1)), int(m.group(2))]
    return None


def user_image(path: str, credit: str, rights: str, title: str = "") -> dict:
    """A photo the user supplies. The user's word is the rights record -- it is written down as such."""
    p = Path(path)
    ok = p.is_file()
    return blank(asset_id=_id("user", p.resolve()), source_title=title or p.name, source_url=None, direct_image_url=None,
                 creator=credit, asset_type="user_photo", license=rights, attribution=credit, local_path=str(p.resolve()),
                 dimensions=_dims(p) if ok else None, retrieval_status="provided" if ok else "failed",
                 rights_status=rights if rights in CLEARED else "unknown",
                 verification_status="verified" if ok and rights in CLEARED else "unverified",
                 rights_note="declared by the user on the command line")


def generated(path: Path, kind: str, hyp_id: str) -> dict:
    there = Path(path).is_file()
    return blank(asset_id=_id("gen", path.name), source_title=f"{kind} plate", source_url=None, direct_image_url=None,
                 creator="this system (generated drawing)", asset_type="generated_plate", license="generated by this tool",
                 attribution="Generated drawing -- not a photograph", local_path=str(path), dimensions=_dims(path),
                 retrieval_status="generated" if there else "failed", rights_status="generated",
                 verification_status="verified" if there else "unverified", related_research_items=[hyp_id])


def save(assets: list, path) -> None:
    Path(path).write_text(json.dumps(assets, ensure_ascii=False, indent=1), encoding="utf-8")
