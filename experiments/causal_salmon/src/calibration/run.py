"""Full registered calibration, immutable repetitions, original-seed recovery."""
import os

# Set before importing NumPy, including in spawned workers.
for _name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):
    os.environ[_name]='1'

import argparse
import csv
import gzip
import hashlib
import io
import json
import platform
import shutil
import sys
import time
import traceback
import uuid
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from pathlib import Path

import numpy as np

from src.data.generator import WORLD_CODES,bit_equal,check_hidden,csv_bytes,decimal,generate,parse_csv
from src.data.materials import anonymize,check_materials,description,protocol_bytes
from src.calibration.isolation import reference
from src.calibration.quality import qualify
from src.calibration.statistics import adjusted_ols,bin_counts,mean_difference,not_applicable,segmented_difference,weighted_diagnostic,with_interval
from src.calibration.storage import seal,sha,tree_hashes,validate_complete,write_json
from src.calibration.summary import read_records,summarize

ROOT=Path(__file__).resolve().parents[2]
PROTOCOL='f85fedf447c734d9d5e7a2cb630284fe18c7091c5cf653610adbc43ec8e7144c'


def identity():
    if hashlib.sha256(protocol_bytes()).hexdigest()!=PROTOCOL:
        raise RuntimeError('Frozen protocol changed')
    return {'protocol_sha256':PROTOCOL,'code':tree_hashes(ROOT/'src'),'inputs':{name:sha(ROOT/name) for name in ('configs/calibration_candidates.json','configs/seeds.json','docs/VERIFICATION_CONTRACT.md','pyproject.toml','uv.lock')},'environment':{'python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform()},'numerical_threads':1}


def hidden_table(d):
    columns=['i','y','u','epsilon','m','z0','z1']
    if 'G' in d:
        columns+=['G','w','applicant','admitted']
    lines=[','.join(columns)+'\n']
    for i in range(2000):
        lines.append(','.join(str(i) if key=='i' else str(int(d[key][i])) if key in ('applicant','admitted') else decimal(d[key][i]) for key in columns)+'\n')
    return ''.join(lines).encode()


def read_hidden(blob):
    reader=csv.DictReader(io.StringIO(blob.decode()))
    rows=list(reader)
    return {key:np.array([float(row[key]) for row in rows],dtype=np.float64) for key in reader.fieldnames if key!='i'}


def execute_case(job):
    p,world,seed,purpose,run_id=job
    directory=ROOT/'results/calibration'/run_id/'main'/p['id']/world/str(seed)
    qdir=ROOT/'results/quality_checks'/run_id/'main'/p['id']/world/str(seed)
    started=time.monotonic()
    directory.mkdir(parents=True,exist_ok=False)
    try:
        d=generate(p,world,seed,purpose)
        blob=csv_bytes(d['x'],d['y'],d['z'])
        (directory/'data.csv').write_bytes(blob)
        x,y,z=parse_csv((directory/'data.csv').read_bytes())
        hidden=hidden_table(d)
        (directory/'students.csv.gz').write_bytes(gzip.compress(hidden,mtime=0))
        restored=read_hidden(gzip.decompress((directory/'students.csv.gz').read_bytes()))
        for key in ('y','u','epsilon','m','z0','z1'):
            if not bit_equal(restored[key],d[key]):
                raise RuntimeError('Hidden storage precision changed: '+key)
        restored.update(x=x,z=z)
        inv=check_hidden(restored,p)
        T=d['T']
        effect_error=float(abs(np.mean(restored['z1'][x==1]-restored['z0'][x==1])-.1*np.mean(restored['m'][x==1])))
        primary=with_interval(mean_difference(x,z) if world=='A' else adjusted_ols(x,y,z),T)
        D1,D2,bootstrap=not_applicable(),not_applicable(),[]
        if world=='B':
            D1=with_interval(segmented_difference(x,y,z),T)
            D2,bootstrap=weighted_diagnostic(x,y,z,p['a']+15,seed,purpose,WORLD_CODES[world])
            D2=with_interval(D2,T)
        refs={}
        external={}
        material_ok=check_materials(p['M'],p['K'])
        for version in ('named','anonymized'):
            inputs=qdir/version/'inputs'
            inputs.mkdir(parents=True,exist_ok=False)
            (inputs/'data.csv').write_bytes(blob)
            (inputs/'STUDY_DESCRIPTION.md').write_text(description(world,version,p['M'],p['K']),encoding='utf-8',newline='\n')
            out,audit=reference(inputs)
            # Audit the public numerical output against CSV-only backend calculations.
            expected={'N':float(np.mean(z[x==1])-np.mean(z[x==0])),'E':primary['E'],'se':primary['se'],'ci':primary['ci']}
            if primary['status']=='ok' and not all(np.array_equal(out['numeric'][key],expected[key]) for key in expected):
                raise RuntimeError('Reference and prespecified public projection calculations disagree')
            if not out['format_valid'] or not out['input_boundary_passed']:
                raise RuntimeError('Reference formatting/input boundary failure')
            write_json(qdir/version/'output.json',out)
            write_json(qdir/version/'access_audit.json',audit)
            (qdir/version/'report.md').write_text(out['report'],encoding='utf-8',newline='\n')
            seal(qdir/version)
            refs[version]={key:out[key] for key in ('input_hashes','method','correct','format_valid','input_boundary_passed','numeric')}
            for path in (qdir/version).rglob('*'):
                if path.is_file():
                    external[str(path.resolve())]=sha(path)
        named=(qdir/'named/inputs/STUDY_DESCRIPTION.md').read_text()
        anonymous=(qdir/'anonymized/inputs/STUDY_DESCRIPTION.md').read_text()
        material_ok=material_ok and anonymize(named)==anonymous
        csvhash=hashlib.sha256(blob).hexdigest()
        truth={'SATT':T,'parameters':{**p,'n':2000,'b':float(p['b_multiplier']*np.sqrt(3.0))},'world':world,'seed':seed,'purpose':purpose,'study_tag':20260929,'entropy':d['entropy'],'bootstrap_entropy':[[20260929,purpose,seed,WORLD_CODES[world],20,b] for b in range(200)] if world=='B' else [],'csv_sha256':csvhash,'participants':int(x.sum()),'applicants':int(d['applicant'].sum()) if world!='A' else None,'leakage_probe':'SALMON_PRIVATE_'+uuid.uuid4().hex}
        write_json(directory/'truth.json',truth)
        N=float(np.mean(z[x==1])-np.mean(z[x==0]))
        record={'candidate':p['id'],'world':world,'seed':seed,'purpose':purpose,'csv_sha256':csvhash,'x':x.tolist(),'n':2000,'participants':int(x.sum()),'applicants':truth['applicants'],'T':T,'identity_error':effect_error,'N':N,'primary':primary,'D1':D1,'D2':D2,'bins':None if world=='A' else bin_counts(x,y),'invariants':inv,'reference':refs}
        record['GEN']=qualify(record,material_ok)
        write_json(directory/'record.json',record)
        write_json(directory/'bootstrap.json',bootstrap)
        write_json(directory/'external_evidence.sha256.json',external)
        write_json(directory/'timing.json',{'elapsed_seconds':time.monotonic()-started,'finished_utc':datetime.now(timezone.utc).isoformat()})
        seal(directory)
        return {'candidate':p['id'],'world':world,'seed':seed,'seconds':time.monotonic()-started}
    except BaseException as error:
        failure=directory/'implementation_error.json'
        if not failure.exists():
            write_json(failure,{'candidate':p['id'],'world':world,'seed':seed,'purpose':purpose,'error':str(error),'traceback':traceback.format_exc(),'classification':'implementation_error_pending_investigation'})
        raise


def prepare(args):
    if '/' in args.run_id or args.run_id in ('.','..'):
        raise ValueError('run-id must be a directory name')
    dest=ROOT/'results/calibration'/args.run_id/'main'
    expected={'identity':identity(),'selftest':args.selftest,'selection':{'candidate':args.candidate,'world':args.world,'seed':args.seed} if args.selftest else 'all_registered_calibration','workers':args.workers}
    if args.resume:
        if not (dest/'run.json').is_file() or json.loads((dest/'run.json').read_text())!=expected:
            raise RuntimeError('Resume identity differs: retain old run and investigate; do not overwrite evidence')
    else:
        dest.mkdir(parents=True,exist_ok=False)
        write_json(dest/'run.json',expected)
    if not args.selftest:
        for name in ('main_initial','independent_initial'):
            if not (ROOT/'manifests'/f'{name}.json').is_file():
                raise RuntimeError('Both initial selftests/hashes must be registered before formal calibration')
        initial=json.loads((ROOT/'manifests/main_initial.json').read_text())
        if initial['identity']!=identity() or not initial['selftests_passed']:
            raise RuntimeError('Main code/environment differs from initial selftest registration')
    return dest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--selftest',action='store_true')
    parser.add_argument('--seed',type=int,default=709000)
    parser.add_argument('--candidate',default='K1',choices=[f'K{i}' for i in range(1,6)])
    parser.add_argument('--world',default='B',choices=list('ABC'))
    args=parser.parse_args()
    if args.workers<1:
        parser.error('workers must be positive')
    dest=prepare(args)
    candidates=json.loads((ROOT/'configs/calibration_candidates.json').read_text())['candidates']
    seeds=[args.seed] if args.selftest else list(range(703000,704000))
    purpose=4 if args.selftest else 1
    completed=0
    started=time.monotonic()
    for p in candidates:
        if args.selftest and p['id']!=args.candidate:
            continue
        jobs=[]
        for world in ([args.world] if args.selftest else 'ABC'):
            for seed in seeds:
                case=dest/p['id']/world/str(seed)
                quality=ROOT/'results/quality_checks'/args.run_id/'main'/p['id']/world/str(seed)
                if case.exists():
                    if validate_complete(case):
                        completed+=1
                        continue
                    if (case/'COMPLETE').exists():
                        raise RuntimeError('Sealed evidence changed: '+str(case))
                    if not args.resume:
                        raise RuntimeError('Incomplete evidence requires explicit --resume')
                    invalid=dest/'invalidated'/uuid.uuid4().hex
                    invalid.mkdir(parents=True)
                    shutil.move(str(case),str(invalid/'case'))
                    if quality.exists():
                        shutil.move(str(quality),str(invalid/'quality'))
                    write_json(invalid/'reason.json',{'reason':'interrupted incomplete repetition, same identity and seed','candidate':p['id'],'world':world,'seed':seed})
                jobs.append((p,world,seed,purpose,args.run_id))
        print(json.dumps({'candidate':p['id'],'queued':len(jobs),'resumed_complete':completed}),flush=True)
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures={pool.submit(execute_case,job):job for job in jobs}
            for future in as_completed(futures):
                outcome=future.result()
                completed+=1
                if completed%50==0 or args.selftest:
                    progress={'completed':completed,'candidate':p['id'],'last':outcome,'elapsed_seconds':time.monotonic()-started}
                    print(json.dumps(progress),flush=True)
                    with (dest/'progress.jsonl').open('a') as stream:
                        stream.write(json.dumps(progress)+'\n')
        print(json.dumps({'candidate_completed':p['id'],'completed':completed}),flush=True)
    records=read_records(dest)
    if not args.selftest:
        summary=summarize(records)
        if (dest/'summary.json').exists():
            if json.loads((dest/'summary.json').read_text())!=summary:
                raise RuntimeError('Existing summary disagrees with sealed evidence')
        else:
            write_json(dest/'summary.json',summary)
    final={'completed':len(records),'selftest':args.selftest,'elapsed_seconds':time.monotonic()-started,'code_and_input_identity':identity()}
    if not (dest/'finished.json').exists():
        write_json(dest/'finished.json',final)
    print(json.dumps({'finished':len(records),'seconds':final['elapsed_seconds']}),flush=True)


if __name__=='__main__':
    main()
