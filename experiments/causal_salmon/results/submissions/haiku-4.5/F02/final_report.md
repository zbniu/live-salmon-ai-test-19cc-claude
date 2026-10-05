# Analysis Report: Effect of Arrangement Q on Change z

## Research Question

For the units that received arrangement Q, did receiving arrangement Q increase their change z? If so, by how much?

## Answer

**Yes, receiving arrangement Q increased change z.** 

The estimated effect is **3.71 points** (95% confidence interval: 3.33 to 4.10), based on regression adjustment for baseline measurement. This estimate is statistically significant (t = 18.97, p < 0.001).

## Key Finding

Arrangement Q caused an increase of approximately **3.7 points** in the follow-up change measurement (on a 0-100 scale), after accounting for differences in baseline measurements between treated and control units.

## Analysis Summary

### The Challenge: Selection Bias

This is not a randomized experiment. The study used a selection process based on baseline measurement (y): units with higher baseline values were more likely to be selected for arrangement Q. Specifically:
- Mean baseline in arrangement Q group: 65.71
- Mean baseline in control group: 56.89
- Difference: 8.82 points

Since baseline is strongly correlated with the outcome change (r = 0.54), comparing the two groups without adjustment would produce a biased estimate.

### Naive Comparison (Biased)

A simple comparison of means would show a difference of 5.41 points in favor of arrangement Q. However, this overstates the true effect because the Q group had higher baseline values, and higher baseline is associated with larger changes even in the absence of treatment.

### Adjusted Analysis

Three different methods for controlling the confounding by baseline all converge on similar estimates:

1. **Regression adjustment for baseline** (primary estimate): 3.71 points (95% CI: 3.33-4.10)
2. **Inverse probability weighting**: 4.27 points
3. **Regression with interaction term**: 3.89 points
4. **Stratified analysis**: consistent differences of 3.7-3.9 points across baseline quartiles

### Interpretation

After accounting for differences in baseline measurement between the treated and control groups, arrangement Q increases the change measurement by approximately 3.7 points on the 0-100 scale. This effect is:
- Statistically significant
- Consistent across multiple estimation methods
- Stable across different baseline levels

## Methods Used

- Descriptive statistics of treatment groups
- Linear regression with baseline adjustment
- Inverse probability weighting based on propensity scores
- Stratified analysis by baseline quartiles
- Interaction analysis to test for heterogeneous treatment effects

## Data

- Sample size: 2,000 units
- Treated group (arrangement Q): 600 units
- Control group: 1,400 units
- All data complete with no missing values
