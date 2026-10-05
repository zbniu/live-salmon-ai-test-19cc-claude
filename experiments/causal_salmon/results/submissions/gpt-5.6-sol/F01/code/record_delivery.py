"""Record the observed optional persistence failure and recheck local delivery.

No analysis is rerun. The error note below comes from the upload helper tool
result and is not represented as captured subprocess stdout or stderr.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import zipfile

root = Path(__file__).resolve().parents[1]
archive = root.parent / 'submission.zip'
with (root / 'run_log.txt').open('a', encoding='utf-8') as handle:
    handle.write(datetime.now(timezone.utc).isoformat() +
        ' Optional persistence helper invoked after local delivery verification: '
        'python3 .../library/scripts/library_upload.py with report and archive paths. '
        'Tool returned exit=1: library upload failed: could not read Codex auth from '
        '/root/.codex/auth.json. This is a note of the observed tool result; '
        'its raw terminal record was not separately captured in a file. '
        'No upload or analysis retry. Local downloadable files remain available.\n')
    handle.write(datetime.now(timezone.utc).isoformat() +
        ' START code/record_delivery.py: preserve optional persistence error in log, '
        'refresh archive, and verify local report and archive again; no analysis rerun.\n')
report = (root / 'final_report.md').read_text(encoding='utf-8')
assert report.strip() and 'Neither the sign nor the average size' in report
with (root / 'run_log.txt').open('a', encoding='utf-8') as handle:
    handle.write(datetime.now(timezone.utc).isoformat() +
        ' Report readback confirmed nonempty and contains intended causal answer. '
        'Archive refresh follows, with CRC and member inspection below.\n')
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(root.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            zf.write(path, path.relative_to(root.parent).as_posix())
with zipfile.ZipFile(archive) as zf:
    assert zf.testzip() is None
    assert zf.read('submission/final_report.md').decode('utf-8') == report
    names = zf.namelist()
    assert all(any(n.startswith(prefix) for n in names) for prefix in
               ['submission/code/', 'submission/results/'])
    assert 'submission/run_log.txt' in names
    assert b'Optional persistence helper' in zf.read('submission/run_log.txt')
print(json.dumps({'final_report_readback_verified': True,
                  'archive_integrity_verified': True,
                  'report_code_results_execution_log_present': True,
                  'persistence_failure_record_present': True,
                  'members': names}, indent=2))
