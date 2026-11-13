"""Ask Codex's image generation for whole-scene candidates for a panel.

    uv run tools/extensions/graft/generate.py PANEL OUT_DIR [--count 6] [--pose NAME]

Each candidate is a complete redrawing of the scene, guided by the scan
placed on a blank frame at the size it should have in the result. Nothing
is asked to stay pixel-exact: `graft.py` fits the drawing to the scan
afterwards. Needs the `codex` CLI; each image takes a few minutes, and four
run at a time.
"""
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
LOCKED = HERE.parent / 'reconstruction-v2'
FRAME = (1536, 1024)  # what the image tool returns

# rows of empty paper to cut from the scan's top, the scale at which the
# rest is shown on the frame, where it goes, and the poses to ask for
PANELS = {
    1: dict(top=0, scale=0.46, at=(420, 40), poses=['walk'], reference=False),
    2: dict(top=700, scale=0.5, at=(330, 50), poses=['kneel', 'crouch'], reference=True),
    3: dict(top=1000, scale=0.42, at=(260, 25), poses=['kneel', 'oneknee'], reference=True),
}


def prepare(panel, out):
    """The images each prompt refers to, written into `out`."""
    spec = PANELS[panel]
    scan = Image.open(LOCKED / f'locked-{panel}.png').convert('L')
    art = scan.crop((0, spec['top'], scan.width, scan.height))
    frame = Image.new('L', FRAME, 255)
    small = art.resize((round(art.width * spec['scale']), round(art.height * spec['scale'])), Image.LANCZOS)
    frame.paste(small, spec['at'])
    frame.save(out / f'p{panel}-placement.png')
    closeup = art.copy()
    closeup.thumbnail((1400, 1400))
    closeup.save(out / f'p{panel}-closeup.png')
    inputs = [f'p{panel}-placement.png', f'p{panel}-closeup.png']
    if spec['reference']:
        reference = Image.open(LOCKED / 'locked-1.png').convert('L')
        reference.thumbnail((1024, 1024))
        reference.save(out / 'panel1-reference.png')
        inputs.append('panel1-reference.png')
        # his legs and shoes large: words alone get shoes a third too small
        legs = Image.open(LOCKED / 'locked-1.png').convert('L').crop((0, 930, 760, 2066))
        legs.save(out / 'legs-reference.png')
        inputs.append('legs-reference.png')
    return inputs


def prompt(panel, pose, name):
    parts = [(HERE / 'prompts' / f'p{panel}-head.txt').read_text()]
    pose_file = HERE / 'prompts' / f'p{panel}-pose-{pose}.txt'
    if pose_file.exists():
        parts.append(pose_file.read_text())
    parts.append((HERE / 'prompts' / 'style.txt').read_text().replace('OUTNAME', name))
    return '\n'.join(parts)


def generate(out, inputs, text, stem):
    (out / f'{stem}.prompt.txt').write_text(text)
    command = ['codex', 'exec', '--skip-git-repo-check', '-s', 'workspace-write', '-C', '.']
    for name in inputs:
        command += ['-i', name]
    command += ['-o', f'{stem}.reply.txt', '--', text]
    # stdin must be closed or codex waits on it for ever
    with open(out / f'{stem}.log', 'w') as log:
        subprocess.run(command, cwd=out, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
    return stem, (out / f'{stem}.png').exists()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('panel', type=int, choices=sorted(PANELS))
    ap.add_argument('out', type=Path)
    ap.add_argument('--count', type=int, default=6, help='candidates per pose')
    ap.add_argument('--pose', action='append', help='only these poses')
    ap.add_argument('--start', type=int, default=1, help='number of the first candidate')
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    inputs = prepare(args.panel, args.out)
    jobs = []
    for pose in args.pose or PANELS[args.panel]['poses']:
        for i in range(args.start, args.start + args.count):
            stem = f'p{args.panel}-{pose}-{i}'
            jobs.append((args.out, inputs, prompt(args.panel, pose, f'{stem}.png'), stem))
    with ThreadPoolExecutor(max_workers=4) as pool:
        for stem, made in pool.map(lambda job: generate(*job), jobs):
            print(stem, 'ok' if made else 'FAILED (see its .log)')


if __name__ == '__main__':
    main()
