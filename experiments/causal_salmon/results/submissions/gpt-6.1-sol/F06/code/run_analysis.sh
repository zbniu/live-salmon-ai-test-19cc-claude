#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 1
log=submission/run_log.txt
printf '\n[%s] EXECUTE code/analyze.py using bundled Python; stdout/stderr -> results/analysis_console.txt\n' "$(date -u +%FT%TZ)" >> "$log"
"$CODEX_PRIMARY_RUNTIME_PYTHON" submission/code/analyze.py > submission/results/analysis_console.txt 2>&1
status=$?
printf '[%s] EXIT %s. Console: results/analysis_console.txt. On success, generated group_summary.csv, adjusted_sensitivity.csv, baseline_deciles.csv, ols_degree_{1,2,3}.json, analysis.json.\n' "$(date -u +%FT%TZ)" "$status" >> "$log"
cat submission/results/analysis_console.txt
exit "$status"
