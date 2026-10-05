"""Verify this public submission without executing submitted model programs."""
import csv
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def public_file(path):
    rel = path.relative_to(ROOT)
    return (path.is_file() and not any(p in {'.packaging', '.venv', '.git', '__pycache__', '.pytest_cache'} for p in rel.parts)
            and path.name != '.DS_Store'
            and not any(p.startswith('selftest_') for p in rel.parts))

def main():
    manifest_path = ROOT / 'manifests/submission_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    listed = set(manifest['files'])
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if public_file(p) and p != manifest_path}
    assert actual == listed, f'File inventory differs: added={actual-listed}, missing={listed-actual}'
    for name, expected in manifest['files'].items():
        assert sha(ROOT/name) == expected, f'Changed public file: {name}'
    cfg = json.loads((ROOT/'configs/submission.json').read_text())
    assert sha(ROOT/cfg['prompt']) == cfg['prompt_sha256']
    assert sha(ROOT/cfg['rubric']) == cfg['rubric_sha256']
    assert cfg['answers'] == 72
    translation = json.loads((ROOT/'manifests/translation.json').read_text())
    original_protocol = gzip.decompress((ROOT/'manifests/frozen_protocol.md.gz').read_bytes())
    assert hashlib.sha256(original_protocol).hexdigest() == translation['original_protocol_sha256']
    assert sha(ROOT/'planning.md') == translation['english_protocol_sha256']
    for key in ['named-'+w for w in 'ABC'] + ['anon-'+w for w in 'ABC'] + ['prompt']:
        pattern = r'<!-- material:'+key+r' -->\n```[^\n]*\n(.*?)\n```\n<!-- /material:'+key+r' -->'
        assert re.search(pattern, original_protocol.decode('utf-8'), re.S)[1] == re.search(pattern, (ROOT/'planning.md').read_text(), re.S)[1], key
    non_english = []
    for path in ROOT.rglob('*'):
        if not public_file(path):
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeError:
            continue
        if re.search('[\u3400-\u4dbf\u4e00-\u9fff]', text):
            non_english.append(str(path.relative_to(ROOT)))
    assert not non_english, non_english
    artifacts = rows(ROOT/'results/submissions/INDEX.csv')
    assert len(artifacts) == 915
    assert len({r['artifact_path'] for r in artifacts}) == 915
    for row in artifacts:
        digest = sha(ROOT/'results/submissions'/row['artifact_path'])
        assert digest == row['source_sha256'] == row['copy_sha256'], row['artifact_path']
    cases = rows(ROOT/'results/tables/case_results.csv')
    evidence = rows(ROOT/'results/submissions/CASE_INDEX.csv')
    assert len(cases) == len(evidence) == 72
    assert len({(r['model_label'],r['case_id']) for r in cases}) == 72
    counts = Counter(r['primary_result'] for r in cases)
    assert set(counts) <= {'PASS', 'FAIL', 'UNKNOWN'}, dict(counts)
    grades = {grade: counts[grade] for grade in ('PASS', 'FAIL', 'UNKNOWN')}
    assert dict(grades) == cfg['grades'], dict(grades)
    assert Counter(r['world'] for r in cases) == dict(A=24,B=24,C=24)
    by_model = defaultdict(list)
    evidence_map = {(r['model_label'],r['case_id']):r for r in evidence}
    for row in cases:
        by_model[row['model_label']].append(row)
        erow = evidence_map[row['model_label'],row['case_id']]
        assert all(row[k] == erow[k] for k in ('world','seed','semantic_version','csv_sha256','primary_result'))
        for key in ('report_path','code_path','results_path','evidence_index_path'):
            path = ROOT/row[key]
            assert path.exists(), row[key]
            if path.is_file(): assert path.stat().st_size > 0, row[key]
            else: assert any(p.is_file() and p.stat().st_size > 0 for p in path.rglob('*')), row[key]
        assert row['rule_version'] == '1.3'
        if row['reported_effect']:
            assert abs(abs(float(row['reported_effect'])-float(row['satt_true']))-float(row['EEE'])) < 1e-12
        else: assert row['EEE'] == '', 'Missing estimates must not become zero errors'
    summaries = rows(ROOT/'results/tables/model_summary.csv')
    assert len(by_model) == len(summaries) == 6
    for model_id,label in cfg['models'].items():
        score_rows=by_model[label]
        assert len(score_rows)==12 and {r['case_id'] for r in score_rows} == set(cfg['formal_case_ids'])
        assert rows(ROOT/f'results/evaluations/{model_id}/case_scores.csv') == score_rows
    paired=rows(ROOT/'results/tables/semantic_pairs.csv')
    assert len(paired) == 36
    groups=defaultdict(list)
    for row in cases: groups[(row['model_label'],row['world'],row['seed'])].append(row)
    assert len(groups)==36
    for group in groups.values():
        assert len(group)==2 and {r['semantic_version'] for r in group} == {'named','anonymized'}
        assert len({r['csv_sha256'] for r in group})==1
        assert len({r['primary_result'] for r in group})==1
    materials=rows(ROOT/'configs/case_index.csv')
    assert len(materials)==24
    material_map={r['case_id']:r for r in materials}
    for row in materials:
        assert sha(ROOT/row['data_path'])==row['csv_sha256']
        assert sha(ROOT/row['description_path'])==row['description_sha256']
    for row in cases:
        m=material_map[row['case_id']]
        assert m['included_in_final_results']=='true'
        assert all(row[k]==m[k] for k in ('world','seed','semantic_version','csv_sha256'))
    assert len({r['csv_sha256'] for r in cases})==6
    selected=list((ROOT/'datasets/public').rglob('data.csv'))
    pool=rows(ROOT/'results/quality_checks/data/POOL_INDEX.csv')
    assert len(selected)==12 and len(pool)==60
    assert sum(r['qualified']=='True' for r in pool)==56
    for row in pool:
        assert sha(ROOT/row['candidate_public_csv'])==row['csv_sha256']
    for path in selected:
        data=rows(path)
        assert len(data)==2000 and list(data[0])==['x','y','z']
        assert sum(int(r['x']) for r in data)==600
    broken=[]; local_links=0
    for md in ROOT.rglob('*.md'):
        if not public_file(md): continue
        body=md.read_text(encoding='utf-8')
        # Inline and fenced code can contain mathematical ]( sequences,
        # which are not Markdown links in the rendered document.
        body=re.sub(r'(`+)(.*?)\1', '', body, flags=re.S)
        for match in re.finditer(r'\]\(([^\n)]+)\)',body):
            target=match.group(1).strip()
            if target.startswith('<'): target=target[1:target.find('>')]
            else: target=target.split(' "',1)[0]
            parsed=urlsplit(target)
            if parsed.scheme or target.startswith('#'): continue
            path=unquote(parsed.path)
            if not path: continue
            local_links+=1
            if not (md.parent/path).exists(): broken.append([str(md.relative_to(ROOT)),target])
    assert not broken, f'Broken local links: {broken}'
    assert not (ROOT/'datasets/ground_truth').exists()
    assert not (ROOT/'results/quality_checks/data/candidate_storage/main/ground_truth').exists()
    assert not any(p.name in {'final_data_private_probe.txt','students.csv.gz'} for p in ROOT.rglob('*') if public_file(p))
    print(json.dumps(dict(public_package_verified=True,public_files=len(listed)+1,
                         original_artifacts=915,answers=72,grades=dict(grades),semantic_pairs=36,
                         unique_used_numeric_datasets=6,selected_datasets=12,pool_candidates=60,
                         rejected_candidates=4,local_links_checked=local_links,
                         public_text_is_English=True,tested_models_or_submitted_code_executed=False),indent=2))

if __name__ == '__main__':
    main()
