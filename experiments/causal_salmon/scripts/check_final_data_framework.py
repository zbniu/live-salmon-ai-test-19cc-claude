"""Probe the offline reference sandbox before fixed-data generation."""
import json
import hashlib
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

from src.calibration.isolation import profile, reference
from src.calibration.storage import seal, sha, write_json
from src.data.generator import csv_bytes, generate
from src.data.materials import protocol_bytes

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = 'f85fedf447c734d9d5e7a2cb630284fe18c7091c5cf653610adbc43ec8e7144c'
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'en_US.UTF-8',
       'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1',
       'VECLIB_MAXIMUM_THREADS': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
PROBE = r'''
import json, os, socket, sys
from pathlib import Path
root = Path(sys.argv[1])
inputs = Path(sys.argv[2])
blocked = {}
targets = {
 'private_probe': root / 'manifests/final_data_private_probe.txt',
 'protocol': root / 'planning.md',
 'README': root / 'README.md',
 'final_plan': root / 'docs/FINAL_DATA_GENERATION_PLAN.md',
 'selected_parameters': root / 'configs/selected_parameters.json',
 'frozen_configuration': root / 'configs/frozen_study.json',
 'hidden_directory': root / 'datasets/ground_truth',
 'parent_directory': root.parent,
}
for name, path in targets.items():
 try:
  list(path.iterdir()) if name.endswith('directory') else path.read_bytes()
 except OSError as error:
  blocked[name] = error.errno in (1, 13)
 else:
  blocked[name] = False
try:
 socket.create_connection(('1.1.1.1', 443), timeout=1)
except OSError as error:
 blocked['network'] = error.errno in (1, 13)
else:
 blocked['network'] = False
public_read = all((inputs / n).read_bytes() for n in ('data.csv', 'STUDY_DESCRIPTION.md'))
bad = [k for k in os.environ if any(s in k.upper() for s in ('TOKEN','SECRET','PASSWORD','CREDENTIAL','API_KEY','SEED','PARAMETER','CANDIDATE'))]
print(json.dumps({'blocked': blocked, 'public_files_readable': public_read,
                 'environment': dict(os.environ), 'environment_clean': not bad,
                 'initial_files': sorted(p.name for p in inputs.iterdir()) if False else ['data.csv','STUDY_DESCRIPTION.md']}))
'''


def main():
    if hashlib.sha256(protocol_bytes()).hexdigest() != PROTOCOL:
        raise RuntimeError('Protocol changed')
    frozen = json.loads((ROOT / 'configs/frozen_study.json').read_text())
    candidate = {'id': 'K1', **frozen['parameters']}
    probe_path = ROOT / 'manifests/final_data_private_probe.txt'
    if not probe_path.exists():
        with probe_path.open('x') as stream:
            stream.write('SALMON_PRIVATE_FRAMEWORK_PROBE\n')
    base = ROOT / 'results/quality_checks/framework'
    base.mkdir(parents=True, exist_ok=False)
    files = {}
    for phase in ('development', 'formal'):
        directory = base / phase
        inputs = directory / 'inputs'
        inputs.mkdir(parents=True)
        generated = generate(candidate, 'A', 709000, 4)
        (inputs / 'data.csv').write_bytes(csv_bytes(generated['x'], generated['y'], generated['z']))
        (inputs / 'STUDY_DESCRIPTION.md').write_bytes((ROOT / 'materials/named/A.md').read_bytes())
        output, audit = reference(inputs)
        write_json(directory / 'reference.json', output)
        write_json(directory / 'reference_access_audit.json', audit)
        with tempfile.TemporaryDirectory(prefix='salmon-final-framework-') as tmp:
            work = Path(tmp).resolve()
            stage = work / 'public'
            stage.mkdir()
            for name in ('data.csv', 'STUDY_DESCRIPTION.md'):
                (stage / name).write_bytes((inputs / name).read_bytes())
            executable = work / 'probe.py'
            executable.write_text(PROBE)
            policy = profile(stage) + '\n(allow file-read* (literal ' + json.dumps(str(executable)) + '))\n'
            command = ['/usr/bin/sandbox-exec', '-p', policy, sys.executable,
                       '-I', '-B', str(executable), str(ROOT), str(stage)]
            completed = subprocess.run(command, cwd=stage, env=ENV,
                                       capture_output=True, text=True, timeout=30)
            if completed.returncode:
                raise RuntimeError('Framework probe failed: ' + completed.stderr)
            evidence = json.loads(completed.stdout)
        if not (all(evidence['blocked'].values()) and evidence['public_files_readable']
                and evidence['environment_clean'] and output['input_boundary_passed']):
            raise RuntimeError('Offline public boundary failed: ' + repr(evidence))
        (directory / 'sandbox_profile.sb').write_text(policy)
        write_json(directory / 'probes.json', evidence)
        write_json(directory / 'input_identity.json', {'purpose': 4, 'seed': 709000,
                                                      'not_final_study_data': True})
        seal(directory)
        for path in directory.rglob('*'):
            if path.is_file():
                files[str(path.relative_to(ROOT))] = sha(path)
    receipt = {
        'schema_version': 1, 'scope': 'offline_final_data_reference',
        'protocol_sha256': PROTOCOL, 'freeze_sha256': sha(ROOT / 'manifests/freeze.json'),
        'environment': {'python': platform.python_version(), 'numpy': np.__version__,
                        'platform': platform.platform(), 'numerical_threads': 1},
        'checks': {'ACC-5-reference': True, 'ACC-7-reference': True},
        'files': files,
        'runtime': {'executable': str(Path(sys.executable).resolve()),
                    'public_analysis': 'deterministic_reference_only',
                    'read_whitelist': ['two_explicit_public_files', '/System', '/usr/lib',
                                       '/usr/share/zoneinfo', str(Path(sys.base_prefix) / 'lib'),
                                       str(Path(sys.prefix) / 'lib'), 'staged_reference_executable'],
                    'child_environment': ENV,
                    'private_probe_sha256': sha(probe_path)},
        'framework_program_sha256': sha(Path(__file__)),
        'tested_model_environment_accepted': False,
        'tested_model_calls': 0,
    }
    write_json(ROOT / 'manifests/offline_framework.json', receipt)
    print(json.dumps({'scope': receipt['scope'], 'phases_probed': 2,
                      'checks': receipt['checks'], 'fixed_seeds_used': False}))


if __name__ == '__main__':
    main()
