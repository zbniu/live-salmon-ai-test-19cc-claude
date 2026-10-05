# Packaging checks

These records concern this submission copy, not new model experiments.

- [Offline unit checks](pytest.txt): 101 passed: 94 existing checks, six canonical-protocol reader checks and one public-display identity check. The missing-registration unit test uses an isolated framework fixture; production generation gates remain unchanged.
- [Independent selftest](independent_selftest.txt): 14 fixture checks passed; a registered purpose-4 checking workload completed 200/200 bootstrap attempts.
- [Check summary](checks.json): source preservation and scope of checks.
- [Contribution checks](contribution_checks.json): 104 offline tests, including three public-audit regression cases, and 14 independent selftests; no model calls or formal data regeneration.

The package validator checks original artifacts, local links, table counts and data hashes. Neither a passing checksum check nor these offline tests independently validates the original App sessions or every submitted scientific analysis.

The English translation preserves every numbered specification section, all public-material blocks, all case grades/numerical fields and all twelve-row model tables. See `manifests/translation.json` for original and translated hashes.
