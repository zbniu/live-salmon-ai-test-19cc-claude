# Manual App experiment procedure

1. Start a fresh independent session for each case. Disable controllable memory, history references and research-specific custom instructions. Do not attach this repository, local folders, a library, browsing or connectors.
2. Select the case in [case_index.csv](../configs/case_index.csv). Upload only its `STUDY_DESCRIPTION.md` and `data.csv` from `materials/uploads/<case>/`. Send the complete [App prompt](../materials/app_prompt.txt). Never supply grading criteria, hidden truth, other reports or case-index world labels.
3. Record the model label, visible reasoning setting, date and actual material case. Keep settings and stopping rules consistent. Do not steer methods or repeat an answer to select a better result. Record limits, faults or model fallback.
4. Download `final_report.md` and `submission.zip`; preserve original files under the model and verified material case. Accept report, code and saved outputs; retain errors and available logs. A cloud session cannot directly save to a local computer path; download and classify its attachments locally.
5. Apply the [core scoring rules](scoring.md) from submitted artifacts. Missing original App tool logs are not by themselves scientific failure. Delivery requirements and scientific correctness are recorded separately.

D01–D06 are retained development materials, not a completed six-case pilot matrix. Prompt-feasibility checks do not substitute for that full matrix and are excluded from formal results.

The reported batch is complete: F01–F12 for each of six models. F13–F18 are retained as unused original materials and have been abandoned, not scheduled for further runs. This guide documents the procedure and does not authorize new experiments. A model's assertion of isolation is not proof that previous context was absent.
