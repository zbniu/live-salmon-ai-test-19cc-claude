"""ATT by control outcome standardization; uncertainty and specification checks.

No assumption of a constant effect is made. A smooth untreated outcome mean
is estimated from controls and averaged over the actual attendee covariates.
HC3 plus treated empirical variance is an approximate independent-student
inferential calculation, not a randomization test of the quota assignment.
"""
from pathlib import Path
import json, csv
import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import SplineTransformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'submission/results'
d=np.genfromtxt(ROOT/'upload/data(20261004-180753).csv',delimiter=',',names=True)
t=d['x']==1; c=d['x']==0
y0,z0=d['y'][c],d['z'][c]; y1,z1=d['y'][t],d['z'][t]
n0,n1=len(z0),len(z1)

def ols_hc3(B,z):
 bread=np.linalg.pinv(B.T@B)
 beta=np.linalg.lstsq(B,z,rcond=None)[0]
 residual=z-B@beta
 leverage=np.einsum('ij,jk,ik->i',B,bread,B)
 adjusted=residual/(1-leverage)
 covariance=bread @ ((B*adjusted[:,None]).T@(B*adjusted[:,None])) @ bread
 return beta,covariance,residual,leverage

def standardized(B0,B1,method):
 beta,cov,residual,h=ols_hc3(B0,z0)
 prediction=B1@beta
 differences=z1-prediction
 bbar=B1.mean(axis=0)
 variance_treated=np.var(differences,ddof=1)/n1
 variance_control=float(bbar@cov@bbar)
 estimate=float(differences.mean()); se=float(np.sqrt(variance_treated+variance_control))
 return {'method':method,'att':estimate,'se':se,
         'ci95':[estimate-norm.ppf(.975)*se,estimate+norm.ppf(.975)*se],
         'normal_approximation_p_value':float(2*norm.sf(abs(estimate/se))),
         'estimated_untreated_gain_for_attendees':float(prediction.mean()),
         'control_model_rank':int(np.linalg.matrix_rank(B0)),
         'max_control_leverage':float(h.max()),
         'variance_treated_component':float(variance_treated),
         'variance_control_component':variance_control}, beta, prediction

# Primary: cubic B-splines, 5 quantile knot locations on all 1400 controls.
sp=SplineTransformer(n_knots=5,degree=3,knots='quantile',include_bias=True)
B0=sp.fit_transform(y0[:,None]); B1=sp.transform(y1[:,None])
primary,beta0,prediction=standardized(B0,B1,'Cubic spline, 5 control quantile knot locations')
rows=[primary]
for degree in [1,2,3]:
 Bc=np.column_stack([((y0-60)/20)**j for j in range(degree+1)])
 Bt=np.column_stack([((y1-60)/20)**j for j in range(degree+1)])
 rows.append(standardized(Bc,Bt,f'Control polynomial degree {degree}')[0])
for knots in [4,6,8,10,15]:
 spline=SplineTransformer(n_knots=knots,degree=3,knots='quantile',include_bias=True)
 Bc=spline.fit_transform(y0[:,None]); Bt=spline.transform(y1[:,None])
 rows.append(standardized(Bc,Bt,f'Cubic spline, {knots} control quantile knot locations')[0])

# Direct stratification checks: no outcome regression, weights target attendees.
bin_details=[]
for width in [1,2,5]:
 bin0=np.floor(y0/width).astype(int); bin1=np.floor(y1/width).astype(int)
 estimate=0.; variance=0.
 for b in np.unique(bin1):
  a=z1[bin1==b]; v=z0[bin0==b]
  assert len(v)>1 and len(a)>1
  w=len(a)/n1
  estimate+=w*(a.mean()-v.mean())
  variance+=w*w*(np.var(a,ddof=1)/len(a)+np.var(v,ddof=1)/len(v))
  bin_details.append({'width':width,'lower':float(b*width),'upper':float((b+1)*width),
                      'attendees':len(a),'nonattendees':len(v),'attendee_weight':w,
                      'mean_y_attendees':float(y1[bin1==b].mean()),
                      'mean_y_nonattendees':float(y0[bin0==b].mean()),
                      'mean_gain_attendees':float(a.mean()),'mean_gain_nonattendees':float(v.mean())})
 se=float(np.sqrt(variance))
 rows.append({'method':f'Attendee-weighted {width}-point starting-score strata',
              'att':float(estimate),'se':se,
              'ci95':[float(estimate-1.96*se),float(estimate+1.96*se)]})

# Common-slope regression is shown as a comparator, not adopted as ATT.
v=(d['y']-y1.mean())/20
full=np.column_stack([np.ones(len(d)),d['x'],v])
coef,cov,_,_=ols_hc3(full,d['z'])
common={'method':'OLS z ~ 1 + x + centered_y (constant-effect model)',
        'x_coefficient':float(coef[1]),'se':float(np.sqrt(cov[1,1]))}
# Interaction model shows whether effect constancy should be assumed.
full_interaction=np.column_stack([np.ones(len(d)),d['x'],v,d['x']*v])
coef,cov,_,_=ols_hc3(full_interaction,d['z'])
interaction={'att_at_attendee_mean_y':float(coef[1]),
             'effect_change_per_y_point':float(coef[3]/20),
             'effect_change_se':float(np.sqrt(cov[3,3])/20),
             'interaction_p_value':float(2*norm.sf(abs(coef[3]/np.sqrt(cov[3,3]))))}

# Stratified pairs bootstrap: resample all attendee and control rows independently
# within their groups (600 and 1400 each replicate); refit knot locations and curve.
# This is an approximate sampling check, not a recreation of admissions.
rng=np.random.default_rng(20261004)
R=2000; draws=np.empty(R)
for r in range(R):
 i0=rng.integers(0,n0,n0); i1=rng.integers(0,n1,n1)
 spline=SplineTransformer(n_knots=5,degree=3,knots='quantile',include_bias=True)
 C=spline.fit_transform(y0[i0,None]); T=spline.transform(y1[i1,None])
 b=np.linalg.lstsq(C,z0[i0],rcond=None)[0]
 draws[r]=np.mean(z1[i1]-T@b)
np.savetxt(OUT/'bootstrap_att.csv',np.column_stack([np.arange(1,R+1),draws]),delimiter=',',header='replicate,att',comments='',fmt=['%d','%.17g'])
bootstrap={'replicates':R,'seed':20261004,'se':float(draws.std(ddof=1)),
           'percentile_ci95':np.quantile(draws,[.025,.975]).tolist()}

# Save the predictions and the exact spline parameters for traceability.
student_rows=np.flatnonzero(t)+1
np.savetxt(OUT/'attendee_counterfactual_predictions.csv',
           np.column_stack([student_rows,y1,z1,prediction,z1-prediction]),delimiter=',',
           header='data_row,y,observed_gain,estimated_untreated_mean_gain,observed_minus_predicted',comments='',
           fmt=['%d','%.17g','%.17g','%.17g','%.17g'])
with (OUT/'strata_details.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(bin_details[0])); writer.writeheader(); writer.writerows(bin_details)
with (OUT/'sensitivity_estimates.csv').open('w',newline='') as f:
 writer=csv.writer(f); writer.writerow(['method','att','se','ci95_lower','ci95_upper'])
 for row in rows: writer.writerow([row['method'],row['att'],row['se'],*row['ci95']])
result={'n_total':len(d),'n_attended':n1,'n_nonattended':n0,
        'estimand':'Mean effect of attendance on gain among attendees (ATT)',
        'primary':primary,'bootstrap_check':bootstrap,'sensitivity':rows,
        'common_slope_comparator':common,'linear_effect_heterogeneity_check':interaction,
        'spline_knots_including_boundary_extensions':sp.bsplines_[0].t.tolist(),
        'spline_coefficients':beta0.tolist(),
        'observed_attendee_mean_gain':float(z1.mean()),
        'raw_mean_difference':float(z1.mean()-z0.mean()),
        'treated_y_range':[float(y1.min()),float(y1.max())],
        'control_y_range':[float(y0.min()),float(y0.max())],
        'control_count_at_or_above_lowest_attendee_y':int(np.sum(y0>=y1.min())),
        'uncertainty_qualification':'Approximate independent-student inference with a fitted smooth outcome mean; not exact quota-design randomization inference.'}
(OUT/'att_results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

grid=np.linspace(y0.min(),y0.max(),400)
beta1,_,_,_=ols_hc3(B1,z1)
fig,ax=plt.subplots(figsize=(8,4.8))
ax.plot(grid,sp.transform(grid[:,None])@beta0,label='Estimated gain without tutoring',color='#496a89')
inside=(grid>=y1.min()) & (grid<=y1.max())
ax.plot(grid[inside],sp.transform(grid[inside,None])@beta1,label='Estimated gain with tutoring',color='#d17d2f')
ax.axvspan(y1.min(),y1.max(),color='grey',alpha=.07,label='Attendee starting-score range')
ax.set(xlabel='Start-of-term score y',ylabel='Estimated mean gain (points)',title='Starting-score adjusted outcome curves')
ax.legend(); ax.grid(alpha=.15); fig.tight_layout()
fig.savefig(OUT/'adjusted_outcome_curves.png',dpi=160); plt.close(fig)
print('Outputs: att_results.json, bootstrap_att.csv, attendee_counterfactual_predictions.csv, strata_details.csv, sensitivity_estimates.csv, adjusted_outcome_curves.png.')
