"""Independent full-calibration CLI. No exam seeds or tested model calls."""
import os
for _key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[_key]='1'
import argparse
from concurrent.futures import ProcessPoolExecutor
import fcntl
import json
from pathlib import Path
import re
import time
from .evaluate import compute
from .materials import verify_structure
from .persistence import ROOT, identity, write_once, json_bytes, verify_complete, save_case, digest, hash_tree, retain_failure
from .summary import make_summary


def one_task(payload):
    candidate,world,seed,purpose,protocol,base,quality=payload
    final=Path(base)/candidate['id']/world/str(seed)
    if verify_complete(final):
        return str(final)
    try:
        computed=compute(candidate,world,seed,purpose,protocol)
        return str(save_case(Path(base),Path(quality),computed))
    except Exception as error:
        retain_failure(base,candidate,world,seed,purpose,error)
        raise


def load_records(base):
    records=[]
    for path in sorted(Path(base).glob('K*/[ABC]/*/record.json')):
        if verify_complete(path.parent):
            records.append(json.loads(path.read_text()))
    return records


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-id',default='calibration')
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--selftest',action='store_true')
    parser.add_argument('--seed',type=int,default=709000)
    parser.add_argument('--candidate',choices=['K1','K2','K3','K4','K5'],default='K1')
    parser.add_argument('--world',choices=list('ABC'),default='B')
    parser.add_argument('--rebuild-summary',action='store_true')
    args=parser.parse_args(argv)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',args.run_id) or args.workers<1:
        parser.error('Safe run id and positive worker count required')
    if args.selftest:
        base=ROOT/'verification/selftest_runs'/args.run_id
        quality=ROOT/'verification/selftest_quality'/args.run_id
        selection=dict(candidate=args.candidate,world=args.world,seed=args.seed,purpose=4)
        if not 709000<=args.seed<=709999:
            parser.error('Only registered purpose4 selftest seeds allowed')
    else:
        base=ROOT/'results/calibration'/args.run_id/'independent'
        quality=ROOT/'results/quality_checks'/args.run_id/'independent'
        selection=None
        for name in ('main_initial.json','independent_initial.json'):
            if not (ROOT/'manifests'/name).exists():
                raise RuntimeError('Both initial selftest/code registrations required before formal execution')
        independent=json.loads((ROOT/'manifests/independent_initial.json').read_text())
        if independent['code']['aggregate_sha256']!=hash_tree()['aggregate_sha256']:
            raise RuntimeError('Independent code changed after initial registration; a new truthful registration required')
    run_identity=identity(args.run_id,args.selftest,selection)
    base.mkdir(parents=True,exist_ok=True)
    with (base/'.run.lock').open('a+b') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another process owns this immutable run')
        identity_path=base/'run_identity.json'
        if identity_path.exists():
            if not args.resume and not args.rebuild_summary:
                raise RuntimeError('Existing run retained; use --resume')
            if json.loads(identity_path.read_text())!=run_identity:
                raise RuntimeError('Immutable run identity mismatch; preserve old evidence and use new run id')
        else:
            if args.rebuild_summary:
                raise RuntimeError('No registered run to summarize')
            write_once(identity_path,json_bytes(run_identity))
            identity_path.chmod(0o444)
        protocol=(ROOT/'planning.md').read_text()
        if not args.rebuild_summary:
            candidates=json.loads((ROOT/'configs/calibration_candidates.json').read_text())['candidates']
            started=time.monotonic()
            completed_count=0
            with ProcessPoolExecutor(max_workers=args.workers) as executor:
                for candidate in candidates:
                    if args.selftest and candidate['id']!=args.candidate:
                        continue
                    worlds=[args.world] if args.selftest else list('ABC')
                    seeds=[args.seed] if args.selftest else range(703000,704000)
                    payloads=[(candidate,world,seed,4 if args.selftest else 1,protocol,str(base),str(quality)) for world in worlds for seed in seeds]
                    for path in executor.map(one_task,payloads,chunksize=1):
                        completed_count+=1
                        if completed_count%100==0 or args.selftest:
                            print(json.dumps(dict(completed=completed_count,last_case=path,elapsed_seconds=time.monotonic()-started)),flush=True)
        records=load_records(base)
        if args.selftest:
            print(json.dumps(dict(selftest=True,records=len(records),base=str(base))),flush=True)
            return
        if len(records)!=15000:
            raise RuntimeError(f'Incomplete full calibration: {len(records)}/15000')
        summary=make_summary(records,material_structure=verify_structure(protocol))
        blob=json_bytes(summary)
        summary_path=base/'summary.json'
        if summary_path.exists():
            if summary_path.read_bytes()!=blob:
                raise RuntimeError('Rebuilt summary differs from immutable saved summary')
        else:
            write_once(summary_path,blob); summary_path.chmod(0o444)
        print(json.dumps(dict(records=len(records),summary_sha256=digest(blob),candidate_states={k:v['state'] for k,v in summary['candidates'].items()})),flush=True)

if __name__=='__main__':
    main()
