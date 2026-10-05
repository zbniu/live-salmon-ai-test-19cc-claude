"""Independent all-repetition aggregation and CAL decisions."""
import collections
import math
import numpy as np

FIELDS = ['bias','MCSE','relative_bias','coverage','precision_ratio','distinction_ratio']


def metrics(records,method):
    applicable = [r for r in records if r[method]['status']!='not_applicable']
    status = 'not_applicable' if not applicable else 'ok'
    out = dict(status=status,count=len(applicable),**{k:None for k in FIELDS})
    if not applicable:
        return out
    if any(r[method]['status']!='ok' for r in applicable):
        out['status']='not_evaluable'
        return out
    E,T,N = [np.array([r[k] if k in ('T','N') else r[method]['E'] for r in applicable]) for k in ('E','T','N')]
    error = E-T
    sd = np.std(error,ddof=1)
    sdE = np.std(E,ddof=1)
    bias = np.mean(error)
    values = dict(bias=float(bias),MCSE=float(sd/np.sqrt(len(error))),relative_bias=float(abs(bias)/np.mean(T)),coverage=float(np.mean([r[method]['covered'] for r in applicable])),precision_ratio=float(np.mean(T)/sd) if sd>0 else None,distinction_ratio=float(np.mean(N-E)/sdE) if sdE>0 else None)
    if any(v is not None and not math.isfinite(v) for v in values.values()):
        out['status']='not_evaluable'
    else:
        out.update(values)
    return out


def conflict(diagnostic,primary,mean_truth):
    if diagnostic['status']!='ok' or primary['status']!='ok':
        return dict(status='not_evaluable',conflict=None,criteria=None)
    delta = abs(diagnostic['bias']-primary['bias'])
    criteria = [diagnostic['relative_bias']>.1,diagnostic['coverage']<.9,delta/mean_truth>.05 and delta>3*math.sqrt(diagnostic['MCSE']**2+primary['MCSE']**2)]
    return dict(status='ok',conflict=any(criteria),criteria=criteria)


def make_summary(records,expected=1000,material_structure=True):
    candidates = {}
    for cid in sorted({r['candidate'] for r in records}):
        own = [r for r in records if r['candidate']==cid]
        worlds,gen = {},{}
        for world in 'ABC':
            subset=[r for r in own if r['world']==world]
            if not subset:
                continue
            worlds[world]={k:metrics(subset,k) for k in ('primary','D1','D2')}
            worlds[world]['support_passes']=None if world=='A' else sum(min(r['bins']['control'])>=20 for r in subset)
            gen[world]={}
            for key in [f'GEN-{i}' for i in range(1,8)]:
                checks=[r['GEN'][key] for r in subset]
                reasons=collections.Counter(reason for c in checks for reason in c['reasons'])
                gen[world][key]=dict(applicable_count=sum(c['applicable'] for c in checks),passed_count=sum(c['passed'] is True for c in checks),failed_count=sum(c['passed'] is False for c in checks),reasons=dict(sorted(reasons.items())))
        if set(worlds)!=set('ABC'):
            candidates[cid]=dict(worlds=worlds,GEN=gen,state='incomplete',CAL={},diagnostic_conflicts={})
            continue
        A,B,C=(worlds[w]['primary'] for w in 'ABC')
        cal={f'CAL-{i}':False for i in range(1,12)}
        cal['CAL-1']=all(r['invariants']['analytic_bounds'] and r['invariants']['potential_bounds'] for r in own)
        cal['CAL-2']=all(r['identity_error']<=1e-9 for r in own)
        cal['CAL-3']=bool(A['status']=='ok' and abs(A['bias'])<=3*A['MCSE'] and A['coverage']>=.93 and A['precision_ratio'] is not None and A['precision_ratio']>=3)
        cal['CAL-4']=worlds['B']['support_passes']>=999 and worlds['C']['support_passes']>=999
        cal['CAL-5']=bool(B['status']=='ok' and B['distinction_ratio'] is not None and B['distinction_ratio']>=2)
        cal['CAL-6']=bool(B['status']=='ok' and B['relative_bias']<=.1 and B['coverage']>=.9)
        cal['CAL-7']=bool(C['status']=='ok' and C['relative_bias']>=.5)
        cal['CAL-8']=all(r['invariants']['outcome_recomputed'] for r in own)
        cal['CAL-9']=None
        cal['CAL-10']=all(len([r for r in own if r['world']==w])==expected and {r['seed'] for r in own if r['world']==w}==set(range(703000,704000)) and all(r['purpose']==1 for r in own if r['world']==w) for w in 'ABC')
        cal['CAL-11']=all(r['invariants']['counts'] for r in own)
        b_records=[r for r in own if r['world']=='B']
        mean_truth=float(np.mean([r['T'] for r in b_records]))
        conflicts={k:conflict(worlds['B'][k],B,mean_truth) for k in ('D1','D2')}
        invalid = not all(cal[k] for k in ('CAL-2','CAL-8','CAL-10','CAL-11')) or not material_structure or any(not r['invariants']['csv_roundtrip'] or not r['invariants']['valid_csv'] or not r['GEN']['GEN-2']['passed'] or not r['GEN']['GEN-7']['passed'] for r in own) or (all(r['invariants']['analytic_bounds'] for r in own) and any(not r['invariants']['potential_bounds'] for r in own))
        hard = all(cal[f'CAL-{i}'] for i in (1,3,4,5,6,7))
        review = any(c['status']=='not_evaluable' or c['conflict'] for c in conflicts.values())
        state = 'invalid_implementation' if invalid else ('failed' if not hard else ('passed_review_required' if review else 'passed'))
        candidates[cid]=dict(worlds=worlds,CAL=cal,CAL9_status='deferred_final_material_freeze',diagnostic_conflicts=conflicts,state=state,GEN=gen)
    return dict(candidates=candidates)
