"""The documented public audit must work and reject changed public evidence."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def audit(root):
    return subprocess.run(
        [sys.executable, '-m', 'scripts.audit_data', '--public-only'],
        cwd=root, capture_output=True, text=True,
    )


def test_public_audit_accepts_published_layout():
    result = audit(ROOT)
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary['public_package_verified'] is True
    assert summary['selected_datasets'] == 12
    assert summary['original_artifacts'] == 915


@pytest.mark.parametrize('name', [
    'planning.md',
    'datasets/public/formal/formal-A-740001/data.csv',
])
def test_public_audit_rejects_changed_evidence(tmp_path, name):
    manifest = json.loads((ROOT/'manifests/submission_manifest.json').read_text())
    for relative in [*manifest['files'], 'manifests/submission_manifest.json']:
        destination = tmp_path/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/relative, destination)
    target = tmp_path/name
    target.write_bytes(target.read_bytes()+b'\nmodified evidence\n')
    result = audit(tmp_path)
    assert result.returncode != 0
    assert f'Changed public file: {name}' in result.stderr
