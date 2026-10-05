"""Complete-vector CAL statistics; no omission of unavailable diagnostics."""
import json
from pathlib import Path

import numpy as np

FIELDS=('bias','MCSE','relative_bias','coverage','precision_ratio','distinction_ratio')


def metrics(estimates,T,N):
    ok=[r['status']=='ok' for r in estimates]
    count=sum(ok)
    state='not_applicable' if estimates and all(r['status']=='not_applicable' for r in estimates) else 'not_evaluable'
    out={'status':state,'count':count,**dict.fromkeys(FIELDS)}
    if count != len(estimates) or count < 2:
        return out
    E=np.array([r['E'] for r in estimates],dtype=np.float64)
    error=E-T
    sd=float(np.std(error,ddof=1))
    spread=float(np.std(E,ddof=1))
    out.update(status='ok',bias=float(np.mean(error)),MCSE=float(sd/np.sqrt(len(E))),relative_bias=float(abs(np.mean(error))/np.mean(T)),coverage=float(np.mean([r['covered'] for r in estimates])),precision_ratio=float(np.mean(T)/sd) if sd>0 else None,distinction_ratio=float(np.mean(N-E)/spread) if spread>0 else None)
    return out


def conflict(diag,primary,meanT):
    if diag['status']!='ok' or primary['status']!='ok':
        return {'status':'not_evaluable','conflict':None,'criteria':None}
    delta=abs(diag['bias']-primary['bias'])
    criteria=[diag['relative_bias']>.10,diag['coverage']<.90,delta/meanT>.05 and delta>3*np.sqrt(diag['MCSE']**2+primary['MCSE']**2)]
    return {'status':'ok','conflict':any(criteria),'criteria':[bool(v) for v in criteria]}


def summarize(records,expected_count=1000):
    output={'candidates':{}}
    for name in ('K1','K2','K3','K4','K5'):
        subset=[r for r in records if r['candidate']==name]
        if not subset:
            continue
        worlds={}
        GEN={}
        complete=len(subset)==3*expected_count
        for world in 'ABC':
            rows=sorted((r for r in subset if r['world']==world),key=lambda r:r['seed'])
            if not rows:
                continue
            T=np.array([r['T'] for r in rows])
            N=np.array([r['N'] for r in rows])
            worlds[world]={k:metrics([r[k] for r in rows],T,N) for k in ('primary','D1','D2')}
            worlds[world]['support_passes']=None if world=='A' else sum(min(r['bins']['control'])>=20 for r in rows)
            GEN[world]={}
            for key in (f'GEN-{i}' for i in range(1,8)):
                applicable=[r['GEN'][key] for r in rows if r['GEN'][key]['applicable']]
                reasons={}
                for r in applicable:
                    for reason in r['reasons']:
                        reasons[reason]=reasons.get(reason,0)+1
                GEN[world][key]={'applicable_count':len(applicable),'passed_count':sum(r['passed'] is True for r in applicable),'failed_count':sum(r['passed'] is False for r in applicable),'reasons':reasons}
        if len(worlds)!=3:
            continue
        A,B,C=[worlds[w]['primary'] for w in 'ABC']
        valid=lambda r:r['status']=='ok'
        allinv=lambda key:all(r['invariants'][key] for r in subset)
        CAL={
            'CAL-1':allinv('analytic_bounds') and allinv('potential_bounds'),
            'CAL-2':all(r['identity_error']<=1e-9 for r in subset),
            'CAL-3':valid(A) and abs(A['bias'])<=3*A['MCSE'] and A['coverage']>=.93 and A['precision_ratio'] is not None and A['precision_ratio']>=3,
            'CAL-4':worlds['B']['support_passes']>=expected_count-1 and worlds['C']['support_passes']>=expected_count-1,
            'CAL-5':valid(B) and B['distinction_ratio'] is not None and B['distinction_ratio']>=2,
            'CAL-6':valid(B) and B['relative_bias']<=.10 and B['coverage']>=.90,
            'CAL-7':valid(C) and C['relative_bias']>=.50,
            'CAL-8':allinv('outcome_recomputed'),
            'CAL-9':None,
            'CAL-10':complete and len({(r['candidate'],r['world'],r['seed']) for r in subset})==len(subset) and all(r['purpose']==1 and 703000<=r['seed']<=703999 for r in subset),
            'CAL-11':allinv('counts'),
        }
        CAL={k:bool(v) if v is not None else None for k,v in CAL.items()}
        bT=np.mean([r['T'] for r in subset if r['world']=='B'])
        conflicts={d:conflict(worlds['B'][d],B,bT) for d in ('D1','D2')}
        review=any(d['status']=='not_evaluable' or d['conflict'] for d in conflicts.values())
        integrity=all(CAL[f'CAL-{i}'] for i in (2,8,10,11)) and allinv('csv_roundtrip') and allinv('individual_effects') and allinv('valid_csv')
        if not integrity:
            state='invalid_implementation'
        elif not all(CAL[f'CAL-{i}'] for i in (1,3,4,5,6,7)):
            state='failed'
        else:
            state='passed_review_required' if review else 'passed'
        output['candidates'][name]={'worlds':worlds,'CAL':CAL,'CAL9_status':'deferred_final_material_freeze','diagnostic_conflicts':conflicts,'state':state,'GEN':GEN}
    return output


def read_records(directory):
    records=[]
    for p in sorted(Path(directory).glob('K?/[ABC]/*/record.json')):
        if (p.parent/'COMPLETE').is_file():
            records.append(json.loads(p.read_text()))
    return records
