"""Capture actual execution, validate report, package, and inspect delivery.

Usage: bundled_python submission/code/run_pipeline.py
This runner preserves earlier logs if invoked again; it never erases errors.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
OUT = ROOT / "results"
LOG = ROOT / "run_log.txt"

def record(message):
    with LOG.open("a", encoding="utf-8") as stream:
        stream.write(f"{datetime.now(timezone.utc).isoformat()} {message}\n")

if not LOG.exists():
    record("Pre-analysis: source description and CSV head/line count inspected through exec tool; exit 0. Original console output is in the session tool transcript, not saved as a separate results file. No analysis had yet been executed.")
    record("Pre-analysis: two supplied files copied unchanged with cp into submission/inputs/data.csv and submission/inputs/STUDY_DESCRIPTION.md; exit 0. No external study sources used.")

record("Runner started: " + sys.executable + " submission/code/run_pipeline.py")
command = [sys.executable, str(ROOT / "code" / "analyze.py")]
record("EXECUTE " + json.dumps(command))
result = subprocess.run(command, cwd=WORKSPACE, capture_output=True, text=True)
(OUT / "analysis_stdout.txt").write_text(result.stdout, encoding="utf-8")
(OUT / "analysis_stderr.txt").write_text(result.stderr, encoding="utf-8")
record(f"EXIT {result.returncode}; stdout -> results/analysis_stdout.txt; stderr -> results/analysis_stderr.txt")
print(result.stdout, end="")
if result.stderr:
    print(result.stderr, file=sys.stderr, end="")
if result.returncode:
    record("Analysis failed; report/archive not claimed. All captured records retained.")
    sys.exit(result.returncode)
record("Outputs: results/group_summary.csv, associations.csv, score_bin_summary.csv, counterfactual_completions.csv, analysis_summary.json; final_report.md. These were produced by the actual analysis execution.")

report_path = ROOT / "final_report.md"
report_bytes = report_path.read_bytes()
report = report_bytes.decode("utf-8")
assert report.strip()
assert "does not establish whether tutoring increased" in report
assert "No numerical point estimate is adopted" in report
assert "finite-study average causal effect can range" in report
assert all((ROOT / "code" / name).is_file() for name in ["analyze.py", "run_pipeline.py"])
assert (OUT / "analysis_summary.json").is_file()
record("PASS: report read back as nonempty UTF-8; intended causal conclusion and numerical bounds present. Executed code and outputs exist.")

checks = {"report_utf8_nonempty": True, "report_bytes": len(report_bytes),
          "report_sha256": hashlib.sha256(report_bytes).hexdigest(),
          "intended_answer_present": True,
          "actual_analysis_returncode": result.returncode,
          "analysis_executions_in_this_pipeline_invocation": 1,
          "expected_archive_members": sorted(
              str(p.relative_to(WORKSPACE)) for p in ROOT.rglob("*") if p.is_file())
              + ["submission/results/delivery_checks.json"]}
(OUT / "delivery_checks.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")

archive = WORKSPACE / "submission.zip"
def pack():
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ROOT.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=str(path.relative_to(WORKSPACE)))

record("EXECUTE packaging and archive inspection in code/run_pipeline.py; report validation -> results/delivery_checks.json.")
pack()
with zipfile.ZipFile(archive) as zf:
    assert zf.testzip() is None
    members = zf.namelist()
    assert "submission/final_report.md" in members
    assert "submission/run_log.txt" in members
    assert any(n.startswith("submission/code/") for n in members)
    assert any(n.startswith("submission/results/") for n in members)
    assert zf.read("submission/final_report.md") == report_bytes
record(f"PASS: submission.zip inspected: {len(members)} files; report, code, results, run log present; CRCs valid; archived report equals read-back report.")
record("Archive refreshed once to include this verification record; no statistical analysis rerun. No analysis errors or missing analysis outputs.")
pack()
with zipfile.ZipFile(archive) as zf:
    assert zf.testzip() is None
    assert zf.read("submission/final_report.md") == report_bytes
    assert zf.read("submission/run_log.txt") == LOG.read_bytes()
    print("Verified final archive members:")
    print("\n".join(zf.namelist()))
print(f"Final archive size: {archive.stat().st_size} bytes")
