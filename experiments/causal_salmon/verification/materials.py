"""Construct only protocol-defined public materials by mechanical replacement."""
import re
import gzip
from pathlib import Path


def protocol_bytes(root):
    """Independently read the canonical protocol archive when supplied."""
    archive = Path(root) / 'manifests/frozen_protocol.md.gz'
    if archive.is_file():
        with gzip.open(archive, 'rb') as stream:
            return stream.read()
    return (Path(root) / 'planning.md').read_bytes()


def block(protocol, name):
    marked = protocol.split(f"<!-- material:{name} -->", 1)[1].split(f"<!-- /material:{name} -->", 1)[0]
    return re.search(r"```[^\n]*\n(.*?)```", marked, re.S).group(1)


def replacement_table(protocol):
    marked = protocol.split("<!-- material:table -->", 1)[1].split("<!-- /material:table -->", 1)[0]
    return re.findall(r"\| `([^`]+)` \| `([^`]+)` \|", marked)


def anonymize(text, table):
    table = sorted(table, key=lambda kv: len(kv[0]), reverse=True)
    lookup = dict(table)
    regex = re.compile(r"(?<![A-Za-z])(?:"+"|".join(re.escape(k) for k, _ in table)+r")(?![A-Za-z])")
    return regex.sub(lambda match: lookup[match.group(0)], text)


def construct(protocol, world, n, M, K):
    named = block(protocol, "named-"+world)
    anonymous = anonymize(named, replacement_table(protocol))
    if anonymous != block(protocol, "anon-"+world):
        raise ValueError("Mechanical anonymization disagrees with protocol")
    def fill(text):
        for key, value in {"N":n, "M":M, "K":K}.items():
            text = text.replace("{{"+key+"}}", str(value))
        if "{{" in text:
            raise ValueError("Residual slot")
        return text.encode()
    return {"named":fill(named), "anonymized":fill(anonymous)}


def verify_structure(protocol):
    texts = [block(protocol, "named-"+world) for world in "ABC"]
    def outside_assignment(text):
        return re.sub(r"(## 3\..*?\n).*?(?=## 4\.)", r"\1", text, flags=re.S)
    if len(set(map(outside_assignment, texts))) != 1:
        return False
    assignment = [re.search(r"## 3\.[^\n]*\n\n(.*?)\n\n## 4\.", text, re.S).group(1) for text in texts]
    return assignment[1].split(". ",1)[1] == assignment[2].split(". ",1)[1]


def extract_report(original):
    lines = original.splitlines(keepends=True)
    positions, outside, headings, fence = [], [], [], None
    offset = 0
    for i, raw in enumerate(lines):
        positions.append(offset)
        offset += len(raw)
        line = raw.rstrip("\r\n")
        indented = line.startswith("\t") or line.startswith("    ")
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        is_out = fence is None and not indented
        outside.append(is_out)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= fence[1] and not match.group(2).strip():
                fence = None
            continue
        if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
            fence = (match.group(1)[0],len(match.group(1)))
            continue
        if is_out and line.rstrip() == "## Final report":
            headings.append(i)
    if len(headings) != 1:
        return None, "heading_count=0" if not headings else "heading_count>1"
    start = headings[0]+1
    end = len(original)
    for i in range(start,len(lines)):
        if outside[i] and re.match(r"^#{1,2} ", lines[i]):
            end = positions[i]
            break
    body = original[positions[start] if start<len(lines) else len(original):end]
    return (body,None) if body.strip() else (None,"empty_report")
