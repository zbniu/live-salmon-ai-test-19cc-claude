# Independent offline verification implementation

These modules implement the frozen numerical specification independently from the main implementation. The [exchange contract](../docs/VERIFICATION_CONTRACT.md) defines comparison boundaries; [reproduction instructions](../docs/reproduction.md) provide checks.

The implementation and original fixtures are preserved byte for byte. Its temporary selftest records are excluded from the submission. Full controller evidence remains controlled; [qualification evidence](../results/qualification/README.md) supplies compact comparison findings. These offline reference checks are distinct from the now-completed 72 model answers and do not independently certify model-session isolation.
