"""Analyze the complete attached randomized tutoring study; no external data."""
from pathlib import Path
import hashlib, json, platform
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels.api as sm
import statsmodels

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'upload/data(20261004-180712).csv'
DESC = ROOT / 'upload/STUDY_DESCRIPTION(20261004-180712).md'
OUT = ROOT / 'submission/results'
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(DATA)
assert list(df.columns) == ['x','y','z']
assert len(df) == 2000 and not df.isna().any().any()
assert np.isfinite(df.to_numpy()).all()
assert set(df.x.unique()) == {0,1}
assert (df.x == 1).sum() == 600
assert df.y.between(0,100).all()
assert (df.y+df.z).between(0,100).all()

summary = df.groupby('x').agg(n=('z','size'), y_mean=('y','mean'), y_sd=('y','std'),
                            z_mean=('z','mean'), z_sd=('z','std'), z_min=('z','min'), z_max=('z','max'))
summary.to_csv(OUT/'group_summary.csv')
t = df.loc[df.x==1,'z'].to_numpy()
c = df.loc[df.x==0,'z'].to_numpy()
est = t.mean()-c.mean()
v1 = t.var(ddof=1)/len(t)
v0 = c.var(ddof=1)/len(c)
se = np.sqrt(v1+v0)
dof = (v1+v0)**2/(v1*v1/(len(t)-1)+v0*v0/(len(c)-1))
crit = stats.t.ppf(.975,dof)
primary = {'estimate':est, 'se':se, 'df':dof, 'ci95':[est-crit*se,est+crit*se],
           'p_two_sided':2*stats.t.sf(abs(est/se),dof),
           'method':'Unadjusted difference in mean gains, Welch t interval/test; design-based Neyman SE'}

# Adjust only for pre-assignment y. Fully interact x with centered polynomial
# terms, so group slopes may differ. Degrees 1 and 2 are sensitivity checks,
# rather than selecting whichever result has the smallest p value.
sens = []
for degree in [1,2]:
    yc = (df.y-df.y.mean())/df.y.std(ddof=0)
    D = pd.DataFrame({'intercept':np.ones(len(df)),'x':df.x})
    for k in range(1,degree+1):
        b = yc**k
        b -= b.mean()
        D[f'y{k}'] = b
        D[f'x_y{k}'] = df.x*b
    fit = sm.OLS(df.z,D).fit(cov_type='HC2')
    contrasts = {}
    for target, mask in [('all_students',np.ones(len(df),dtype=bool)),('attendees',df.x.to_numpy()==1)]:
        contrast = np.zeros(D.shape[1]); contrast[D.columns.get_loc('x')] = 1
        for k in range(1,degree+1):
            contrast[D.columns.get_loc(f'x_y{k}')] = D.loc[mask,f'y{k}'].mean()
        value = float(contrast@fit.params)
        stderr = float(np.sqrt(contrast@fit.cov_params()@contrast))
        contrasts[target] = {'estimate':value,'se_hc2':stderr,
                            'ci95_normal':[value-1.959963984540054*stderr,value+1.959963984540054*stderr]}
    info = {'degree':degree,'contrasts':contrasts,'r_squared':float(fit.rsquared),
            'note':'Attendee-standardized contrast uses observed attendee y distribution; conditional regression interval.'}
    sens.append(info)
    (OUT/f'adjusted_degree{degree}_model.txt').write_text(fit.summary().as_text()+'\n',encoding='utf-8')

# Descriptive baseline quintiles, not separate confirmatory hypothesis tests.
df['baseline_quintile'] = pd.qcut(df.y,5,labels=False)+1
bins = df.groupby(['baseline_quintile','x'],observed=True).agg(n=('z','size'),y_mean=('y','mean'),z_mean=('z','mean'),z_sd=('z','std'))
bins.to_csv(OUT/'baseline_quintiles.csv')

result = {'validation':{'rows':len(df),'treated':len(t),'control':len(c),'missing_values':int(df[['x','y','z']].isna().sum().sum()),
                         'end_score_min':float((df.y+df.z).min()),'end_score_max':float((df.y+df.z).max())},
          'primary':primary,'sensitivity':sens,
          'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'statsmodels':statsmodels.__version__},
          'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA,DESC]}}
(OUT/'analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('ALL 2000 ROWS ANALYZED; validation passed')
print(summary.to_string())
print('\nPRIMARY RESULT\n'+json.dumps(primary,indent=2))
print('\nADJUSTMENT SENSITIVITY\n'+json.dumps(sens,indent=2))
print('\nDESCRIPTIVE BASELINE QUINTILES\n'+bins.to_string())
