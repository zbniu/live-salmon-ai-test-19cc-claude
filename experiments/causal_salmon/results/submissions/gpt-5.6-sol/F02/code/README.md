# Reproduction

The substantive analysis was executed once successfully using Python 3.12.14
and NumPy 2.3.5. From an extracted archive, an equivalent reproduction command is:

    python submission/code/analyze.py submission/inputs/data.csv submission/inputs/STUDY_DESCRIPTION.md

This would write new outputs into submission/results; preserve the original
delivered results if comparing runs. Do not rerun merely to obtain a cleaner log.

The original execution used the uploaded inputs in the surrounding workspace.
run_analysis_initial.py preserves the failed wrapper attempt, which did not
launch analysis. run_analysis.py is its corrected version and captured the
successful analysis stdout and stderr. initial_inspection.py preserves the
first executed inspection snippet. create_report_and_archive.py creates the
report from existing results without recalculating any statistical analysis.
