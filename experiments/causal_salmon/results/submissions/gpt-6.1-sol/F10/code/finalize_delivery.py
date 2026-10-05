"""Preserve post-analysis delivery records and repackage without rerunning analysis."""
from datetime import datetime, timezone
from pathlib import Path
import json
import zipfile

root = Path(__file__).resolve().parents[1]
workspace = root.parent
log = root / "run_log.txt"
def record(message):
    with log.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()} {message}\n")

record("Post-analysis delivery: library_upload.py invoked for report and zip; exit 1 before uploads began: could not read Codex auth from /root/.codex/auth.json. Original error output remains in the session tool transcript; no separate raw helper stdout/stderr file was captured. This was a delivery error, not an analysis failure.")
record("Post-analysis delivery: available platform create-file tool then saved both files successfully; returned status succeeded for each. No external connectors accessed. Metadata helper succeeded for both original local paths.")
record("Execution-message correction: analysis_stdout.txt says six analysis output files in results; the analysis wrote five data-result files and the report. The original stdout is retained unchanged. The runner additionally captured stdout/stderr and wrote delivery checks.")
record("EXECUTE code/finalize_delivery.py: preserve delivery records, read report, and repackage. Statistical analysis is not rerun.")

report_bytes = (root / "final_report.md").read_bytes()
report = report_bytes.decode("utf-8")
assert report.strip() and "does not establish whether tutoring increased" in report
assert "-19.827 to 80.173 points" in report
archive = workspace / "submission.zip"
members = sorted(str(p.relative_to(workspace)) for p in root.rglob("*") if p.is_file())
check = {"report_read_back_nonempty_utf8": True, "intended_answer_verified": True,
         "analysis_was_not_rerun": True, "archive_members": members + ["submission/results/final_archive_check.json"]}
(root / "results" / "final_archive_check.json").write_text(json.dumps(check, indent=2) + "\n", encoding="utf-8")
record("PASS: report read back, nonempty UTF-8, intended answer and bounds present; package contains executed code, original analysis outputs and execution log.")
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            zf.write(path, str(path.relative_to(workspace)))
with zipfile.ZipFile(archive) as zf:
    assert zf.testzip() is None
    assert zf.read("submission/final_report.md") == report_bytes
    assert zf.read("submission/run_log.txt") == log.read_bytes()
    assert any(n.startswith("submission/code/") for n in zf.namelist())
    assert any(n.startswith("submission/results/") for n in zf.namelist())
    print("Final archive read-back inspection passed:")
    print("\n".join(zf.namelist()))
print("Report nonempty and intended conclusion verified; no analyses rerun.")
