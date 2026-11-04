"""Independent native-reference checks for the holding-hands candidates."""
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/font'))
from holding_hands_sources import validate_sources
from prototype_holding_hands_svg import RECIPES, prepare


def test_all_native_tone_references():
    spec = json.loads((ROOT / 'docs/holding-hands-emoji-svg-source-probe.json').read_text())
    reports = validate_sources(ROOT, spec['files'], RECIPES)
    assert len(reports) == 4
    assert sum(report['variants'] for report in reports) == 104


@pytest.mark.parametrize('key', RECIPES)
def test_skin_masks_follow_anatomy(key):
    (white, left, right, ink), report = prepare(key)
    padding = report['padding']
    def sample(mask, x, y):
        return bool(mask[round(y * 12) + padding, round(x * 12) + padding])
    # Interior forehead points distinguish the two people independently of palette.
    assert sample(left, 36, 25) and not sample(right, 36, 25)
    assert sample(right, 92, 25) and not sample(left, 92, 25)
    # Clothes must stay paper-white, and hair must remain ink, for every tone pair.
    for x in (36, 92):
        for material_x, y in ((x, 60), (x - 6, 100)):
            assert sample(white, material_x, y)
            assert not sample(left, material_x, y) and not sample(right, material_x, y)
            assert not sample(ink, material_x, y)
        assert sample(ink, x, 16)
        assert not sample(left, x, 16) and not sample(right, x, 16)
