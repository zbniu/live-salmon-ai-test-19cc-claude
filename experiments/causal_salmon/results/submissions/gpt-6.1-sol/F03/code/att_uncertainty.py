"""Target-specific uncertainty for the average effect in the realized attendees.
Under complete random assignment, D - SATT equals the imbalance in Y(0).
Its variance is (1/n1 + 1/n0) * finite-population variance of Y(0).
The observed control variance estimates that variance without constant effects.
This is an approximate repeated-randomization interval for a random target SATT.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import numpy as np
import pandas as pd
from scipy.stats import norm
root=Path(__file__).resolve().parents[2]
out=root/'submission/results'
log=root/'submission/run_log.txt'
with log.open('a') as f:
 f.write('\n'+datetime.now(timezone.utc).isoformat()+' BEGIN code/att_uncertainty.py; supplemental target-specific calculation (does not replace earlier outputs).\n')
df=pd.read_csv(root/'upload/data(20261004-180712).csv')
t=df.loc[df.x==1,'z']; c=df.loc[df.x==0,'z']
difference=float(t.mean()-c.mean())
control_variance=float(c.var(ddof=1))
se=float(np.sqrt(control_variance*(1/len(t)+1/len(c))))
q=float(norm.ppf(.975))
r={'target':'SATT: mean of z_i(1)-z_i(0) over the 600 realized attendees',
   'adopted_estimate_points':difference,'standard_error_points':se,
   'approximate_95_percent_randomization_interval':[difference-q*se,difference+q*se],
   'control_sample_variance':control_variance,
   'variance_formula':'s0^2 * (1/n_attendees + 1/n_nonattendees)',
   'coverage':'Approximate over repeated complete random draws of 600 attendees; target varies with the draw.',
   'identity':'difference_in_means - SATT = mean(z(0) among attendees) - mean(z(0) among nonattendees)',
   'assumptions':'Supplied complete random assignment, consistency, no interference; large-sample normal approximation. No constant-treatment-effect assumption.'}
text=json.dumps(r,indent=2)+'\n'
(out/'att_result.json').write_text(text,encoding='utf-8')
(out/'att_stdout.txt').write_text(text,encoding='utf-8')
print(text)
with log.open('a') as f:
 f.write(datetime.now(timezone.utc).isoformat()+' END code/att_uncertainty.py, exit=0; outputs results/att_result.json and results/att_stdout.txt.\n')
