# Tutoring class and score gain

**Answer:** The supplied material does not establish whether attendance increased the score gain of the 600 attendees, or by how much. Their average causal effect would be their observed gain minus the gain those *same students* would have had without tutoring. That second quantity is unobserved, and the supplied assignment process and variables do not identify it for all attendees.

Using all 2,000 records, attendees gained **14.124 points** on average versus **8.719** for nonattendees, a **5.405-point observed difference**. This is **not** the answer to the causal question: attendees started higher (65.708 versus 56.888 points), and applicant status depended partly on unrecorded circumstances. Neither the application scores nor the applicant list is available.

The admissions rule creates a change in attendance at the lowest attended start score, **55.593**. A local linear, triangular-weight analysis within 4 starting-score points of that value estimates an attendance-rate jump of **0.459** and a gain jump of **−0.010 points**, giving a local ratio of **−0.021 points**. Ratios across bandwidths of 2–8 points range from **−1.256 to 0.814 points**; an illustrative fixed-cutoff bootstrap interval at bandwidth 4 is **−3.321 to 2.514**. Even if the continuity conditions needed for a causal cutoff interpretation held, this would concern students near that cutoff, not the average effect among all attendees. Those conditions are not established by the study description; the bootstrap also treats the sample-derived cutoff as fixed.

As a scale check, an attendee's unobserved end score without tutoring can be anywhere from 0 to 100 under the stated score scale. The resulting **score-scale bounds on the attendees' average effect are −20.168 to 79.832 points** (mean observed end score 79.832 minus an unknown mean counterfactual end score between 0 and 100). These are logical bounds, not a confidence interval or an estimate, and include both harm and benefit. Thus **no definite numerical causal answer for the attendees is supported**.

Analysis code and the actual saved output are included alongside this report.
