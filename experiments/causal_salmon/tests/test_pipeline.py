import json
from pathlib import Path

import numpy as np


def test_reference_runtime_is_public_only(tmp_path):
    from src.calibration.isolation import reference, preflight
    from src.data.generator import generate,csv_bytes
    from src.data.materials import description
    root=Path(__file__).resolve().parents[1]
    p=json.loads((root/'configs/calibration_candidates.json').read_text())['candidates'][0]
    d=generate(p,'B',709000,4)
    (tmp_path/'data.csv').write_bytes(csv_bytes(d['x'],d['y'],d['z']))
    (tmp_path/'STUDY_DESCRIPTION.md').write_text(description('B','named',900,600))
    assert all(preflight(tmp_path).values())
    out,audit=reference(tmp_path)
    assert out['method']=='standardized_ols'
    assert out['correct'] and out['format_valid'] and out['input_boundary_passed']
    assert set(out['input_hashes'])=={'data.csv','STUDY_DESCRIPTION.md'}
    assert len(audit['data_inputs'])==2 and audit['network']=='denied'


def test_full_d2_attempts_and_repeatability():
    from src.data.generator import generate
    from src.calibration.statistics import weighted_diagnostic
    root=Path(__file__).resolve().parents[1]
    p=json.loads((root/'configs/calibration_candidates.json').read_text())['candidates'][0]
    d=generate(p,'B',709000,4)
    a,ab=weighted_diagnostic(d['x'],d['y'],d['z'],60,709000,4,2)
    b,bb=weighted_diagnostic(d['x'],d['y'],d['z'],60,709000,4,2)
    assert a==b and ab==bb
    assert len(ab)==200
    assert a['bootstrap_successes']+len(a['bootstrap_failures'])==200
    assert [v['index'] for v in ab]==list(range(200))


def test_missing_diagnostic_invalidates_full_aggregate():
    from src.calibration.summary import metrics,conflict
    samples=[{'status':'ok','E':1.,'covered':True},{'status':'unavailable','E':None,'covered':None}]
    aggregate=metrics(samples,np.array([1.,1.]),np.array([2.,2.]))
    assert aggregate['status']=='not_evaluable' and aggregate['bias'] is None and aggregate['coverage'] is None
    assert conflict(aggregate,aggregate,1.)['status']=='not_evaluable'


def test_resume_rejects_tampering_and_preserves_complete_case(tmp_path):
    from src.calibration.storage import write_json,seal,validate_complete
    (tmp_path/'data.csv').write_bytes(b'x,y,z\n1,1,1\n')
    write_json(tmp_path/'record.json',{'seed':709000})
    seal(tmp_path)
    assert validate_complete(tmp_path)
    (tmp_path/'data.csv').write_bytes(b'x,y,z\n1,2,1\n')
    assert not validate_complete(tmp_path)
