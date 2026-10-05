"""Freeze confirmed public descriptions; never generate study data."""
import difflib
import json
import hashlib
from pathlib import Path

from src.data.materials import anonymize, check_materials, description, substitutions, templates, protocol_bytes
from src.calibration.storage import sha, write_json

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = 'f85fedf447c734d9d5e7a2cb630284fe18c7091c5cf653610adbc43ec8e7144c'


def put(path, data):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise RuntimeError('Existing frozen material differs: ' + str(path))
    else:
        with path.open('xb') as stream:
            stream.write(data)


def main():
    if hashlib.sha256(protocol_bytes()).hexdigest() != PROTOCOL:
        raise RuntimeError('Protocol identity changed')
    selected = json.loads((ROOT / 'configs/selected_parameters.json').read_text())
    confirmation = json.loads((ROOT / selected['confirmation_record']).read_text())
    if selected['status'] != 'confirmed' or selected['candidate'] != 'K1':
        raise RuntimeError('Original K1 complete-row confirmation required')
    if confirmation['selected_configuration_sha256'] != sha(ROOT / 'configs/selected_parameters.json'):
        raise RuntimeError('Confirmation/configuration identity mismatch')
    parameters = selected['parameters']
    if parameters != confirmation['confirmed_complete_row']:
        raise RuntimeError('Confirmed complete row differs')
    check_materials(parameters['M'], parameters['K'])
    texts = {}
    paths = []
    for world in 'ABC':
        for version in ('named', 'anonymized'):
            rel = f'materials/{version}/{world}.md'
            data = description(world, version, parameters['M'], parameters['K']).encode()
            put(rel, data)
            paths.append(rel)
            texts[world, version] = data.decode()
        if anonymize(texts[world, 'named']) != texts[world, 'anonymized']:
            raise RuntimeError('Mechanical substitution differs')
    _, _, prompt = templates()
    put('materials/prompt.txt', prompt.encode())
    table = {'replacements': [list(pair) for pair in substitutions()]}
    put('materials/substitutions.json', (json.dumps(table, indent=2, allow_nan=False) + '\n').encode())
    paths += ['materials/prompt.txt', 'materials/substitutions.json']
    checks = {
        'CAL-9-description-pairing': True,
        'ACC-3-description-pairing': True,
        'ACC-4': True,
        'CSV-pairing': 'checked_after_each_fixed_dataset_is_generated',
        'world_assignment_only_differences': True,
        'B_C_only_first_assignment_sentence_differs': True,
        'residual_slots': False,
        'mechanical_diffs': {
            w: list(difflib.unified_diff(texts[w, 'named'].splitlines(), texts[w, 'anonymized'].splitlines(), fromfile='named', tofile='anonymized', lineterm=''))
            for w in 'ABC'
        },
    }
    configuration = {
        'schema_version': 1,
        'status': 'public_materials_frozen',
        'candidate': 'K1',
        'parameters': parameters,
        'protocol_sha256': PROTOCOL,
        'selected_parameters_sha256': sha(ROOT / 'configs/selected_parameters.json'),
        'parameter_confirmation_sha256': sha(ROOT / selected['confirmation_record']),
        'seed_registration_sha256': sha(ROOT / 'configs/seeds.json'),
        'calibration_report_sha256': selected['calibration_report_sha256'],
        'materials': {rel: sha(ROOT / rel) for rel in paths},
        'fixed_datasets_generated': False,
        'tested_model_calls': 0,
    }
    target = ROOT / 'configs/frozen_study.json'
    if target.exists():
        if json.loads(target.read_text()) != configuration:
            raise RuntimeError('Frozen configuration differs')
    else:
        write_json(target, configuration)
    receipt = {'schema_version': 1, 'protocol_sha256': PROTOCOL,
               'configuration_sha256': sha(target), 'checks': checks,
               'material_files': configuration['materials'],
               'freeze_program_sha256': sha(Path(__file__))}
    frozen = ROOT / 'manifests/freeze.json'
    if frozen.exists():
        if json.loads(frozen.read_text()) != receipt:
            raise RuntimeError('Frozen receipt differs')
    else:
        write_json(frozen, receipt)
    print(json.dumps({'materials': len(paths), 'description_checks_passed': True,
                      'freeze_sha256': sha(frozen), 'fixed_datasets_generated': False}))


if __name__ == '__main__':
    main()
