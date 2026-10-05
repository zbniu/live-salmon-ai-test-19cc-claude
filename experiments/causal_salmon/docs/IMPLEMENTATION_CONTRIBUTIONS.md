# Implementation and verification responsibilities

**Record scope:** the offline implementation stage, before the App experiments and repository publication. Later experiments and publication are described in [the current contribution record](contributions.md).

The project owner confirmed the research design, K1 parameters and final generation policy.

The main Codex agent implemented the generator, estimators, diagnostics, public reference executable, sandbox launcher, hidden qualification checks, persistence, report extraction, summaries and comparison tools in `src/` and `scripts/`.

A separately initialized Codex agent implemented `verification/` and the independent final-data entry point from the complete specification and exchange contract. Its initial context excluded main code and intermediate numerical conclusions. Neither numerical implementation imports the other's generation or statistical code. They share the locked numerical environment, specification and frozen settings.

Both implementations completed every registered calibration repetition and every final-pool candidate. Comparison tools checked all paired numerical results, including every ordered bootstrap estimate. Source registrations, complete candidate outcomes and compact comparison records accompany the final package.

Independent programming does not constitute an independent research team or a blinded human assessment. Deterministic reference analysis is separate from tested-model evaluation. No model experiments, automated report scoring or GitHub publication have occurred.
