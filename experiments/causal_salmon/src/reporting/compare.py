"""Full independent evidence comparison, without importing independent code."""
import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from src.calibration.storage import sha,write_json

ROOT=Path(__file__).resolve().parents[2]


def compare_values(main,other,path,issues):
    if isinstance(main,bool) or isinstance(other,bool) or main is None or other is None or isinstance(main,str) or isinstance(other,str):
        if type(main)!=type(other) or main!=other:
            issues.append({'path':path,'main':main,'independent':other,'kind':'status_discrete_or_null'})
    elif isinstance(main,dict) and isinstance(other,dict):
        if set(main)!=set(other):
            issues.append({'path':path,'main_keys':sorted(main),'independent_keys':sorted(other),'kind':'keys'})
        for key in main.keys() & other.keys():
            compare_values(main[key],other[key],path+'.'+key,issues)
    elif isinstance(main,list) and isinstance(other,list):
        if len(main)!=len(other):
            issues.append({'path':path,'main_length':len(main),'independent_length':len(other),'kind':'length'})
        for i,(a,b) in enumerate(zip(main,other)):
            compare_values(a,b,path+f'[{i}]',issues)
    elif isinstance(main,(int,float)) and isinstance(other,(int,float)):
        delta=abs(main-other)
        tolerance=0 if isinstance(main,int) and isinstance(other,int) else 1e-8*max(1,abs(main))
        if not math.isfinite(main) or not math.isfinite(other) or delta>tolerance:
            issues.append({'path':path,'main':main,'independent':other,'delta':delta,'tolerance':tolerance,'kind':'numeric'})
    else:
        issues.append({'path':path,'kind':'type_mismatch'})


def projection(record):
    keys=('candidate','world','seed','purpose','csv_sha256','x','n','participants','applicants','T','identity_error','N','bins','invariants')
    output={key:record[key] for key in keys}
    for key in ('primary','D1','D2'):
        output[key]={name:record[key][name] for name in ('status','E','se','ci','covered')}
        if key=='D2' and record['world']=='B':
            output[key].update({name:record[key][name] for name in ('max_weight','ess','bootstrap_successes','bootstrap_failures')})
    output['GEN']={key:{name:value[name] for name in ('applicable','passed')} for key,value in record['GEN'].items()}
    output['reference']=record['reference']
    return output


def summary_projection(summary):
    output={}
    for candidate,value in summary['candidates'].items():
        output[candidate]={key:value[key] for key in ('worlds','CAL','CAL9_status','diagnostic_conflicts','state')}
        output[candidate]['GEN']={world:{gen:{key:v[key] for key in ('applicable_count','passed_count','failed_count')} for gen,v in checks.items()} for world,checks in value['GEN'].items()}
    return output


def verified_manifest(case):
    case=Path(case)
    expected=(case/'COMPLETE').read_text().strip()
    manifest_path=case/'evidence.sha256.json'
    if sha(manifest_path)!=expected:
        return False
    manifest=json.loads(manifest_path.read_text())
    files=manifest.get('files',manifest)
    if not all((case/name).is_file() and sha(case/name)==digest for name,digest in files.items()):
        return False
    if (case/'external_evidence.sha256.json').exists():
        if not all(Path(name).is_file() and sha(name)==digest for name,digest in json.loads((case/'external_evidence.sha256.json').read_text()).items()):
            return False
    return True


def hidden_projection(path):
    with gzip.open(path,'rt',encoding='utf-8',newline='') as stream:
        reader=csv.DictReader(stream)
        rows=list(reader)
        aliases={'eps':'epsilon','epsilon':'epsilon','row_id':'i','row':'i','index':'i','applicants':'applicant','admission':'admitted'}
        return {aliases.get(key,key):np.array([float(row[key]) for row in rows]) for key in reader.fieldnames}


def compare_run(run_id,output_name='comparison.json'):
    root=ROOT/'results/calibration'/run_id
    for name in ('main_initial','independent_initial'):
        if not (ROOT/'manifests'/f'{name}.json').is_file():
            raise RuntimeError('Comparison is prohibited before both initial freezes')
    issues=[]
    checked=0
    bootstrap_checked=0
    failure_reproductions=[]
    for k in range(1,6):
        for world in 'ABC':
            for seed in range(703000,704000):
                relative=Path(f'K{k}')/world/str(seed)
                a,b=root/'main'/relative,root/'independent'/relative
                if not (a/'COMPLETE').exists() or not (b/'COMPLETE').exists():
                    issues.append({'path':str(relative),'kind':'missing_complete_evidence'})
                    continue
                if not verified_manifest(a) or not verified_manifest(b):
                    issues.append({'path':str(relative),'kind':'sealed_evidence_changed'})
                    continue
                ra,rb=[json.loads((p/'record.json').read_text()) for p in (a,b)]
                compare_values(projection(ra),projection(rb),str(relative),issues)
                if sha(a/'data.csv')!=ra['csv_sha256'] or sha(b/'data.csv')!=rb['csv_sha256']:
                    issues.append({'path':str(relative),'kind':'public_csv_hash_registration'})
                ha,hb=[hidden_projection(p/'students.csv.gz') for p in (a,b)]
                hidden_keys=['y','u','epsilon','m','z0','z1']+(['G','w','applicant','admitted'] if world!='A' else [])
                for key in hidden_keys:
                    if key not in ha or key not in hb:
                        issues.append({'path':str(relative)+'.hidden.'+key,'kind':'missing_hidden_field'})
                        continue
                    left,right=ha[key],hb[key]
                    tolerance=1e-8*np.maximum(1,np.abs(left))
                    if left.shape!=right.shape or not np.all(np.abs(left-right)<=tolerance):
                        issues.append({'path':str(relative)+'.hidden.'+key,'kind':'hidden_numeric_difference'})
                if world=='B':
                    ba,bb=[json.loads((p/'bootstrap.json').read_text()) for p in (a,b)]
                    select=lambda rows:[{key:r[key] for key in ('index','status','E')} for r in rows]
                    compare_values(select(ba),select(bb),str(relative)+'.bootstrap',issues)
                    bootstrap_checked+=len(ba)
                    for index,(va,vb) in enumerate(zip(ba,bb)):
                        if va['status']!='ok' or vb['status']!='ok':
                            failure_reproductions.append({'case':str(relative),'bootstrap_index':index,'main':va,'independent':vb,'same_failure_status':va['status']==vb['status'],'data_level_evidence_present':bool(va.get('details')) and bool(vb.get('details'))})
                for name in ('primary','D1','D2'):
                    if ra[name]['status']=='unavailable' or rb[name]['status']=='unavailable':
                        failure_reproductions.append({'case':str(relative),'method':name,'main':ra[name],'independent':rb[name],'same_failure_status':ra[name]['status']==rb[name]['status'],'data_level_evidence_present':bool(ra[name].get('details')) and bool(rb[name].get('details'))})
                checked+=1
    sa,sb=[json.loads((root/impl/'summary.json').read_text()) for impl in ('main','independent')]
    compare_values(summary_projection(sa),summary_projection(sb),'summary',issues)
    output={'run_id':run_id,'repetitions_checked':checked,'expected_repetitions':15000,'bootstrap_estimates_checked':bootstrap_checked,'expected_bootstrap_estimates':1000000,'numeric_tolerance':'abs(delta)<=1e-8*max(1,abs(main))','mismatches':issues,'failure_reproductions':failure_reproductions,'passed':checked==15000 and bootstrap_checked==1000000 and not issues,'input_hashes':{'main_summary':sha(root/'main/summary.json'),'independent_summary':sha(root/'independent/summary.json'),'main_initial':sha(ROOT/'manifests/main_initial.json'),'independent_initial':sha(ROOT/'manifests/independent_initial.json')}}
    write_json(root/output_name,output)
    return output


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--output-name',default='comparison.json')
    args=parser.parse_args()
    value=compare_run(args.run_id,args.output_name)
    print(json.dumps({'passed':value['passed'],'checked':value['repetitions_checked'],'mismatches':len(value['mismatches'])}))
    raise SystemExit(0 if value['passed'] else 1)
