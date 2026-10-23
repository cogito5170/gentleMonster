"""층이 있는 포토샵 파일(.psd, 8비트 RGB) 쓰기 — 외부 라이브러리 없이 Adobe 파일 형식 문서대로.

  write_psd(path, W, H, layers, composite, dpi=300)
    layers    : 아래에서 위로 [(이름, RGBA PIL 이미지(쪽 크기), 보임 bool), …] — 층마다 투명한 테두리는 잘라 낸다
    composite : 합친 RGB 이미지(쪽 크기) — 포토샵이 아닌 보기 프로그램이 보여 주는 그림
채널은 PackBits(RLE) 압축. 층 이름은 유니코드('luni')로도 넣어 한글이 그대로 보인다.
"""
import struct

import numpy as np


def _packbits_row(row):
    """한 줄을 PackBits 로. 같은 값 3개 이상은 반복 묶음, 나머지는 글자 그대로 묶음(최대 128)."""
    n = len(row)
    if n == 0:
        return b''
    change = np.flatnonzero(np.diff(row)) + 1
    starts = np.concatenate(([0], change))
    lens = np.diff(np.concatenate((starts, [n])))
    out = bytearray()
    lit_start = None
    raw = row.tobytes()

    def flush_lit(a, b):
        while a < b:
            k = min(128, b - a)
            out.append(k - 1)
            out.extend(raw[a:a + k])
            a += k

    for s, ln in zip(starts.tolist(), lens.tolist()):
        if ln >= 3:
            if lit_start is not None:
                flush_lit(lit_start, s)
                lit_start = None
            v = raw[s]
            while ln > 0:
                k = min(128, ln)
                if k >= 2:
                    out.append((257 - k) & 0xFF)
                    out.append(v)
                else:
                    out.append(0)
                    out.append(v)
                ln -= k
        elif lit_start is None:
            lit_start = s
    if lit_start is not None:
        flush_lit(lit_start, n)
    return bytes(out)


def _rle_channel(a):
    """2차원 uint8 → (줄 길이 표 + 압축 자료). 앞에 압축 방식(1) 두 바이트는 부르는 쪽이 붙인다."""
    rows = [_packbits_row(r) for r in a]
    return struct.pack(f'>{len(rows)}H', *[len(r) for r in rows]) + b''.join(rows)


def _pascal(name, pad=4):
    b = name.encode('ascii', 'replace')[:255]
    s = bytes([len(b)]) + b
    while len(s) % pad:
        s += b'\0'
    return s


def write_psd(path, W, H, layers, composite, dpi=300):
    recs, chans = b'', b''
    count = 0
    for name, im, visible in layers:
        a = np.asarray(im.convert('RGBA'))
        alpha = a[..., 3]
        ys, xs = np.nonzero(alpha)
        if len(ys) == 0:
            continue
        t, l, b, r = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
        crop = a[t:b, l:r]
        data = {}
        for cid, ch in ((-1, 3), (0, 0), (1, 1), (2, 2)):
            data[cid] = struct.pack('>H', 1) + _rle_channel(np.ascontiguousarray(crop[..., ch]))
        rec = struct.pack('>4iH', int(t), int(l), int(b), int(r), 4)
        for cid in (-1, 0, 1, 2):
            rec += struct.pack('>hI', cid, len(data[cid]))
        flags = 0 if visible else 2
        rec += b'8BIMnorm' + struct.pack('>BBBB', 255, 0, flags, 0)
        uni = name.encode('utf-16-be')
        luni = struct.pack('>I', len(name)) + uni
        if len(luni) % 2:
            luni += b'\0'
        extra = struct.pack('>I', 0) + struct.pack('>I', 0) + _pascal(name) + b'8BIMluni' + struct.pack('>I', len(luni)) + luni
        rec += struct.pack('>I', len(extra)) + extra
        recs += rec
        chans += b''.join(data[c] for c in (-1, 0, 1, 2))
        count += 1
    li = struct.pack('>h', count) + recs + chans      # 합친 그림에 알파 채널이 없으므로 양수
    if len(li) % 2:
        li += b'\0'
    layer_info = struct.pack('>I', len(li)) + li
    lmi = layer_info + struct.pack('>I', 0)  # 전체 마스크 정보 없음
    # 해상도 정보(자원 1005): dpi 를 16.16 고정소수로
    res = struct.pack('>IHHIHH', dpi << 16, 1, 1, dpi << 16, 1, 1)
    irb = b'8BIM' + struct.pack('>H', 1005) + b'\0\0' + struct.pack('>I', len(res)) + res
    out = bytearray()
    out += b'8BPS' + struct.pack('>H', 1) + b'\0' * 6 + struct.pack('>HIIHH', 3, H, W, 8, 3)
    out += struct.pack('>I', 0)                       # 색상 모드 자료 없음
    out += struct.pack('>I', len(irb)) + irb
    out += struct.pack('>I', len(lmi)) + lmi
    c = np.asarray(composite.convert('RGB'))
    planes = [np.ascontiguousarray(c[..., k]) for k in range(3)]
    rows = [[_packbits_row(r) for r in p] for p in planes]
    out += struct.pack('>H', 1)
    out += b''.join(struct.pack(f'>{H}H', *[len(r) for r in pr]) for pr in rows)
    out += b''.join(b''.join(pr) for pr in rows)
    with open(path, 'wb') as f:
        f.write(out)
    return count
