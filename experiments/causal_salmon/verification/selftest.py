"""Independent hand-array tests and registered-purpose selftest workloads."""
import os
for _key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[_key]='1'
import copy
import hashlib
import io
import json
from pathlib import Path
import time
import unittest
import uuid
import numpy as np
from .generator import generate, uniform, encode_csv, decode_csv, descending, hidden_csv
from .statistics import difference, standardized, coverage, partitions, stratified_difference, weighted_point, sigmoid, result, absent
from .materials import extract_report, construct, replacement_table, anonymize, verify_structure, block
from .evaluate import compute, check_gen, diagnostic_two
from .summary import metrics, conflict, make_summary
from .persistence import ROOT, write_once, json_bytes, hash_tree, environment, verify_complete, save_case
from .reference import run_reference

PROTOCOL=(ROOT/'planning.md').read_text()
CANDIDATES=json.loads((ROOT/'configs/calibration_candidates.json').read_text())['candidates']


class IndependentFixtures(unittest.TestCase):
    def test_random_raw_transform_and_registered_entropy(self):
        v=uniform([20260929,4,709000,1,1],2000)
        self.assertTrue(np.all((v>0)&(v<1)))
        self.assertTrue(np.array_equal(v,uniform([20260929,4,709000,1,1],2000)))
        self.assertFalse(np.array_equal(v,uniform([20260929,4,709000,2,1],2000)))
        with self.assertRaises(ValueError): generate(CANDIDATES[0],'A',720001,3)
        with self.assertRaises(ValueError): generate(CANDIDATES[0],'B',704000,1)

    def test_assignment_ties(self):
        p=np.array([1.,2.,2.,2.]); tie=np.array([1.,.4,.5,.5]); rows=np.array([0,1,2,3])
        self.assertEqual(descending(p,tie,rows).tolist(),[2,3,1,0])

    def test_csv_precision_and_rejections(self):
        x=np.array([0,1]); y=np.array([np.nextafter(45.,46.),75.]); z=np.array([-0.,np.nextafter(1.,2.)])
        data=encode_csv(x,y,z)
        self.assertEqual(data.splitlines()[1].split(b',')[-1],b'0')
        xp,yp,zp=decode_csv(data)
        np.testing.assert_array_equal(yp.view(np.uint64),y.view(np.uint64))
        self.assertEqual(zp[1],z[1])
        for invalid in (b'x,y,z\n2,1,2\n',b'x,y,z\n1,nan,2\n',b'x,y,z\r\n1,1,2\r\n',b'x,y,z\n1, 1,2\n'):
            with self.assertRaises(ValueError): decode_csv(invalid)

    def test_hand_difference_and_closed_interval(self):
        r=difference(np.array([1,1,0,0]),np.array([2.,4.,0.,2.]))
        self.assertEqual(r['E'],2.)
        self.assertAlmostEqual(r['se'],np.sqrt(2.))
        self.assertTrue(coverage(r,r['ci'][0])['covered'])
        self.assertTrue(coverage(r,r['ci'][1])['covered'])
        self.assertFalse(coverage(r,np.nextafter(r['ci'][1],np.inf))['covered'])

    def test_hand_four_column_hc3(self):
        x=np.array([0,0,0,1,1,1]); y=np.tile(np.array([-1.,0.,1.]),2); z=np.array([1.,-2.,1.,3.,0.,3.])
        r,d=standardized(x,y,z)
        self.assertEqual(r['status'],'ok')
        self.assertAlmostEqual(r['E'],2.)
        self.assertAlmostEqual(r['se'],np.sqrt(18.))
        self.assertAlmostEqual(d['max_leverage'],5/6)
        bad,_=standardized(x,np.zeros(6),z)
        self.assertEqual(bad['status'],'unavailable')
        # Four unique rows make a full-rank saturated model with leverage >= 1.
        saturated,_=standardized(np.array([0,0,1,1]),np.array([0.,1.,0.,1.]),np.array([0.,1.,1.,2.]))
        self.assertEqual(saturated['status'],'unavailable')

    def test_bin_edges_ties_and_missing_diagnostic(self):
        x=np.array([1]*10+[0]*8); y=np.array(list(range(10))+[0,2,4,6,8,9,10,-1],dtype=float)
        bins,_=partitions(x,y)
        self.assertEqual(bins['edges'],[0.,2.,4.,6.,8.,9.])
        self.assertEqual(bins['treated'],[2]*5)
        self.assertEqual(bins['control'],[1,1,1,1,2])
        d1,_=stratified_difference(x,y,np.arange(18,dtype=float))
        self.assertEqual(d1['status'],'unavailable')
        tied,_=partitions(np.array([1]*10+[0]*5),np.ones(15))
        self.assertEqual(tied['treated'],[0,0,0,0,10])

    def test_hand_weighting_and_failure(self):
        y=np.tile(np.array([-1.,0.,1.,-1.,0.,1.]),2)
        x=np.array([1]*6+[0]*6); z=1+y+2*x
        point=weighted_point(x,y,z)
        self.assertEqual(point['status'],'ok')
        self.assertAlmostEqual(point['E'],2.)
        self.assertAlmostEqual(point['ess'],6.)
        self.assertAlmostEqual(point['max_weight'],1/6)
        self.assertEqual(point['details']['iterations'],1)
        fail=weighted_point(np.array([1,1,0,0]),np.array([5.,6.,1.,2.]),np.ones(4))
        self.assertEqual(fail['reason'],'no_controls_in_support')
        np.testing.assert_array_equal(sigmoid(np.array([-1000.,0.,1000.])),[0.,.5,1.])

    def test_all_200_bootstraps_retained_when_original_fails(self):
        from unittest.mock import patch
        fake=dict(status='unavailable',E=None,max_weight=None,ess=None,reason='hand_fixture_hessian_failure',details=dict(iterations=1,support_n=12,support_control_n=6,newton=[]))
        x=np.array([1]*6+[0]*6); y=np.tile(np.arange(6,dtype=float),2); z=np.ones(12)
        with patch('verification.evaluate.weighted_point',return_value=fake) as fitted:
            diag,attempts,details=diagnostic_two(x,y,z,709000,4,'B',60.)
        self.assertEqual(fitted.call_count,201)
        self.assertEqual(len(attempts),200)
        self.assertEqual(diag['bootstrap_failures'],list(range(200)))
        self.assertIsNone(diag['se'])
        self.assertTrue(all(a['details']['support_control_n']==6 for a in attempts))

    def test_mechanical_materials_and_public_rules(self):
        self.assertTrue(verify_structure(PROTOCOL))
        table=replacement_table(PROTOCOL)
        self.assertEqual(anonymize('student students studentish Student start-of-term test score',table),'unit units studentish Student baseline measurement')
        for world in 'ABC':
            pair=construct(PROTOCOL,world,2000,900,600)
            self.assertEqual(anonymize(pair['named'].decode(),table).encode(),pair['anonymized'])
            self.assertNotIn(b'{{',pair['named'])
        self.assertNotIn('confound',block(PROTOCOL,'prompt'))

    def test_report_extraction_edges(self):
        body,error=extract_report('intro\r\n## Final report\r\nBody\r\n### Detail\r\nMore\r\n## End\r\nignored')
        self.assertIsNone(error); self.assertEqual(body,'Body\r\n### Detail\r\nMore\r\n')
        for text in ('```\n## Final report\n```\n', '    ## Final report\n', '## Final report\n \n', '## Final report\nA\n## Final report\nB'):
            self.assertIsNotNone(extract_report(text)[1])
        self.assertEqual(extract_report('~~~\n## Final report\n~~~\n## Final report\nreal')[0],'real')
        self.assertEqual(extract_report('```\n~~~\n## Final report\n```\n## Final report\nreal')[0],'real')

    def test_gen_thresholds_and_absent_values(self):
        inv={k:True for k in ('analytic_bounds','individual_effects','potential_bounds','csv_roundtrip','outcome_recomputed','counts','valid_csv')}
        bins=dict(treated=[2]*5,control=[20]*5)
        refs={v:dict(correct=True,format_valid=True,input_boundary_passed=True,method='insufficient_information',numeric=dict(N=3.,E=1.5,se=.1,ci=[1.304,1.696])) for v in ('named','anonymized')}
        p=coverage(result(1.5,.1),1.)
        checks=check_gen('C',inv,p,1.,3.,bins,refs,True)
        self.assertTrue(checks['GEN-6']['passed'])
        p['E']=np.nextafter(1.5,1.)
        self.assertFalse(check_gen('C',inv,p,1.,3.,bins,refs,True)['GEN-6']['passed'])
        self.assertIsNone(checks['GEN-4']['passed'])
        c=conflict(dict(status='ok',bias=.1,MCSE=.1,relative_bias=.1,coverage=.9),dict(status='ok',bias=.1,MCSE=.1),1.)
        self.assertEqual(c['criteria'],[False,False,False])
        self.assertEqual(conflict(dict(status='not_evaluable'),dict(status='ok'),1.)['status'],'not_evaluable')

    def test_all_record_aggregation_and_missing_diagnostics(self):
        records=[]
        for world in 'ABC':
            for i in range(1000):
                T=1.; error=.1 if i%2 else -.1
                E=(2. if world=='C' else 1.)+error
                primary=coverage(result(E,.2),T)
                na=absent('world_not_B','not_applicable')
                invariants={k:True for k in ('analytic_bounds','individual_effects','potential_bounds','csv_roundtrip','outcome_recomputed','counts','valid_csv')}
                gen={f'GEN-{j}':dict(applicable=True,passed=True,reasons=[]) for j in range(1,8)}
                records.append(dict(candidate='K1',world=world,seed=703000+i,purpose=1,T=T,N=4.,identity_error=0.,primary=primary,D1=primary.copy() if world=='B' else na.copy(),D2=primary.copy() if world=='B' else na.copy(),bins=dict(treated=[120]*5,control=[20]*5) if world!='A' else None,invariants=invariants,GEN=gen))
        summary=make_summary(records)['candidates']['K1']
        self.assertEqual(summary['state'],'passed')
        self.assertIsNone(summary['CAL']['CAL-9'])
        self.assertEqual(summary['worlds']['B']['D2']['count'],1000)
        records[1000]['D2']=absent('hand_fixture_failure')
        changed=make_summary(records)['candidates']['K1']
        self.assertEqual(changed['state'],'passed_review_required')
        self.assertEqual(changed['worlds']['B']['D2']['status'],'not_evaluable')
        self.assertIsNone(changed['worlds']['B']['D2']['bias'])

    def test_registered_selftest_seeds_all_candidates(self):
        for seed in range(709000,709010):
            for world in 'ABC':
                baseline=None
                for candidate in CANDIDATES:
                    public,projection,hidden,truth,invariants=generate(candidate,world,seed,4)
                    self.assertTrue(all(invariants.values()),(seed,world,candidate['id']))
                    self.assertEqual(truth['participants'],candidate['K'])
                    self.assertEqual(truth['applicants'],None if world=='A' else candidate['M'])
                    if baseline is None: baseline=hidden
                    else:
                        np.testing.assert_array_equal(hidden['y'],baseline['y'])
                        np.testing.assert_array_equal(hidden['u'],baseline['u'])
                    regenerated=generate(candidate,world,seed,4)[0]
                    self.assertEqual(public,regenerated)
                    self.assertNotIn('probe',str(truth['streams']))

    def test_public_runtime_isolation_each_world(self):
        for world in 'ABC':
            public,projection,_,_,_=generate(CANDIDATES[0],world,709000,4)
            pair=construct(PROTOCOL,world,2000,900,600)
            refs={version:run_reference(public,description) for version,description in pair.items()}
            self.assertEqual(refs['named']['numeric'],refs['anonymized']['numeric'])
            for ref in refs.values():
                self.assertTrue(ref['input_boundary_passed'])
                self.assertTrue(ref['correct']); self.assertTrue(ref['format_valid'])
                self.assertTrue(all(ref['probes'].values()))


def main():
    started=time.monotonic()
    stream=io.StringIO()
    outcome=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IndependentFixtures))
    uid=time.strftime('%Y%m%dT%H%M%S',time.gmtime())+'-'+uuid.uuid4().hex[:8]
    output_dir=ROOT/'verification/selftest_evidence'/uid
    output_dir.mkdir(parents=True)
    write_once(output_dir/'fixtures.txt',stream.getvalue().encode())
    if not outcome.wasSuccessful():
        print(stream.getvalue())
        write_once(output_dir/'result.json',json_bytes(dict(passed=False,tests_run=outcome.testsRun,elapsed_seconds=time.monotonic()-started)))
        raise SystemExit(1)
    benchmark=time.monotonic()
    computed=compute(CANDIDATES[0],'B',709000,4,PROTOCOL)
    path=save_case(ROOT/'verification/selftest_runs'/uid,ROOT/'verification/selftest_quality'/uid,computed)
    benchmark_seconds=time.monotonic()-benchmark
    record=computed[0]
    if record['D2']['bootstrap_successes']+len(record['D2']['bootstrap_failures'])!=200 or len(computed[4])!=200 or not verify_complete(path):
        raise AssertionError('Full diagnostic workload or persistence failed')
    # Hidden gzip is recoverable and numeric fields remain exact .17g values.
    import gzip
    recovered=gzip.decompress((path/'students.csv.gz').read_bytes())
    if recovered!=hidden_csv(computed[2]):
        raise AssertionError('Hidden serialization recovery failed')
    complete=dict(passed=True,tests_run=outcome.testsRun,fixture_failures=len(outcome.failures),fixture_errors=len(outcome.errors),seeds=[709000,709009],purpose=4,all_candidates=True,all_worlds=True,benchmark=dict(world='B',candidate='K1',seed=709000,purpose=4,seconds=benchmark_seconds,bootstrap_attempts=len(computed[4]),bootstrap_successes=record['D2']['bootstrap_successes'],bootstrap_failures=record['D2']['bootstrap_failures'],primary_status=record['primary']['status'],D1_status=record['D1']['status'],D2_status=record['D2']['status'],evidence_path=str(path)),elapsed_seconds=time.monotonic()-started,code=hash_tree(),environment=environment(),read_boundary='No src/, tests/, main implementation or results read')
    write_once(output_dir/'result.json',json_bytes(complete))
    print(stream.getvalue())
    print(json.dumps(dict(passed=True,tests=outcome.testsRun,benchmark_seconds=benchmark_seconds,bootstrap_successes=record['D2']['bootstrap_successes'],selftest_result=str(output_dir/'result.json'),code_sha256=complete['code']['aggregate_sha256'])))

if __name__=='__main__': main()
