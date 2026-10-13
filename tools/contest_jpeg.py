"""공모전 제출용 JPG — 용량을 범위 안에 맞추고 sRGB 로 바꾸고 촬영 정보(EXIF)는 남긴다.

    python3 tools/contest_jpeg.py photos/puddle.jpg photos/bulb.tif
    python3 tools/contest_jpeg.py photos/*.jpg --max-mb 5 --min-mb 1 --long-edge 4000

결과는 out/contest/<이름>.jpg. 기본값은 Sony WPA 규격(1–5MB · sRGB · JPG).
RAF(후지 RAW)는 열지 못한다 — 카메라나 X RAW Studio · Lightroom 에서 먼저 JPG/TIFF 로 뽑는다.
"""
import argparse
import io
import sys
from pathlib import Path

from PIL import Image, ImageCms, ImageOps

MB = 1024 * 1024
SRGB = ImageCms.createProfile("sRGB")


def to_srgb(img):
    """내장 색 프로파일(Adobe RGB 등)이 있으면 sRGB 로 바꾼다. 없으면 sRGB 로 본다."""
    img = img.convert("RGB") if img.mode not in ("RGB", "CMYK") else img
    icc = img.info.get("icc_profile")
    if icc:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        img = ImageCms.profileToProfile(img, src, SRGB, outputMode="RGB")
    return img.convert("RGB")


def encode(img, quality, exif, icc):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality, subsampling=0 if quality >= 90 else 2,
             optimize=True, exif=exif, icc_profile=icc)
    return buf.getvalue()


def fit(img, exif, icc, lo, hi):
    """hi 이하에서 가장 높은 화질을 이분 탐색으로 찾는다. 화질 80 으로도 크면 화질을 더 깎지 않고 긴 변을 10% 줄인다."""
    while True:
        best = None
        a, b = 80, 100
        while a <= b:
            q = (a + b) // 2
            data = encode(img, q, exif, icc)
            if len(data) <= hi:
                best, a = (q, data), q + 1
            else:
                b = q - 1
        if best:
            q, data = best
            if len(data) < lo:
                return None, q, img, "최고 화질로도 하한보다 작다 — 원본 해상도가 낮다"
            return data, q, img, None
        w, h = img.size
        img = img.resize((int(w * 0.9), int(h * 0.9)), Image.LANCZOS)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("images", nargs="+")
    ap.add_argument("--max-mb", type=float, default=5.0)
    ap.add_argument("--min-mb", type=float, default=1.0)
    ap.add_argument("--long-edge", type=int, default=0, help="긴 변 픽셀(0 = 그대로)")
    ap.add_argument("--out", default="out/contest")
    args = ap.parse_args(argv)

    hi = int(args.max_mb * MB * 0.98)  # 사이트마다 MB 를 다르게 세니 2% 여유
    lo = int(args.min_mb * MB)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    icc = ImageCms.ImageCmsProfile(SRGB).tobytes()
    failed = 0
    for p in map(Path, args.images):
        try:
            src = Image.open(p)
        except Exception as e:  # RAF 등
            print(f"건너뜀 {p.name}: 열 수 없음 ({e.__class__.__name__}) — JPG/TIFF 로 먼저 뽑는다")
            failed += 1
            continue
        exif = src.getexif()
        img = to_srgb(ImageOps.exif_transpose(src))
        exif[0x0112] = 1  # 회전은 이미 픽셀에 반영했다
        if args.long_edge and max(img.size) > args.long_edge:
            img.thumbnail((args.long_edge, args.long_edge), Image.LANCZOS)
        data, q, img, err = fit(img, exif.tobytes(), icc, lo, hi)
        if err:
            print(f"실패 {p.name}: {err}")
            failed += 1
            continue
        dst = out / (p.stem + ".jpg")
        dst.write_bytes(data)
        print(f"{p.name} → {dst}  {len(data) / MB:.2f}MB  {img.size[0]}x{img.size[1]}  화질 {q}  sRGB")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
