Reproduction

The analysis used only the two supplied files. Copies are in submission/inputs/.
The executed scripts expect an upload/ directory next to submission/, containing
data(4).csv and STUDY_DESCRIPTION(4).md with their original names. To reproduce,
copy the supplied input copies there. Run from the directory containing submission/:

python submission/code/run_capture.py explore_reproduction python submission/code/explore.py
python submission/code/run_capture.py final_reproduction python submission/code/final_analysis.py
python submission/code/run_capture.py report_reproduction python submission/code/write_report.py

Requirements: Python, NumPy, pandas, SciPy. Versions are recorded in results/initial_results.json.
explore_v1_missing_dependency.py preserves the original failed source; do not use it
for reproduction. The original traceback remains in results/01_explore_execution.txt.
