import json
from pathlib import Path

import numpy as np


def test_original_d2_failure_still_preserves_all_bootstrap_attempts():
    from src.calibration.statistics import weighted_diagnostic
    x=np.repeat([1,0],10)
    y=np.ones(20)
    r,boot=weighted_diagnostic(x,y,np.arange(20.),1.,709001,4,2)
    assert r['status']=='unavailable'
    assert len(boot)==200 and r['bootstrap_failures']==list(range(200))
    assert all(b['reason']=='hessian_unsolvable' for b in boot)
    assert all(b['details']['hessian_rank']==1 for b in boot)


def test_comparison_checks_bootstraps_nulls_and_decisions():
    from src.reporting.compare import compare_values
    issues=[]
    compare_values({'E':1.,'status':'ok','covered':True},{'E':1.+1e-9,'status':'ok','covered':True},'case',issues)
    assert issues==[]
    compare_values({'E':None,'covered':False},{'E':1.,'covered':True},'case',issues)
    assert len(issues)==2
    issues=[]
    compare_values([{'index':0,'status':'ok','E':1.}],[{'index':0,'status':'ok','E':1.1}],'bootstrap',issues)
    assert len(issues)==1


def test_public_numeric_failure_is_recorded_not_lost():
    from src.calibration.public_reference import analyze
    import tempfile
    root=Path(__file__).resolve().parents[1]
    from src.data.materials import description
    with tempfile.TemporaryDirectory() as temporary:
        p=Path(temporary)
        (p/'data.csv').write_text('x,y,z\n'+''.join(f'{i%2},60,{i}\n' for i in range(20)))
        (p/'STUDY_DESCRIPTION.md').write_text(description('B','named',900,600))
        out=analyze(p/'data.csv',p/'STUDY_DESCRIPTION.md')
    assert not out['correct'] and out['numeric']['E'] is None
    assert out['analysis']['failure']=='rank_below_four'
