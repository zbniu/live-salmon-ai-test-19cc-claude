# Final report: effect of arrangement Q on change `z` among units that received it

## Answer

**The data do not support a definite answer for the treated units as a whole.** The only effect the design identifies is for treated units whose baseline `y` is at the acceptance threshold (c ≈ 55.59). For those units there is **no evidence that Q increased `z`**: adopted estimate **−0.83 points** (fuzzy RD, local linear, MSE-optimal bandwidth 2.85; robust bias-corrected 95% CI **−5.65 to +2.96**). Estimates across bandwidths and polynomial orders range from about −1.6 to +1.0, and none is distinguishable from zero. Effects larger than roughly +3 points at the threshold are not supported by the data.

For treated units with higher baseline values (most of the 600), the effect is **not identified**. Simple treated-vs-untreated comparisons (raw difference 5.41; regression-adjusted about 3.7–4.0 points) are **not** estimates of the effect, because they are confounded by the unrecorded circumstances that entered selection.

## Why this approach

Section 3 implies the following structure. Candidates were accepted in descending order of `y`, so there is a threshold c equal to the lowest `y` among treated units (55.593). No unit below c was treated. Above c, a unit was treated exactly when it was a candidate. Candidacy depended on `y`, on unrecorded circumstances, and on random noise. Consistent with this, the data show 0% treated below c and about 46% just above it (first stage 0.457, SE 0.077). Above c, untreated units are non-candidates.

Above c, treatment therefore depends on unrecorded circumstances that may also affect `z`. Regression on `y` cannot remove that confounding, and the random component of the selection value is not available to use as an instrument. The discontinuity at c remains valid. Units just below and just above c have the same mix of candidates and non-candidates, and only the candidates above c receive Q. A fuzzy RD at c therefore identifies the effect for candidates at y = c. Because no one below c can be treated (one-sided noncompliance), those candidates are exactly the treated units at the threshold. The baseline was measured before assignment, so its value cannot have been manipulated. A density test was attempted, but its numerical output was not printed (see run log).

## Key results (code in `code/`, outputs in `results/`)

| Estimate | Value | 95% CI |
|---|---|---|
| **Fuzzy RD, p=1, MSE-opt h=2.85 (adopted)** | **−0.83** | robust [−5.65, 2.96] |
| Fuzzy RD, p=2, MSE-opt h=4.01 | −1.57 | robust [−7.46, 3.63] |
| Fuzzy RD, p=1, triangular, h = 2 … 10.5 | −1.26 … +0.96 | all include 0 |
| Reduced-form jump in z at c (sharp) | −0.38 | robust [−2.50, 1.29] |
| *Confounded:* OLS z ~ x + y, units with y ≥ c | 3.83 (SE 0.20) | not causal |
| *Confounded:* raw difference in means | 5.41 | not causal |

Diagnostics support the interpretation:

- The mean of `z` across all units is continuous at c, so the fact that 46% of units become treated there produces no visible jump.
- Among untreated units only, `z` drops by about 2.1 points at c (robust CI −4.4 to −0.1). Just above c, untreated units are non-candidates, so this drop means non-candidates have lower `z` than the pooled population. That is direct evidence of selection on outcome-relevant unrecorded circumstances.
- Decomposing the naive treated-untreated gap at c (about 3.9 points) gives an implied selection bias of about 3–4.7 points and an implied effect of about −0.7 to +0.9, depending on bandwidth.
- Placebo cutoffs (49, 51, 53 below c; 60, 63, 66, 69 above c) show no jumps.

## Limitations

The estimate is local to treated units with baseline near 55.6 and is imprecise: the CI is about 8 points wide. Above c, the treated-untreated gap in `z` is roughly constant (about 3.5–4 points) across `y`. At c, that gap is almost entirely selection. This pattern fits a near-zero effect throughout, but only under the additional, untestable assumption that selection bias does not vary with `y`. That assumption is not adopted. No definite number is given for the average effect over all 600 treated units.
