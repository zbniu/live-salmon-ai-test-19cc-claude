"""Hidden-side quality checks consume outputs, never transmit truth to analysis."""
import numpy as np


def qualify(record,paired_materials_ok):
    world=record['world']
    r=record['primary']
    T,N=record['T'],record['N']
    refs=record['reference']
    output={}
    def check(i,applicable,conditions):
        reasons=[name for name,ok in conditions if not ok] if applicable else []
        output[f'GEN-{i}']={'applicable':applicable,'passed':not reasons if applicable else None,'reasons':reasons}
    inv=record['invariants']
    check(1,True,[(name,inv[name]) for name in ('individual_effects','potential_bounds','counts','csv_roundtrip','outcome_recomputed','valid_csv')])
    check(2,True,[(f'{v}_{field}',ref[field]) for v,ref in refs.items() for field in ('correct','format_valid','input_boundary_passed')])
    bins=record['bins']
    check(3,world!='A',[('treated_segment_below_2',bins is not None and min(bins['treated'])>=2),('control_segment_below_20',bins is not None and min(bins['control'])>=20),('primary_unavailable',r['status']=='ok')])
    primary_ok=r['status']=='ok'
    check(4,world in 'AB',[('nonpositive_truth',T>0),('nonpositive_or_unavailable_se',primary_ok and r['se']>0),('precision_below_3',primary_ok and r['se']>0 and T/r['se']>=3),('interval_misses_truth',primary_ok and r['covered']),('lower_interval_not_positive',primary_ok and r['ci'][0]>0)])
    check(5,world=='B',[('raw_not_above_truth',N>T),('raw_not_above_adjusted',primary_ok and N>r['E']),('adjustment_does_not_improve_error',primary_ok and abs(r['E']-T)<abs(N-T)),('adjustment_not_adopted',all(ref['method']=='standardized_ols' and ref['correct'] for ref in refs.values()))])
    check(6,world=='C',[('insufficiency_not_stated',all(ref['method']=='insufficient_information' and ref['correct'] for ref in refs.values())),('adjusted_relative_error_below_half',primary_ok and abs(r['E']-T)/T>=.5)])
    a,b=refs['named'],refs['anonymized']
    equal=all(np.array_equal(a['numeric'][k],b['numeric'][k]) for k in ('N','E','se','ci'))
    check(7,True,[('paired_materials_mismatch',paired_materials_ok),('paired_csv_mismatch',a['input_hashes']['data.csv']==b['input_hashes']['data.csv']==record['csv_sha256']),('paired_task_incorrect',a['correct'] and b['correct']),('paired_numeric_mismatch',equal)])
    return output
