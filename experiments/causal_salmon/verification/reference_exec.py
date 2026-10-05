"""Runtime-staged executable. No backend metadata, generator or hidden input."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import sys

# Arguments identify only safe runtime and randomly staged public files, no world or seed.
root = Path(sys.argv[1]).resolve()
runtime = Path(sys.argv[2]).resolve()
site = Path(sys.argv[3]).resolve()
probe = Path(sys.argv[4]).resolve()
allowed_roots = [Path('/System'), Path('/usr'), Path('/Library'), Path(sys.base_prefix), site, runtime]
allowed_files = {root/'data.csv', root/'STUDY_DESCRIPTION.md'}
audit = []

def audit_hook(event, arguments):
    if event == 'open' and isinstance(arguments[0], (str,bytes,os.PathLike)):
        p = Path(os.fsdecode(arguments[0])).resolve()
        allowed = p in allowed_files or any(p == r or r in p.parents for r in allowed_roots) or p == Path('/dev/null')
        audit.append(dict(event='open', path=str(p), permitted=allowed))
        if not allowed:
            raise PermissionError('Public reference read whitelist')
    if event.startswith('socket.') and event not in ('socket.__new__',):
        audit.append(dict(event=event, permitted=False))
        raise PermissionError('Public reference network disabled')

sys.addaudithook(audit_hook)
sys.path[:0] = [str(runtime), str(site)]
import numpy as np
from statistics_public import difference, standardized

public = (root/'data.csv').read_bytes()
description = (root/'STUDY_DESCRIPTION.md').read_bytes()
rows = list(csv.reader(io.StringIO(public.decode())))
if rows[0] != ['x','y','z']:
    raise ValueError('Invalid CSV header')
arr = np.array([[float(v) for v in row] for row in rows[1:]], dtype=np.float64)
x,y,z = arr[:,0].astype(np.int64),arr[:,1],arr[:,2]
paragraph = description.decode().split('## 3.',1)[1].split('## 4.',1)[0]
N = float(np.mean(z[x==1])-np.mean(z[x==0]))
if 'by a random draw' in paragraph and 'The draw used no information' in paragraph:
    method = 'random_difference'
    estimate = difference(x,z)
    basis = 'The equal-chance random draw used no information about the units, so the groups are comparable.'
elif 'made of two parts:' in paragraph and 'no other characteristic' in paragraph and 'descending order' in paragraph:
    method = 'standardized_ols'
    estimate,_ = standardized(x,y,z)
    basis = 'The selection value used only baseline measurement and unrelated random numbers, and acceptance used only baseline measurement. Units with the same baseline measurement are therefore comparable.'
elif 'made of three parts:' in paragraph and 'were not recorded' in paragraph:
    method = 'insufficient_information'
    estimate,_ = standardized(x,y,z)
    basis = 'Selection also used circumstances that were not recorded. The supplied material does not establish that those circumstances are unrelated to change, so it cannot determine the effect.'
else:
    raise ValueError('Unknown public assignment rule')
if estimate['status'] != 'ok':
    report = '## Final report\n'+basis+' The registered numerical analysis was unavailable: '+str(estimate['reason'])+'.\n'
elif method == 'insufficient_information':
    report = '## Final report\n'+basis+f" The observed unadjusted difference is {N:.17g} points. A descriptive baseline-adjusted interaction regression gives {estimate['E']:.17g} points (SE {estimate['se']:.17g}; nominal 95% interval {estimate['ci'][0]:.17g} to {estimate['ci'][1]:.17g}). These values are descriptive only and are not adopted as causal effect estimates. The question concerns units that received the arrangement. Missing selection circumstances are the principal limitation.\n"
else:
    analysis = 'difference in group means' if method=='random_difference' else 'four-column interaction OLS regression, standardized at the treated mean baseline measurement, with HC3 uncertainty'
    report = '## Final report\n'+basis+f" We ran {analysis}. We adopt its estimate: receiving the arrangement increased change by {estimate['E']:.17g} points for the units that received it (SE {estimate['se']:.17g}; nominal 95% interval {estimate['ci'][0]:.17g} to {estimate['ci'][1]:.17g}). The unadjusted difference, {N:.17g} points, is descriptive. Sampling uncertainty and the supplied study's scope limit the result; it is not generalized to all units.\n"
probes = {}
try:
    probe.read_bytes()
    probes['hidden_read_blocked'] = False
except (PermissionError,OSError):
    probes['hidden_read_blocked'] = True
try:
    os.listdir(probe.parent)
    probes['parent_listing_blocked'] = False
except (PermissionError,OSError):
    probes['parent_listing_blocked'] = True
try:
    socket.create_connection(('127.0.0.1',9),timeout=.1)
    probes['network_blocked'] = False
except (PermissionError,OSError):
    probes['network_blocked'] = True
print(json.dumps(dict(input_hashes={'data.csv':hashlib.sha256(public).hexdigest(),'STUDY_DESCRIPTION.md':hashlib.sha256(description).hexdigest()},method=method, report=report, numeric=dict(N=N,E=estimate['E'],se=estimate['se'],ci=estimate['ci']), analysis_status=estimate['status'], probes=probes, access_log=audit),allow_nan=False))
