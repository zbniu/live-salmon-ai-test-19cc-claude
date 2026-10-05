#!/usr/bin/env bash
# Exact command executed after archive validation; failed before upload.
python3 /root/.codex/plugins/cache/openai-curated-remote/openai-library/0.1.61/skills/library/scripts/library_upload.py <<'JSON'
{"uploads":[{"local_path":"/workspace/scratch/cc98ef88aef6/submission/final_report.md","purpose":"create_library_file","library_artifact_type":"report"},{"local_path":"/workspace/scratch/cc98ef88aef6/submission.zip","purpose":"create_library_file","library_artifact_type":"other"}]}
JSON
