"""Read/snapshot exactly the ten requested inputs; never rewrite their sources."""
from pathlib import Path
import hashlib
import json
import shutil

REV = Path(__file__).resolve().parent
ROOT = REV.parents[1]
INPUTS = [
    'CURRENT_STATUS_structural_exploration_2026-11-03.md', 'STRUCTURAL_PRIVACY_2026-11-03.md',
    'EXPLORATION_SCREEN_2026-11-03.md', 'construction/structural_masks.py',
    'construction/structural_checker.py', 'construction/validate_structural.py',
    'results/structural_delivery01/manifest.json', 'RANK_PRIVACY_TRADEOFF_2026-11-03.md',
    'SEED_REPAIR_2026-11-03.md', 'SOURCE_BINDING_2026-11-03.md']


def main():
    destination = REV / 'inputs'; destination.mkdir(exist_ok=False)
    receipt = []
    for name in INPUTS:
        data = (ROOT / name).read_bytes(); data.decode('utf-8')
        target = destination / name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        receipt.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    manifest = json.loads((destination / INPUTS[6]).read_text())
    summary = {'inputs': receipt, 'all_ten_read': len(receipt) == 10,
               'manifest_keys': list(manifest), 'manifest_history_entries': len(manifest['historical_files']),
               'prior_completion_flags_are_claims_not_new_verification': True,
               'write_scope': str(REV), 'protected_mainline': 'auth-lifecycle'}
    (REV / 'input_receipt.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps({'inputs': len(receipt), 'bytes_read': sum(x['bytes'] for x in receipt),
                      'manifest_rows_parsed': summary['manifest_history_entries']}))


if __name__ == '__main__': main()
