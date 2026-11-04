"""Private warmer entry point using the proven exact frozen geometry predicate."""
import json
from pathlib import Path
from fast_supplemental_validation import install
import warm_supplemental


def main():
    backend=install();print('Exact fast validation backend '+json.dumps(backend,sort_keys=True),flush=True)
    warm_supplemental.main()

if __name__=='__main__':main()
