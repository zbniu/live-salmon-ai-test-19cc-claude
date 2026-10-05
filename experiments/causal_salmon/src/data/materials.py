"""Backend material preparation. This module never enters reference runtime."""
import re
import gzip
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def protocol_bytes():
    """Read canonical frozen bytes; English planning.md is a reading translation."""
    archive = ROOT / 'manifests/frozen_protocol.md.gz'
    return gzip.decompress(archive.read_bytes()) if archive.exists() else (ROOT / 'planning.md').read_bytes()


@lru_cache
def templates():
    source=protocol_bytes().decode('utf-8')
    def block(key, fence):
        m=re.search(r'<!-- material:'+re.escape(key)+r' -->\n```'+fence+r'\n(.*?)\n```\n<!-- /material:'+re.escape(key)+r' -->',source,re.S)
        if not m:
            raise ValueError('Missing frozen material '+key)
        return m.group(1)+'\n'
    return ({w:block('named-'+w,'markdown') for w in 'ABC'}, {w:block('anon-'+w,'markdown') for w in 'ABC'},block('prompt','text'))


@lru_cache
def substitutions():
    source=protocol_bytes().decode('utf-8')
    table=source.split('<!-- material:table -->')[1].split('<!-- /material:table -->')[0]
    return re.findall(r'\| `([^`]+)` \| `([^`]+)` \|',table)


def anonymize(text):
    replacements=dict(substitutions())
    pattern=re.compile(r'(?<![A-Za-z])(?:'+'|'.join(re.escape(k) for k in sorted(replacements,key=len,reverse=True))+r')(?![A-Za-z])')
    return pattern.sub(lambda m:replacements[m.group(0)],text)


def description(world,version,M,K):
    named,anon,_=templates()
    original=named[world] if version=='named' else anonymize(named[world])
    if version!='named' and original!=anon[world]:
        raise ValueError('Mechanical anonymous template mismatch')
    return original.replace('{{N}}','2000').replace('{{M}}',str(M)).replace('{{K}}',str(K))


def identify_assignment(text):
    paragraph=text.split('## 3. ')[1].split('## 4. ')[0]
    if 'by a random draw' in paragraph and 'same chance' in paragraph and 'used no information' in paragraph:
        return 'random_difference'
    if 'made of three parts' in paragraph and 'were not recorded' in paragraph:
        return 'insufficient_information'
    if 'made of two parts' in paragraph and 'no other characteristic' in paragraph and 'descending order' in paragraph:
        return 'standardized_ols'
    raise ValueError('Public assignment description does not match registered rules')


def check_materials(M,K):
    named,anon,prompt=templates()
    for world in 'ABC':
        assert anonymize(named[world])==anon[world]
        a=description(world,'anonymized',M,K)
        assert not re.search('student|tutor|class|test|score|term|school|teacher|pupil|applicant|application|admit|attend|grade|lesson|exam',a,re.I)
        for version in ('named','anonymized'):
            d=description(world,version,M,K)
            assert '{{' not in d
            assert set(map(int,re.findall(r'\d+',d))) <= {0,1,2,3,4,5,6,100,2000,M,K}
            assert not re.search(r'SATT|Gumbel|World [ABC]|u_i|m_i|10%|0\.10',d)
    outside=lambda t:t.split('## 3. ')[0]+t.split('## 4. ')[1]
    assert outside(named['A'])==outside(named['B'])==outside(named['C'])
    par=lambda w:named[w].split('## 3. ')[1].split('## 4. ')[0].split('\n\n',1)[1]
    assert par('B').split('. ',1)[1]==par('C').split('. ',1)[1]
    assert not re.search('causal|identif|confound|adjust|random',prompt,re.I)
    return True
