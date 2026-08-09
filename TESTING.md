# Testing

After the README test install, run `.venv/bin/python -m pytest -q` and `.venv/bin/python scripts/benchmark.py --records 10000`. Tests verify normalization, sparse blocking, hard conflicts, exact company/product decisions, rejection memory, idempotent/colliding mappings, provenance survivorship, transitive conflict protection and metric definitions. The benchmark asserts that 10,000 records do not create an all-pairs candidate set.
