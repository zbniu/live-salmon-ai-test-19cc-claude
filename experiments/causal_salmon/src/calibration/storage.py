"""Immutable per-repetition evidence and verified recovery."""
import hashlib
import json
from pathlib import Path


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def write_json(path,value):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,indent=2,allow_nan=False)
        f.write('\n')


def seal(directory):
    directory=Path(directory)
    files={str(p.relative_to(directory)):sha(p) for p in sorted(directory.rglob('*')) if p.is_file() and p.name not in ('evidence.sha256.json','COMPLETE')}
    write_json(directory/'evidence.sha256.json',files)
    (directory/'COMPLETE').write_text(sha(directory/'evidence.sha256.json')+'\n')


def validate_complete(directory):
    directory=Path(directory)
    try:
        if (directory/'COMPLETE').read_text().strip()!=sha(directory/'evidence.sha256.json'):
            return False
        manifest=json.loads((directory/'evidence.sha256.json').read_text())
        local_ok=all((directory/name).is_file() and sha(directory/name)==expected for name,expected in manifest.items())
        external=directory/'external_evidence.sha256.json'
        external_ok=not external.is_file() or all(Path(name).is_file() and sha(name)==expected for name,expected in json.loads(external.read_text()).items())
        return local_ok and external_ok
    except (OSError,ValueError):
        return False


def tree_hashes(root):
    root=Path(root)
    return {str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*.py')) if '__pycache__' not in p.parts}
