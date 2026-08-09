# Project status

## IMPLEMENTED

Company/product normalization; multi-key blocking; candidate evidence/features; hard conflicts; auto/manual/no-match outcomes; rejection memory; canonical IDs; provenance/survivorship; conflict-safe component union; deterministic 10k benchmark; precision/recall/F1/auto-match precision/manual-review/false-merge metrics.

## TESTED

Python 3.12 unit suite and timed 10,000-record synthetic benchmark with candidate-pair count and metrics.

## NOT TESTED

Live source systems, production merge, persisted review workflow, multilingual legal normalization at scale and privacy/retention policy.

## EXTERNAL DEPENDENCIES

Python 3.11+ standard library; `pytest` for tests.

## KNOWN LIMITATIONS

Benchmark generation creates clean duplicate pairs and is not representative of production ambiguity. Policy state is in memory; thresholds are illustrative.

## NEXT PRODUCTION STEPS

Label an approved representative dataset, persist review decisions/provenance, add source freshness and role controls, tune per-domain thresholds and validate false merges before enabling any master-data writeback.
