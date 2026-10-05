"""Package existing records without rerunning analyses, then inspect the archive."""
from pathlib import Path
from datetime import datetime, timezone
import json, zipfile, hashlib

ROOT=Path(__file__).resolve().parents[2]
SUB=ROOT/'submission'; archive=ROOT/'submission.zip'; log=SUB/'run_log.txt'
validation_file=SUB/'results/archive_validation.json'
stdout_file=SUB/'results/package_submission_stdout.txt'

def record(line):
 with log.open('a',encoding='utf-8') as f: f.write(line+'\n')

def package():
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for p in sorted(SUB.rglob('*')):
   if p.is_file(): z.write(p,p.relative_to(ROOT))

def inspect():
 with zipfile.ZipFile(archive) as z:
  names=z.namelist()
  assert z.testzip() is None
  assert 'submission/final_report.md' in names
  assert 'submission/run_log.txt' in names
  assert any(n.startswith('submission/code/') for n in names)
  assert any(n.startswith('submission/results/') for n in names)
  assert len(names)==len(set(names))
  report=z.read('submission/final_report.md').decode('utf-8')
  assert report.strip() and '1.22 additional score points' in report
  assert report==(SUB/'final_report.md').read_text(encoding='utf-8')
  return names,report

record(f'\nSTART {datetime.now(timezone.utc).isoformat()}')
record('Command: bundled Python submission/code/package_submission.py')
record('Packages the existing files only; does not rerun statistical analyses.')
record('Outputs: submission.zip; results/archive_validation.json; results/package_submission_stdout.txt.')
# Initial package and genuine validation record, before final synchronization.
package(); names,report=inspect()
validation={'first_archive_crc_test_passed':True,
            'report_read_back_from_disk_and_archive':True,
            'report_nonempty':True,'report_matches_disk':True,
            'report_contains_adopted_att':True,
            'required_report_code_results_execution_record_present':True,
            'report_sha256':hashlib.sha256(report.encode()).hexdigest(),
            'initial_archive_members':names,
            'note':'These checks were executed on the first package. The archive is then refreshed to include this validation and completed records and checked again; final inspection is printed to the session tool record.'}
validation_file.write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
first_stdout='First package inspected successfully.\n'+json.dumps(validation,indent=2)+'\n'
stdout_file.write_text(first_stdout,encoding='utf-8')
record(f'END initial package validation {datetime.now(timezone.utc).isoformat()} exit_status=0')
record('Packaging stdout through the first inspection is saved in results/package_submission_stdout.txt.')
record('Final refresh includes completed execution records and initial validation; final inspection stdout is in the session tool record only, not reconstructed in the archived stdout file.')
package()
final_names,final_report=inspect()
assert 'submission/results/archive_validation.json' in final_names
assert 'submission/results/package_submission_stdout.txt' in final_names
print('FINAL ARCHIVE INSPECTION: CRC checks pass; report, executed code, actual results, and execution record present.')
print('Final report read back as UTF-8; nonempty; equals the archived report; adopted ATT 1.22 verified.')
print('ARCHIVE MEMBERS:\n'+'\n'.join(final_names))
print(f'final_report.md: {(SUB/"final_report.md").stat().st_size} bytes')
print(f'submission.zip: {archive.stat().st_size} bytes')
