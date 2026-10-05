"""Audit every frozen candidate and disclose deterministic GEN-based selection."""
import argparse
import csv
import io
import json
from pathlib import Path
from scripts import pairwise_audit as paired
from scripts import generate_data as main_program

ROOT = paired.ROOT
BASE = ROOT / 'results/quality_checks/data'
DEST = ROOT / 'datasets'


def immutable_text(path, text, verify=False):
    if path.exists():
        assert path.read_text() == text, 'Immutable output differs: ' + str(path)
    else:
        assert not verify, 'Missing output: ' + str(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x') as stream: stream.write(text)
        path.chmod(0o444)


def immutable_json(path, value, verify=False):
    immutable_text(path, json.dumps(value, indent=2, allow_nan=False)+'\n', verify)


def copy_exact(source, destination, verify=False):
    if destination.exists():
        assert destination.read_bytes() == source.read_bytes(), str(destination)
    else:
        assert not verify, 'Missing selected file: ' + str(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream: stream.write(source.read_bytes())
        destination.chmod(0o444)


def csv_text(fields, rows):
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return stream.getvalue()




def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-only',action='store_true',help='Verify the Git submission package without private evidence')
    parser.add_argument('--selftest',action='store_true')
    parser.add_argument('--verify-only',action='store_true')
    args=parser.parse_args()
    if args.public_only:
        if (ROOT/'manifests/submission_manifest.json').exists():
            from scripts.validate_submission import main as validate_submission
            validate_submission()
            return
        manifest=paired.read(ROOT/'manifests/delivery.json')
        for name,expected in manifest['files'].items():
            assert paired.sha(ROOT/name)==expected, name
        rows=list(csv.DictReader((BASE/'DATASET_INDEX.csv').open()))
        assert len(rows)==12 and len(list((ROOT/'datasets/public').rglob('data.csv')))==12
        pool=list(csv.DictReader((BASE/'POOL_INDEX.csv').open()))
        assert len(pool)==60 and sum(r['qualified']=='True' for r in pool)==56
        for row in rows:
            assert paired.sha(ROOT/row['public_csv'])==row['csv_sha256']
            data=list(csv.DictReader((ROOT/row['public_csv']).open()))
            assert len(data)==2000 and sum(int(r['x']) for r in data)==600
        print(json.dumps({'public_package_verified':True,'selected_datasets':12,'student_records':24000,'candidate_records':60}))
        return
    main_program.check_gate()
    cfg=main_program.load(main_program.CONFIG)
    cases=([dict(phase='selftest',world=w,seed=s,purpose=4,case_id=f'selftest-{w}-{s}') for w in 'ABC' for s in range(709000,709010)] if args.selftest else main_program.case_matrix())
    compared=[];main_records=[]
    for case in cases:
        phase,world,seed,case_id=(case[k] for k in ('phase','world','seed','case_id'))
        md=BASE/'main'/phase/case_id
        ind=BASE/'independent'/phase/f'{world}-{seed}'
        storage=BASE/'main/selftest_storage' if args.selftest else BASE/'candidate_storage/main'
        public=storage/'public'/phase/case_id/'data.csv'
        hidden=storage/'ground_truth'/case_id
        row=paired.inspect_pair(phase,world,seed,md,ind,hidden,public)
        del row['private_probe']
        compared.append(row)
        main_records.append(paired.read(md/'record.json'))
    assert len({r['csv_sha256'] for r in compared})==len(cases)
    summary={'scope':'selftest_only' if args.selftest else 'complete_screened_candidate_pool','case_pairs_checked':len(cases),'reference_pairs_checked':2*len(cases),'bootstrap_pairs_checked':200*sum(r['world']=='B' for r in compared),'independent_comparison_passed':True,'records':compared,'config_sha256':paired.sha(ROOT/main_program.CONFIG),'audit_program_sha256':paired.sha(Path(__file__)),'tested_model_calls':0}
    immutable_json(BASE/('SELFTEST_COMPARISON.json' if args.selftest else 'POOL_COMPARISON.json'),summary,args.verify_only)
    if args.selftest:
        print(json.dumps({k:v for k,v in summary.items() if k!='records'}));return
    selected,counts=main_program.select_cases(main_records)
    identities=[{k:r[k] for k in ('phase','world','seed')} for r in selected]
    independent=paired.read(BASE/'independent/summary.json')
    assert independent['selection_complete'] is True
    assert independent['qualifying_counts']==counts
    assert independent['selected_cases']==identities, 'Independent selection differs'
    selected_keys={(r['phase'],r['world'],r['seed']) for r in selected}
    selection={'scope':'GEN_screened_synthetic_benchmark','selection_rule':cfg['selection'],'pool_count':60,'selected_count':12,'qualifying_counts':counts,'selected_cases':identities,'independent_selection_agrees':True,'ACC-10':True,'qualification_population':'conditional on unchanged GEN qualification','parameters_changed':False,'pool_extended':False,'tested_model_calls':0}
    immutable_json(BASE/'SELECTION.json',selection,args.verify_only)
    ledger=[];gen_rows=[];index=[]
    for row,record in zip(compared,main_records):
        case_id=record['case_id'];phase,world,seed=(record[k] for k in ('phase','world','seed'))
        chosen=(phase,world,seed) in selected_keys
        storage=BASE/'candidate_storage/main'
        pool_public=storage/'public'/phase/case_id/'data.csv'
        pool_hidden=storage/'ground_truth'/case_id
        ledger.append({'phase':phase,'world':world,'seed':seed,'qualified':row['quality_passed'],'selected':chosen,'csv_sha256':row['csv_sha256'],'candidate_public_csv':str(pool_public.relative_to(ROOT)),'failure_reasons':json.dumps(row['failure_reasons'],sort_keys=True)})
        for check,g in record['GEN'].items():
            gen_rows.append({'phase':phase,'world':world,'seed':seed,'selected':chosen,'check':check,'applicable':g['applicable'],'passed':g['passed'],'reasons':json.dumps(g['reasons'])})
        if not chosen:continue
        public=DEST/'public'/phase/case_id/'data.csv'
        hidden=DEST/'ground_truth'/case_id
        copy_exact(pool_public,public,args.verify_only)
        for name in ('students.csv','truth.json'):copy_exact(pool_hidden/name,hidden/name,args.verify_only)
        index.append({'phase':phase,'world':world,'seed':seed,'rows':record['n'],'participants':record['participants'],'applicants':record['applicants'],'public_csv':str(public.relative_to(ROOT)),'hidden_students':str((hidden/'students.csv').relative_to(ROOT)),'hidden_truth':str((hidden/'truth.json').relative_to(ROOT)),'csv_sha256':row['csv_sha256'],'SATT':row['T'],'reference_estimate':row['E'],'standard_error':row['se'],'ci':json.dumps(row['ci']),'dataset_quality_passed':True,'batch_eligible':True,'screened':True})
    for name,rows in (('POOL_INDEX.csv',ledger),('GEN_TABLE.csv',gen_rows),('DATASET_INDEX.csv',index)):
        immutable_text(BASE/name,csv_text(list(rows[0]),rows),args.verify_only)
    failures=[r for r in compared if not r['quality_passed']]
    immutable_json(BASE/'FAILURES.json',{'classification':'retained_candidate_quality_failures','count':len(failures),'records':failures,'pool_extension_allowed':False},args.verify_only)
    report='# Screened Synthetic Data Batch Qualification\n\n'
    report+='**Status:** All 12 selected datasets qualify under the registered screening protocol. No tested models have run.\n\n'
    report+='The owner authorized a finite candidate pool and transparent GEN screening before candidate generation. Both programs generated all 60 registered candidates using unchanged K1 parameters, assignment, random streams, numerical algorithms and public materials. Selection takes the lowest-seed qualifying candidates within each phase/world. No candidate seeds were appended and no student values were manually edited.\n\n'
    report+='## Complete pool and selection\n\n| Phase/world | Generated | Qualified | Selected |\n|---|---:|---:|---:|\n'
    for phase in ('development','formal'):
        for world in 'ABC':
            key=phase+'/'+world;report+=f'| {key} | 10 | {counts[key]} | {cfg["phases"][phase]["quota_per_world"]} |\n'
    report+=f'\nAll {len(failures)} candidate quality failures are retained in FAILURES.json and POOL_INDEX.csv. GEN_TABLE.csv reports all 420 candidate checks, including unselected candidates. Both programs retained 120 public-only reference analyses and 4000 B bootstrap attempts each; every candidate and bootstrap pair agreed.\n\n'
    report+='## Selected datasets\n\n| Phase | World | Seed | SATT | Reference estimate | SE | 95% interval |\n|---|---|---:|---:|---:|---:|---|\n'
    for r in index:report+=f'| {r["phase"]} | {r["world"]} | {r["seed"]} | {r["SATT"]:.8g} | {r["reference_estimate"]:.8g} | {r["standard_error"]:.8g} | {r["ci"]} |\n'
    report+='\nAll 12 selected cases and named/anonymous pairs pass every applicable GEN check. Hidden truth is checked separately from public reference analyses. C estimates remain descriptive and its reports recognize insufficient information. ACC-10 is true for this screened batch.\n\n'
    report+='## Interpretation and execution boundary\n\nThis is an explicitly screened synthetic benchmark, conditional on GEN qualification. It is not an unscreened random sample. Its guaranteed acceptance coverage is a selection property, not a claim that nominal confidence intervals cover every future draw. The original calibration describes the unchanged unfiltered generator. All pool exclusions must accompany any publication, and model-performance conclusions apply to the selected benchmark.\n\n'
    report+='Model, budget and scoring-personnel registration and tested-model runtime isolation remain required before experiments. Offline reference sandbox checks do not certify the future model environment. No model calls or publication are authorized by data qualification.\n'
    immutable_text(BASE/'FINAL_DATA_QUALIFICATION_REPORT.md',report,args.verify_only)
    manifest=ROOT/'manifests/delivery.json'
    if manifest.exists():
        for name,expected in paired.read(manifest)['files'].items():assert paired.sha(ROOT/name)==expected,name
    evidence=BASE/'EVIDENCE_MANIFEST.json'
    if evidence.exists():
        for name,expected in paired.read(evidence)['files'].items(): assert paired.sha(ROOT/name)==expected,name
    print(json.dumps({'pool_pairs':60,'qualified_candidates':60-len(failures),'selected_cases':12,'bootstrap_pairs':4000,'independent_selection_agrees':True,'ACC-10':True,'tested_model_calls':0}))


if __name__=='__main__': main()
