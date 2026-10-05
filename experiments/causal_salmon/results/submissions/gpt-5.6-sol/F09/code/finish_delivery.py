"""Record the actual ancillary save error and refresh/inspect the package."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[2]
sub = root / 'submission'
with (sub / 'run_log.txt').open('a', encoding='utf-8') as f:
    f.write('\nAncillary persistence attempt after finalization: python3 /root/.codex/plugins/cache/openai-curated-remote/openai-library/0.1.61/skills/library/scripts/library_upload.py, with report and zip as creates on stdin.\n')
    f.write('Exit 1; actual error: library upload failed: could not read Codex auth from /root/.codex/auth.json. No upload request was started. Local deliverables remain intact.\n')
    f.write('Finalizer stdout (report readback and successful final archive inspection) was displayed in the session tool output, not captured as a separate stdout file; its substantive checks are recorded in results/delivery_verification.json. Finalizer exit code was 0.\n')
    f.write('Executed code/finish_delivery.py to record this error and refresh/inspect the archive; no statistical analysis rerun.\n')
report = (sub / 'final_report.md').read_text(encoding='utf-8')
assert report.strip() and 'No numerical causal effect is adopted.' in report
assert '5.464 points' in report
with zipfile.ZipFile(root / 'submission.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(sub.rglob('*')):
        if p.is_file():
            z.write(p, p.relative_to(root).as_posix())
with zipfile.ZipFile(root / 'submission.zip') as z:
    assert z.testzip() is None
    names = z.namelist()
    for required in ['submission/final_report.md', 'submission/run_log.txt',
                     'submission/code/analyze.py', 'submission/results/analysis.json']:
        assert required in names
    for p in sub.rglob('*'):
        if p.is_file():
            assert z.read(p.relative_to(root).as_posix()) == p.read_bytes()
    assert z.read('submission/final_report.md').decode('utf-8') == report
print('Report readback: nonempty UTF-8; intended conclusion and numerical descriptive result confirmed.')
print('Final archive CRC, required report/code/results/log entries, and all file-byte comparisons passed.')
print('\n'.join(names))
