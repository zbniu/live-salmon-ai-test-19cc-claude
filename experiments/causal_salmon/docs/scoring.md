# Causal Salmon: Scoring Rules

Operator-only; never provide this document to tested models. Apply the following artifact-based requirements consistently across models.

## Accepted evidence

Check for a nonempty final report, analysis code and saved results. Inspect whether code methods and outputs correspond to the report's adopted value. These submitted artifacts are sufficient grading evidence. Original App tool calls, screenshots, timing traces and independent proof of execution are not PASS prerequisites. Routine rerunning or file-by-file recalculation is not required.

`run_log.txt` can assist checking. Its absence, or missing original App logs, does not by itself reduce scientific grading. The experiment prompt specifies file delivery; delivery omissions and scientific correctness are recorded separately. Missing reports or code/results necessary for verification produce UNKNOWN. Confirmed scientific-condition errors produce FAIL. Complete files do not automatically imply scientific correctness, and missing logs do not establish nonexecution.

## Judge only the A/B/C requirements

| World | PASS conditions |
|---|---|
| A | Report gives an effect judgement and point estimate; submitted method is compatible with random assignment and outputs match the adopted value. A random-group mean difference is accepted. |
| B | Code performs effective baseline-y adjustment; the final answer adopts the adjusted effect and submitted output corresponds. Computing adjustment but finally adopting the raw difference is FAIL. |
| C | Answer recognises that supplied material cannot determine the original participant causal effect, without simultaneously making an unsupported unconditional causal conclusion. A causal point estimate is optional. Merely saying nonsignificant or no effect is FAIL. |

Ordinary `z ~ x+y` is effective adjustment, with participant-target approximation recorded separately. No specific model, method count or method change is required or rewarded. Language, headings, length, structure and method explanations are not graded. Units and population may be inherited from the question.

If multiple estimates leave the adopted answer unclear, use UNKNOWN. For consistent rounding of one estimate, use its highest displayed precision. Clearly descriptive C comparisons and conditional estimates under explicitly unestablished assumptions do not automatically fail. Neither a raw nor a y-only comparison establishes participant-subgroup benefit. Supplementary problems do not automatically fail the entire answer by error count.

## Outputs and summaries

- PASS: submitted material supports every necessary condition for this world.
- FAIL: material confirms at least one necessary scientific-condition error.
- UNKNOWN: necessary report/code/results are missing, the core answer is indeterminate, or its correspondence cannot be checked.

Record case, world, answer, decision, one-sentence reason, evidence location and a link to these scoring rules. Summarise completed cases and PASS/FAIL/UNKNOWN by world. Do not remove missing/faulty cases from planned denominators. No percentage score, report-quality score or ability grade is assigned.

Optional `EEE = |adopted report value − actual sample average effect on participants (SATT)|` uses displayed precision, without an error pass threshold. Lock the adopted value before consulting truth; never select the number closest to truth. Leave EEE blank, never zero, for justified C refusals without a causal point estimate.

This rubric checks observable answers and artifacts against preset requirements. It does not prove internal reasoning or unobserved context isolation. Missing original App records alone do not prevent PASS. The experiment prompt, public data and assignment descriptions determine the task; the scoring rules remain inaccessible to tested models.
