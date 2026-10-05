"""Artifact adapter for independently serialized evidence manifests.

This is comparison-only code registered separately from the frozen simulation
programs; it imports no independent generator or statistics.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.reporting import compare
from src.calibration.storage import sha


def validate_case(case):
    case=Path(case)
    manifest_path=case/'evidence.sha256.json'
    if sha(manifest_path)!=(case/'COMPLETE').read_text().strip():
        return False
    manifest=json.loads(manifest_path.read_text())
    if 'case_files' in manifest:
        local=manifest['case_files']
        quality=manifest['quality_files']
        return all((case/name).is_file() and sha(case/name)==digest for name,digest in local.items()) and all((compare.ROOT/name).is_file() and sha(compare.ROOT/name)==digest for name,digest in quality.items())
    return compare.verified_manifest(case)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--output-name',default='comparison.json')
    args=parser.parse_args()
    original=compare.verified_manifest
    def adapter(case):
        manifest=json.loads((Path(case)/'evidence.sha256.json').read_text())
        return validate_case(case) if 'case_files' in manifest else original(case)
    compare.verified_manifest=adapter
    output=compare.compare_run(args.run_id,args.output_name)
    print(json.dumps({'passed':output['passed'],'checked':output['repetitions_checked'],'mismatches':len(output['mismatches'])}))
    raise SystemExit(0 if output['passed'] else 1)
