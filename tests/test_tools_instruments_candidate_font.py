"""Fine strings survive the actual candidate font's integer contour grid."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from prototype_tools_instruments import prepare
from svg_counter_review import review_counters


def test_compiled_banjo_keeps_all_thirty_six_larger_source_counters():
    folder=ROOT/'output/font-review/pen-translation'
    report=json.loads((folder/'tools-instruments-candidate.json').read_text())
    path=folder/'tools-instruments-candidate.woff2'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
    font=TTFont(path)
    (paper,*_,ink),r=prepare('1fa95')
    ys,xs=np.nonzero(paper)
    transform=xs.min(),ys.min(),760/max(np.ptp(xs)+1,np.ptp(ys)+1)
    actual=review_counters(ink,transform,font['glyf']['tools-instruments.1fa95'],max_small_losses=1)
    expected=next(e for e in report['flags'] if e['region']=='1fa95')['penTreatment']['fontCounterReview']
    assert actual==expected
    assert actual['largeCountersChecked']==36 and actual['smallCounterLosses']==1
