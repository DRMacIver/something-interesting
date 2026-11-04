"""Review the detailed SVG conversion independently of the production font."""
import argparse
import json
from emoji_svg import ROOT,RECIPES,convert


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codepoint', choices=sorted(RECIPES), default='1f930')
    parser.add_argument('--pixels', type=int, choices=[384, 768, 1024], default=768)
    parser.add_argument('--stroke', type=float, default=1.3)
    args = parser.parse_args()
    if not 1 <= args.stroke <= 3: parser.error('stroke must be between 1 and 3')
    image, report = convert(args.pixels, args.stroke, args.codepoint)
    report['status']='standalone conversion review'
    output = ROOT/f'output/font-review/pen-translation/detailed-svg-{args.codepoint}-{args.pixels}-{args.stroke:g}.png'
    image.save(output)
    output.with_suffix('.json').write_text(json.dumps(report, indent=2)+'\n')
    print(output)
    print({k:report[k] for k in ['appliedStrength','fallback','sourceComponents','sourceHoles']})


if __name__ == '__main__': main()
