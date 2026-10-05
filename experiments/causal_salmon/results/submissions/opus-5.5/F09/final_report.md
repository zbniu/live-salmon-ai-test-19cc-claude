# Final report: did arrangement Q increase change `z` for the units that received it?

## Answer

**For the treated units as a whole (all 600), the supplied material does not support a definite answer.** The only effect the design identifies is the effect for treated units whose baseline is at the acceptance cutoff (y ≈ 57.0). For those units, the estimate is **−0.53 points** (fuzzy regression-discontinuity, local linear, triangular kernel, MSE-optimal bandwidth 3.8; robust 95% CI **−4.7 to +3.7**; p = 0.81). This is the numerical result I adopt. It gives **no evidence that Q increased `z`** at the cutoff, although the interval is too wide to rule out an increase of up to about 3.7 points or a decrease of similar size.

The covariate-adjusted comparison of treated and untreated units (about +4 points) should **not** be read as the effect of Q, because treatment depended on unrecorded circumstances, and the data show the pattern that this selection would produce (see below).

## Why this is the identified quantity

From the study description, a unit received Q only if (a) it was a candidate, which depended on baseline `y`, on unrecorded circumstances, and on noise, and (b) its baseline was at or above the lowest baseline accepted among candidates. In the data, the lowest baseline among treated units is c = 56.995. All 793 units below c are untreated. Above c, 600 units are treated and 607 are not. Above c, treatment is therefore equivalent to candidacy, which depends partly on unrecorded factors that may also affect `z`. This means that comparing treated and untreated units at the same baseline is confounded.

At c, however, the probability of treatment jumps from 0 to about 0.40 (first stage 0.404, SE 0.062). This jump is driven only by the acceptance rule. Candidacy and the unrecorded factors vary smoothly with `y`, and `y` was measured before selection and could not be manipulated. The fuzzy RD ratio (jump in E[z] / jump in P(x)) therefore identifies the effect of Q for candidates at c. Because nobody below c can be treated, those candidates are exactly the treated units at the cutoff. The result is an effect on the treated, but only locally at baseline ≈ 57. Treated units range up to y = 75, and nothing in the material identifies their effect without untestable assumptions about the unrecorded selection factor.

## Robustness of the cutoff estimate

| specification | estimate | uncertainty |
|---|---|---|
| p=1, triangular, h=3.8 (adopted) | −0.53 | robust CI [−4.71, 3.70] |
| p=2, triangular, h=5.8 | −0.22 | robust CI [−4.48, 4.59] |
| p=1, uniform, h=3.2 | −0.26 | robust CI [−4.03, 4.26] |
| p=1, Epanechnikov, h=3.5 | −0.56 | robust CI [−4.93, 3.63] |
| manual uniform, h = 3,4,5,6,8,10,12 | −0.20, −0.42, 0.14, −1.58, −0.03, 0.20, 1.07 | bootstrap SE 1.9 → 0.8 |

All specifications give estimates near zero. Of five placebo cutoffs in regions with no change in treatment rule, one (y = 66) showed a nominally significant jump (p = 0.012). The others did not. This is roughly what chance would produce, but it shows that local estimates in these data are noisy.

## Evidence of selection on unrecorded factors

* The naive difference in mean `z` between treated and untreated units is +5.46. Most of this reflects baseline, because `z` rises about 0.25 points per baseline point.
* Regressing `z` on x and y gives +3.79 (SE 0.20) overall and +4.01 among units with y ≥ c. At the cutoff, the treated–untreated gap among units with y ≥ c is +3.63.
* At c, the untreated units just above (non-candidates only) have `z` about 1.5 points *lower* than the mixed group just below (robust CI −3.2 to 0.3). Treated units just above have `z` about 1.6 points *higher*. If Q had no effect and candidates had a higher untreated change than non-candidates, this split is what one would expect. It is consistent with the ~4-point adjusted gap being largely selection rather than an effect of Q. The size of these individual jumps is imprecise.

## Conclusion

The data do not show that Q increased `z` for treated units at the acceptance cutoff. The estimate there is −0.5 points (95% CI −4.7 to +3.7). For all treated units, the average effect is not identified by the supplied material. The apparent ~4–5-point advantage of treated units is confounded by selection on unrecorded circumstances, so it cannot be taken as the effect.

Code: `code/01_explore.py`, `code/02_rd_analysis.py`, `code/03_descriptive_and_selection.py`; outputs in `results/`.
