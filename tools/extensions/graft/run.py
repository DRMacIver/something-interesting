"""Graft candidate drawings onto a panel's scan and rank them.

    uv run tools/extensions/graft/run.py PANEL OUT_DIR CANDIDATE.png...

PANEL is 1, 2 or 3. Each candidate gets OUT_DIR/<name>.png (the export-size
panel) and <name>.json (its fit report). `sheet.py` turns a directory of
these into a ranked contact sheet.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import graft  # noqa: E402

LOCKED = Path(__file__).resolve().parent.parent / 'reconstruction-v2'

# paper around each scan crop (scan px) and the empty rows above the art
FRAMES = {
    1: graft.Frame(left=250, right=0, below=0),
    2: graft.Frame(left=450, right=450, below=500, skip=350),
    3: graft.Frame(left=450, right=650, below=800, skip=500),
}


def one(job):
    panel, out, path = job
    scan = Image.open(LOCKED / f'locked-{panel}.png')
    image, report = graft.graft(scan, Image.open(path), FRAMES[panel])
    stem = Path(path).stem
    image.save(Path(out) / f'{stem}.png')
    data = dict(report.as_dict(), candidate=str(path), panel=panel, left=FRAMES[panel].left * 2)
    (Path(out) / f'{stem}.json').write_text(json.dumps(data, indent=1))
    return stem, data


def main():
    panel, out, paths = int(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]
    out.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=6) as pool:
        for stem, data in pool.map(one, [(panel, out, p) for p in paths]):
            print(f"{stem}: fit {data['fit_warped']:.2f} (rigid {data['fit_rigid']:.2f}), "
                  f"scale {data['scale']:.2f}, edges {data['edges_matched']} matched "
                  f"{data['edges_lost']} lost {data['edges_extra']} extra, "
                  f"weight {data['weight_before']:.1f}->{data['weight_after']:.1f} "
                  f"(scan {data['weight_scan']:.1f})" + (' CLIPPED' if data['clipped'] else ''))


if __name__ == '__main__':
    main()
