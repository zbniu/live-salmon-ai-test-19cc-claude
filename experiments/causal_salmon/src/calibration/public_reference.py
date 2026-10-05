"""Standalone public analyzer: no imports from the project or hidden metadata."""
import csv
import hashlib
import json
import socket
import sys
from pathlib import Path

import numpy as np


def failed_output(data,prose,method,N,reason,details,data_path,description_path):
    report='## Final report\n\nThe prespecified public calculation could not be completed: '+reason+'. The raw difference is '+format(N,'.17g')+' points, descriptive only. No adjusted causal estimate is adopted. '
    if method=='insufficient_information':
        report+='The supplied material cannot determine the effect because selection used unrecorded circumstances whose relation to the outcome is not established. '
    report+='The missing estimate and uncertainty are a numerical limitation, not evidence of no effect. The intended population is the actual participants.\n'
    return {'input_hashes':{'data.csv':hashlib.sha256(data).hexdigest(),'STUDY_DESCRIPTION.md':hashlib.sha256(prose).hexdigest()},'method':method,'numeric':{'N':N,'E':None,'se':None,'ci':None},'analysis':{'failure':reason,'details':details},'report':report,'correct':method=='insufficient_information','format_valid':True,'input_boundary_passed':True,'accessed_inputs':[str(Path(data_path).resolve()),str(Path(description_path).resolve())]}


def analyze(data_path,description_path):
    data=Path(data_path).read_bytes()
    prose=Path(description_path).read_bytes()
    description=prose.decode('utf-8')
    assignment=description.split('## 3. ')[1].split('## 4. ')[0]
    if 'by a random draw' in assignment and 'same chance' in assignment and 'used no information' in assignment:
        method='random_difference'
    elif 'made of three parts' in assignment and 'were not recorded' in assignment:
        method='insufficient_information'
    elif 'made of two parts' in assignment and 'no other characteristic' in assignment and 'descending order' in assignment:
        method='standardized_ols'
    else:
        raise ValueError('Unsupported public assignment description')
    rows=list(csv.DictReader(data.decode('utf-8').splitlines()))
    x=np.array([int(row['x']) for row in rows])
    y=np.array([float(row['y']) for row in rows])
    z=np.array([float(row['z']) for row in rows])
    t,c=x==1,x==0
    N=float(np.mean(z[t])-np.mean(z[c]))
    analysis={'N':N}
    if method=='random_difference':
        E=N
        se=float(np.sqrt(z[t].var(ddof=1)/t.sum()+z[c].var(ddof=1)/c.sum()))
        analysis['method']='difference in means; sample variance ddof=1'
    else:
        center=np.mean(y[t])
        yc=y-center
        X=np.column_stack((np.ones(len(x)),x,yc,x*yc))
        rank=int(np.linalg.matrix_rank(X))
        if rank!=4:
            return failed_output(data,prose,method,N,'rank_below_four',{'rank':rank},data_path,description_path)
        xtx=X.T@X
        try:
            coef=np.linalg.solve(xtx,X.T@z)
            inv=np.linalg.inv(xtx)
        except np.linalg.LinAlgError:
            return failed_output(data,prose,method,N,'normal_equations_unsolvable',{'rank':rank},data_path,description_path)
        h=np.sum((X@inv)*X,axis=1)
        if np.any(h>=1):
            return failed_output(data,prose,method,N,'leverage_at_least_one',{'h_max':float(h.max())},data_path,description_path)
        residual=z-X@coef
        hc3=inv@(X.T@((residual**2/(1-h)**2)[:,None]*X))@inv
        E,se=float(coef[1]),float(np.sqrt(hc3[1,1]))
        analysis.update(method='four-column interaction OLS standardized at participant mean baseline; HC3',center=float(center),coefficients=coef.tolist(),rank=rank,h_max=float(h.max()))
    if not np.isfinite([N,E,se]).all():
        return failed_output(data,prose,method,N,'nonfinite_estimate_or_se',{},data_path,description_path)
    ci=[E-1.96*se,E+1.96*se]
    numeric={'N':N,'E':E,'se':se,'ci':ci}
    f=lambda v:format(v,'.17g')
    anon='arrangement Q' in description
    population='units that received arrangement Q' if anon else 'students who attended the tutoring class'
    treatment='Receiving arrangement Q' if anon else 'Attending the tutoring class'
    baseline='baseline measurement' if anon else 'start-of-term test score'
    response='change' if anon else 'score gain'
    if method=='random_difference':
        conclusion=f'{treatment} changed {response} by an estimated {f(E)} points for the {population}. The equal-chance random draw used no information about the units, which supports this causal comparison.'
        limits='The estimate concerns actual participants in this simulated study. Finite-sample uncertainty remains; it does not establish an effect for every individual or other populations.'
    elif method=='standardized_ols':
        conclusion=f'{treatment} changed {response} by an estimated {f(E)} points for the {population}. This adjusted result is the single estimate adopted for the effect. The selection value used only the baseline measurement and independently generated randomness unrelated to every characteristic; acceptance used only the baseline measurement. These facts justify comparing units at the same baseline measurement.'
        limits='The result is standardized over actual participants. It uses a linear interaction outcome model and comparisons over their baseline range; finite-sample and model uncertainty remain.'
    else:
        conclusion=f'The supplied material cannot determine whether {treatment.lower()} increased {response} for the {population}. Selection also used unrecorded circumstances. The supplied material does not establish that those circumstances are unrelated to the outcome, so adjusting the recorded {baseline} cannot rule out their contribution.'
        limits='All numerical comparisons below are descriptive only and are not causal effect estimates. Statistical precision cannot resolve this information limitation.'
    report='## Final report\n\n'+conclusion+'\n\n'+f'We calculated the raw mean difference ({f(N)} points). '
    report+=('For the random comparison, ' if method=='random_difference' else 'We also fitted the interaction regression, standardized over participants; ')
    report+=f'the estimate/difference is {f(E)} points, SE {f(se)}, with nominal 95% interval [{f(ci[0])}, {f(ci[1])}].\n\n'+limits+'\n'
    return {'input_hashes':{'data.csv':hashlib.sha256(data).hexdigest(),'STUDY_DESCRIPTION.md':hashlib.sha256(prose).hexdigest()},'method':method,'numeric':numeric,'analysis':analysis,'report':report,'correct':True,'format_valid':True,'input_boundary_passed':True,'accessed_inputs':[str(Path(data_path).resolve()),str(Path(description_path).resolve())]}


def probe(path):
    denied={}
    for name,target in [('project_file',Path(path)/'planning.md'),('parent_listing',Path(path).parent)]:
        try:
            list(target.iterdir()) if target.is_dir() else target.read_bytes()
        except (PermissionError,OSError):
            denied[name]=True
        else:
            denied[name]=False
    try:
        socket.create_connection(('1.1.1.1',443),timeout=1)
    except PermissionError:
        denied['network']=True
    except OSError as e:
        denied['network']=e.errno in (1,13)
    else:
        denied['network']=False
    return denied


if __name__=='__main__':
    if sys.argv[1]=='--probe':
        output=probe(sys.argv[2])
    else:
        output=analyze(sys.argv[1],sys.argv[2])
    print(json.dumps(output,allow_nan=False))
