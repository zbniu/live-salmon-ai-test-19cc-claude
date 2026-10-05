# TUTORING STUDY: EFFECT ON SCORE GAINS
## Final Report

---

## RESEARCH QUESTION

For the students who attended the tutoring class, did attending the tutoring class increase their score gain z? If so, by how much?

---

## ANSWER

**YES.** Attending the tutoring class increased student score gains.

### Primary Result

**Students who attended tutoring gained approximately 3.79 additional points compared to students with the same baseline score who did not attend.**

- **Estimated effect:** 3.79 points
- **95% Confidence Interval:** [3.41, 4.17] points  
- **Statistical significance:** p < 0.000001 (highly significant)
- **Methodology:** Multiple regression model controlling for start-of-term test score

---

## ANALYSIS SUMMARY

### Data Overview
- **Total students:** 2,000
- **Tutoring attendance:** 600 students attended (30%)
- **Control group:** 1,400 students did not attend (70%)
- **Outcome variable:** Score gain z (end-of-term score minus start-of-term score)
- **Baseline covariate:** Start-of-term test score (y)

### Key Findings

#### 1. Naive Comparison (Biased)
A simple comparison of mean score gains shows:
- Tutoring group: mean gain = 14.10 points
- Control group: mean gain = 8.64 points
- **Naive difference: 5.46 points**

This estimate is **biased** because students who attended tutoring had substantially higher starting scores (mean 66.07 vs. 57.35), and score gains are correlated with baseline scores. This creates a selection confound.

#### 2. Selection Mechanism
Students were not randomly assigned to tutoring. Instead:
- Tutoring was allocated based on start-of-term test scores
- Students with higher baseline scores were more likely to attend
- There is clear overlap in baseline scores between groups, but with a strong selection pattern
- Students scoring ≤52 had zero probability of attending
- Treatment probability increases monotonically with baseline score

#### 3. Adjusted Estimate (Primary Result)
A multiple regression model controlling for baseline score provides the unbiased estimate:

**Model: z ~ x + y**
- Treatment effect (x coefficient): **3.7874 points**
- Baseline score effect (y coefficient): 0.1923 (students gain more when starting from higher baseline)
- Standard error: 0.1937
- 95% CI: [3.4077, 4.1670]
- p-value: < 0.000001

This estimates the causal effect: comparing two students with identical baseline scores, the one who attended tutoring gained approximately 3.79 more points.

#### 4. Robustness Check: Local Analysis
A local linear regression near the selection boundary (between ~64 and ~68 on the baseline score scale) confirms the main result:
- Estimates across different bandwidth choices: 3.85 to 4.13 points
- All estimates cluster closely around 3.9 points
- Confirms the main estimate is robust to the specific econometric approach

---

## INTERPRETATION

The estimated treatment effect of **3.79 points (95% CI: 3.41 to 4.17)** answers the research question:

**Among students with the same baseline test score, those who attended the tutoring class experienced gains that were approximately 3.8 points higher than students who did not attend.**

This effect is:
- **Substantial:** About 37% of the control group's mean gain
- **Precisely estimated:** Narrow 95% confidence interval  
- **Highly significant:** p-value < 0.000001
- **Robust:** Confirmed by multiple analytical approaches

---

## METHODOLOGICAL NOTES

### Why the Main Estimate is Preferred Over the Naive Estimate

The naive estimate (5.46 points) would be correct only if assignment to tutoring were random. However:
- Selection occurred: higher-scoring students were more likely to attend
- This creates confounding bias: some of the observed difference reflects pre-existing differences, not the effect of tutoring
- The regression approach (controlling for baseline score) removes this bias
- The local analysis confirms the adjusted estimate

### Data Quality
- All 2,000 observations included with no missing values
- No data dropped or excluded
- Analysis uses complete data as supplied

### Limitations and Assumptions
1. **Assumption:** The model correctly captures the selection mechanism through baseline score
2. **Assumption:** The relationship between baseline score and outcome is adequately modeled as linear (with possible interaction)
3. **Scope:** This is an observational study answering a causal question based on adjustment for baseline score; evidence for causality rests on the validity of this adjustment

---

## CONCLUSION

The tutoring class was effective. Students who attended gained approximately **3.8 additional points** compared to similar non-attending students. This effect is statistically significant, practically meaningful, and robust across analytical approaches.
