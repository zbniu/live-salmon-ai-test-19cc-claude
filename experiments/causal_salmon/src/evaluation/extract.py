"""Appendix D.2, preserving original report bytes/characters."""
import re


def extract_report(answer):
    original_lines=answer.splitlines(keepends=True)
    lines=[line.replace('\r\n','\n').rstrip('\n') for line in original_lines]
    outside=[]
    fence=None
    candidates=[]
    for i,line in enumerate(lines):
        outside.append(fence is None)
        if fence:
            if re.fullmatch(r' {0,3}'+re.escape(fence[0])+r'{'+str(fence[1])+r',}[ \t]*',line):
                fence=None
            continue
        opening=re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$',line)
        if opening and not (opening.group(1)[0]=='`' and '`' in opening.group(2)):
            fence=(opening.group(1)[0],len(opening.group(1)))
            continue
        if line.startswith('\t') or line.startswith('    '):
            continue
        if line.rstrip()== '## Final report':
            candidates.append(i)
    if len(candidates)!=1:
        return {'status':'format_noncompliance','reason':'heading_count=0' if not candidates else 'heading_count>1','report':None}
    start=candidates[0]+1
    end=len(lines)
    for i in range(start,len(lines)):
        if outside[i] and (lines[i].startswith('# ') or lines[i].startswith('## ')):
            end=i
            break
    body=''.join(original_lines[start:end])
    if not body.strip():
        return {'status':'format_noncompliance','reason':'empty_report','report':None}
    return {'status':'ok','reason':None,'report':body,'start':sum(map(len,original_lines[:start])),'end':sum(map(len,original_lines[:end]))}
