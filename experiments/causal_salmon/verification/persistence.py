"""Write-once evidence and immutable run identity, independent implementation."""
import gzip
import io
import traceback
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import uuid
import numpy as np
from .generator import hidden_csv
from .materials import protocol_bytes

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_HASH = 'f85fedf447c734d9d5e7a2cb630284fe18c7091c5cf653610adbc43ec8e7144c'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value,ensure_ascii=False,allow_nan=False,sort_keys=True,indent=2)+'\n').encode()


def write_once(path,data):
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def hash_tree():
    files = {str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in sorted((ROOT/'verification').glob('*.py'))}
    return dict(files=files,aggregate_sha256=digest(json_bytes(files)))


def environment():
    return dict(python=sys.version,numpy=np.__version__,platform=platform.platform(),machine=platform.machine(),executable=str(Path(sys.executable).resolve()))


def identity(run_id,selftest=False,selection=None):
    inputs={p:digest((ROOT/p).read_bytes()) for p in ['planning.md','configs/calibration_candidates.json','configs/seeds.json','docs/VERIFICATION_CONTRACT.md','pyproject.toml','uv.lock']}
    canonical_hash = digest(protocol_bytes(ROOT))
    if canonical_hash!=PROTOCOL_HASH:
        raise ValueError('Protocol fingerprint changed')
    return dict(source_protocol_sha256=canonical_hash,run_id=run_id,implementation='independent',selftest=selftest,selection=selection,inputs=inputs,code=hash_tree(),environment=environment(),thread_limits={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS')})


def verify_complete(path):
    path=Path(path)
    if not (path/'COMPLETE').exists():
        return False
    evidence_data=(path/'evidence.sha256.json').read_bytes()
    if (path/'COMPLETE').read_text().strip()!=digest(evidence_data):
        raise ValueError(f'Completion hash mismatch: {path}')
    manifest=json.loads(evidence_data)
    for base,entries in ((path,manifest['case_files']), (ROOT,manifest['quality_files'])):
        for name,expected in entries.items():
            if digest((base/name).read_bytes())!=expected:
                raise ValueError(f'Immutable evidence changed: {base/name}')
    return True


def preserve_incomplete(path):
    path=Path(path)
    if path.exists():
        failed=path.parent/('.retained-incomplete-'+path.name+'-'+uuid.uuid4().hex)
        path.rename(failed)
        write_once(failed/'RETAINED_REASON.json',json_bytes(dict(reason='Interrupted incomplete attempt retained; same registered input will be recomputed',time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))))


def save_case(base,quality_base,computed):
    record,public,hidden,truth,bootstrap,descriptions,refs=computed
    suffix=Path(record['candidate'])/record['world']/str(record['seed'])
    final,quality_final=base/suffix,quality_base/suffix
    if verify_complete(final):
        return final
    preserve_incomplete(final)
    preserve_incomplete(quality_final)
    temp=final.parent/('.partial-'+final.name+'-'+uuid.uuid4().hex)
    temp.mkdir(parents=True)
    quality_final.mkdir(parents=True)
    truth={**truth,'leakage_probe':'SALMON_PRIVATE_'+uuid.uuid4().hex}
    write_once(temp/'data.csv',public)
    write_once(temp/'students.csv.gz',gzip.compress(hidden_csv(hidden),mtime=0))
    write_once(temp/'truth.json',json_bytes(truth))
    recovered = gzip.decompress((temp/'students.csv.gz').read_bytes())
    saved = np.genfromtxt(io.BytesIO(recovered),delimiter=',',names=True,dtype=np.float64)
    params=truth['parameters']
    recomputed_m=10+params['gamma']*(saved['y']-(params['a']+15))+2*saved['u']
    recomputed_z0=recomputed_m+saved['epsilon']
    recomputed_z1=recomputed_z0+.1*recomputed_m
    for actual,expected in ((saved['m'],recomputed_m),(saved['z0'],recomputed_z0),(saved['z1'],recomputed_z1)):
        if not np.array_equal(actual.view(np.uint64),expected.view(np.uint64)):
            raise ValueError('Saved hidden-table CAL-8 bitwise recomputation failed')
    if any(truth['leakage_probe'] in str(ref) for ref in refs.values()):
        raise ValueError('Unique hidden leakage probe in reference output')
    write_once(temp/'record.json',json_bytes(record))
    write_once(temp/'bootstrap.json',json_bytes(bootstrap))
    for version in ('named','anonymized'):
        folder=quality_final/version
        folder.mkdir()
        ref=refs[version]
        write_once(folder/'data.csv',public)
        write_once(folder/'STUDY_DESCRIPTION.md',descriptions[version])
        write_once(folder/'reference.json',json_bytes(ref))
        write_once(folder/'report.md',ref['report'].encode())
        write_once(folder/'access_audit.json',json_bytes(dict(access_log=ref['access_log'],probes=ref['probes'],sandbox_profile=ref['sandbox_profile'])))
        write_once(folder/'input_manifest.json',json_bytes(ref['input_hashes']))
    evidence=dict(case_files={p.name:digest(p.read_bytes()) for p in sorted(temp.iterdir())},quality_files={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in sorted(quality_final.rglob('*')) if p.is_file()})
    manifest=json_bytes(evidence)
    write_once(temp/'evidence.sha256.json',manifest)
    write_once(temp/'COMPLETE',(digest(manifest)+'\n').encode())
    temp.rename(final)
    for folder in (final,quality_final):
        for p in folder.rglob('*'):
            if p.is_file():
                p.chmod(0o444)
    return final


def retain_failure(base,candidate,world,seed,purpose,exception):
    from .generator import generate
    folder=Path(base)/'.failed_attempts'/(candidate['id']+'-'+world+'-'+str(seed)+'-'+uuid.uuid4().hex)
    folder.mkdir(parents=True)
    write_once(folder/'failure.json',json_bytes(dict(candidate=candidate,world=world,seed=seed,purpose=purpose,exception=repr(exception),traceback=traceback.format_exc(),code=hash_tree(),environment=environment(),classification='implementation_error_pending_review')))
    try:
        public,projection,hidden,truth,invariants=generate(candidate,world,seed,purpose)
        write_once(folder/'data.csv',public)
        write_once(folder/'students.csv.gz',gzip.compress(hidden_csv(hidden),mtime=0))
        write_once(folder/'truth.json',json_bytes(truth))
    except Exception as regeneration_error:
        write_once(folder/'regeneration_failure.json',json_bytes(dict(exception=repr(regeneration_error))))
    return folder
