"""Verify that a completed main run resumes without changing sealed evidence."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.calibration.storage import sha, write_json

ROOT = Path(__file__).resolve().parents[1]


def snapshot(base):
    cases = sorted(base.glob('K*/[ABC]/*/COMPLETE'))
    if len(cases) != 15000:
        raise RuntimeError(f'Full run required, found {len(cases)} complete cases')
    files = [base / 'summary.json', base / 'run.json', base / 'finished.json', base / 'progress.jsonl']
    files.extend(cases)
    files.extend(p.parent / 'evidence.sha256.json' for p in cases)
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    output = ROOT / 'results/calibration' / args.run_id
    before = snapshot(output / 'main')
    write_json(output / 'main_resume_before.json', before)
    command = [sys.executable, '-m', 'src.calibration.run', '--run-id', args.run_id, '--workers', '2', '--resume']
    log_path = output / 'main_resume.log'
    with log_path.open('x', encoding='utf-8') as stream:
        result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    after = snapshot(output / 'main')
    write_json(output / 'main_resume_after.json', after)
    events = [json.loads(line) for line in log_path.read_text().splitlines() if line.startswith('{')]
    queued = [e['queued'] for e in events if 'queued' in e]
    passed = result.returncode == 0 and before == after and queued == [0] * 5 and events[-1]['finished'] == 15000
    write_json(output / 'main_resume_verification.json', {
        'command': command, 'exit_code': result.returncode,
        'before_snapshot_sha256': sha(output / 'main_resume_before.json'),
        'after_snapshot_sha256': sha(output / 'main_resume_after.json'),
        'log_sha256': sha(log_path), 'completed_cases': 15000,
        'queued_repetitions_by_candidate': queued,
        'all_complete_and_manifest_hashes_unchanged': before == after,
        'summary_run_identity_finish_progress_unchanged': before == after,
        'passed': passed,
    })
    print(json.dumps({'passed': passed, 'queued': queued, 'completed': 15000}))
    raise SystemExit(0 if passed else 1)
