# Inspecting and verifying this submission

From the repository root, run the dependency-free package check:

```sh
python scripts/validate_submission.py
```

It validates public file hashes, 915 byte-identical original artifacts, 72 cases, result totals, 36 semantic pairs, the case-to-data mapping, dataset sizes and local Markdown links. It does not execute submitted model code, regrade answers, authenticate model identity or establish backend isolation.

For the original offline implementation checks, use Python 3.12 and the dependencies in `pyproject.toml` / `uv.lock`:

```sh
uv sync --group dev
uv run python -m pytest -q
uv run python -m scripts.audit_data --public-only
uv run python -m verification.selftest
```

The independent selftest uses registered checking seeds and writes temporary evidence under `verification/selftest_*`; these paths are Git-excluded. It makes no tested-model calls. Numerical generation and statistical routines are unchanged. Small protocol-reading adapters use `manifests/frozen_protocol.md.gz` for the original frozen identity. English planning.md is the reading translation, with its own hash in the translation manifest. The main and independent implementations retain separate readers.

The public package contains 12 selected datasets, all 60 public candidate CSVs, calibration summaries, all four qualification failures, and compact independent-comparison evidence. Qualification/calibration documents are preserved records of the **earlier offline stage**, so statements such as “No tested models have run” describe their original time, not today's completed 72-answer batch.

Full hidden student records, complete controller repetitions and original ZIP archives remain in the controlled source project. Replaying the complete locked generation/calibration workflow needs that original evidence and compatible runtime; this public copy does not pretend to contain them. Do not use `--verify-only` as a public-clone command. Historical manifest file lists can name controlled files that are intentionally excluded; the current public manifest is `manifests/submission_manifest.json`.

The neutral App prompt and artifact-based rubric differ from the earlier offline baseline prompt/extractor. The latter are retained for frozen source compatibility, not presented as the scientific grader for current results. Cloud paths inside submitted code and outputs are original evidence, not portable instructions. Model-answer collection was manual; this repository does not contain an automated runner that can recreate the original App conversations.

## English translation and original evidence

Human-readable study documents and grading reasons are in English. The deterministic frozen-protocol archive preserves the original source bytes without presenting them as the English reading document. Historical code-registration hashes belong to the original implementation; the translation adapters have separate current hashes and do not retroactively change those registrations. Complete locked regeneration still requires the original controlled source context. Translation does not change scores, estimates, seeds, parameters, public inputs or any of the 915 original submitted artifacts.

## Public copies and report maintenance

Machine-specific paths have been removed from historical environment and offline-access display records. `manifests/path_redaction.json` records original and public-copy hashes. Placeholders in historical sandbox profiles are documentary and must not be executed. Public display records cannot satisfy the original locked generation gate; it correctly rejects their changed hashes. Historical hash maps still identify the controlled original bytes; `manifests/submission_manifest.json` covers the current public copies. The independent reference program derives its Python installation root from the active interpreter instead of a machine-specific prefix.

The root README is the complete public research account. The controlled working project retains its separate report; its research sections are included in the README with public-layout links. Future research-report edits must update the corresponding README sections. Changes to a public file require updating its current manifest hash.
