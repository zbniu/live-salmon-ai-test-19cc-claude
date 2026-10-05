"""Independent per-case computation and hidden quality checks."""
import numpy as np
from .generator import generate, uniform, WORLD, STUDY
from .materials import construct, anonymize, replacement_table
from .reference import run_reference
from .statistics import absent, result, coverage, difference, standardized, partitions, stratified_difference, weighted_point


def diagnostic_two(x,y,z,seed,purpose,world,mu_y):
    point = weighted_point(x,y,z,mu_y)
    Trows,Crows = np.flatnonzero(x==1),np.flatnonzero(x==0)
    K,n = len(Trows),len(x)
    attempts = []
    for index in range(200):
        entropy = [STUDY,purpose,seed,WORLD[world],20,index]
        v = uniform(entropy,n)
        tindex = np.minimum(np.floor(v[:K]*K).astype(np.int64),K-1)
        cindex = np.minimum(np.floor(v[K:]*len(Crows)).astype(np.int64),len(Crows)-1)
        rows = np.concatenate((Trows[tindex],Crows[cindex]))
        boot = weighted_point(x[rows],y[rows],z[rows],mu_y)
        detail = boot['details'] if boot['status'] != 'ok' else dict(iterations=boot['details']['iterations'],support_n=boot['details']['support_n'],support_control_n=boot['details']['support_control_n'])
        attempts.append(dict(index=index,status=boot['status'],E=boot['E'],reason=boot['reason'],details=detail))
    failures = [r['index'] for r in attempts if r['status']!='ok']
    if point['status'] != 'ok' or failures:
        estimate = absent(point['reason'] if point['status']!='ok' else 'bootstrap_attempt_unavailable')
        estimate['E'] = point['E']
    else:
        estimate = result(point['E'],np.std([r['E'] for r in attempts],ddof=1))
    estimate.update(max_weight=point['max_weight'],ess=point['ess'],bootstrap_successes=200-len(failures),bootstrap_failures=failures)
    return estimate,attempts,point['details']


def check_gen(world,invariants,primary,T,N,bins,refs,pairing):
    gen = {}
    def check(key,applicable,conditions):
        reasons = [reason for condition,reason in conditions if not condition] if applicable else []
        gen[key] = dict(applicable=applicable,passed=not reasons if applicable else None,reasons=reasons)
    check('GEN-1',True,[(invariants['individual_effects'],'individual_effects'),(invariants['potential_bounds'],'potential_final_score_bounds'),(invariants['counts'],'fixed_counts'),(invariants['csv_roundtrip'],'public_hidden_roundtrip'),(invariants['outcome_recomputed'],'hidden_outcome_recomputation'),(invariants['valid_csv'],'csv_validation')])
    check('GEN-2',True,[(all(r['input_boundary_passed'] for r in refs.values()),'public_input_boundary'),(all(r['correct'] for r in refs.values()),'reference_correctness'),(all(r['format_valid'] for r in refs.values()),'final_report_format')])
    check('GEN-3',world!='A',[(bins is not None and min(bins['treated'])>=2,'bin_treated_count'),(bins is not None and min(bins['control'])>=20,'bin_control_count'),(primary['status']=='ok','primary_computable')])
    check('GEN-4',world in 'AB',[(T>0,'truth_positive'),(primary['se'] is not None and primary['se']>0,'standard_error_positive'),(primary['se'] is not None and primary['se']>0 and T/primary['se']>=3,'case_precision_ratio'),(primary['covered'] is True,'interval_covers_truth'),(primary['ci'] is not None and primary['ci'][0]>0,'lower_interval_positive')])
    check('GEN-5',world=='B',[(N>T,'raw_above_truth'),(primary['E'] is not None and N>primary['E'],'raw_above_adjusted'),(primary['E'] is not None and abs(primary['E']-T)<abs(N-T),'adjustment_reduces_error'),(all(r['method']=='standardized_ols' and r['correct'] for r in refs.values()),'adjustment_executed_and_adopted')])
    check('GEN-6',world=='C',[(all(r['method']=='insufficient_information' and r['correct'] for r in refs.values()),'public_insufficiency_without_hard_claim'),(T>0 and primary['E'] is not None and abs(primary['E']-T)/T>=.50,'case_relative_deviation')])
    check('GEN-7',True,[(pairing,'mechanical_material_pairing'),(all(r['correct'] for r in refs.values()),'paired_reference_correctness'),(refs['named']['numeric']==refs['anonymized']['numeric'],'paired_numeric_identity')])
    return gen


def compute(candidate,world,seed,purpose,protocol):
    public,projection,hidden,truth,invariants = generate(candidate,world,seed,purpose)
    x,y,z = projection
    T = truth['T']
    raw = difference(x,z)
    N = raw['E']
    detail = {}
    if world=='A':
        primary,bins = raw,None
    else:
        primary,detail = standardized(x,y,z)
        bins,_ = partitions(x,y)
    primary = coverage(primary,T)
    bootstrap=[]
    if world=='B':
        d1,_ = stratified_difference(x,y,z)
        d2,bootstrap,d2detail = diagnostic_two(x,y,z,seed,purpose,world,candidate["a"]+15)
        detail['D2_point'] = d2detail
        d1,d2 = coverage(d1,T),coverage(d2,T)
    else:
        d1 = absent('world_not_B','not_applicable')
        d2 = {**absent('world_not_B','not_applicable'), 'max_weight':None,'ess':None,'bootstrap_successes':0,'bootstrap_failures':[]}
    descriptions = construct(protocol,world,len(x),candidate['M'],candidate['K'])
    refs = {version:run_reference(public,text) for version,text in descriptions.items()}
    pairing = anonymize(descriptions['named'].decode(),replacement_table(protocol)).encode()==descriptions['anonymized']
    record = dict(candidate=candidate['id'],world=world,seed=seed,purpose=purpose,csv_sha256=truth['csv_sha256'],x=x.tolist(),n=len(x),participants=int(sum(x)),applicants=truth['applicants'],T=T,identity_error=float(abs(np.mean((hidden['z1']-hidden['z0'])[x==1])-.1*np.mean(hidden['m'][x==1]))),N=N,primary=primary,D1=d1,D2=d2,bins=bins,invariants=invariants,GEN=check_gen(world,invariants,primary,T,N,bins,refs,pairing),reference={v:{k:r[k] for k in ('input_hashes','method','correct','format_valid','input_boundary_passed','numeric')} for v,r in refs.items()},details=detail)
    return record,public,hidden,truth,bootstrap,descriptions,refs
