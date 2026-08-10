# 1C Master Data Resolution

[![CI](https://github.com/sergey-lastochkin/master-data-resolution/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/sergey-lastochkin/master-data-resolution/actions/workflows/ci.yml)

## What

Python entity-resolution engine designed to consume company/product records exported from 1C or peer systems. It demonstrates normalization, blocking, conflict-aware scoring, remembered review decisions, canonical mappings and provenance with synthetic inputs.

## Why

Normalized-name equality alone causes false merges, while comparing every pair is O(N²). Legal identifiers and SKUs need hard-conflict rules; ambiguous cases need review memory and provenance rather than an irreversible fuzzy match.

## Architecture

- Models for source records, candidates, resolutions and field provenance.
- Domain-specific normalization and multi-key blocking for companies/products.
- Conflict-aware feature scorer and manual/auto/no-match decisions.
- Canonical mapping, prior rejection memory, survivorship and anti-transitive union.
- Benchmark generator/evaluator for precision, recall, F1, auto-match precision, manual-review and false-merge rates.

## Key engineering decisions

- Candidate generation compares only shared blocking buckets, not all pairs.
- Different INN/bank identifiers and same-SKU/different-brand are hard conflicts.
- Embeddings are not used for exact INN/SKU identity.
- A verified provenance value outranks an unverified but newer/high-confidence value.
- Component union checks cross-group conflicts before accepting a transitive merge.

## Run

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
.venv/bin/python scripts/benchmark.py --records 10000
```

## Test

```bash
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
```

Tests cover company/product normalization, blocking, exact matches, identifier/brand conflicts, rejection memory, idempotent/conflicting mappings, survivorship, transitive false-merge protection, metric math and the deterministic 10,000-record benchmark.

CI additionally runs `ruff` and `compileall`; it uses only synthetic records and does not connect to 1C or a master-data system.

## Limitations

- The benchmark is synthetic/easy and its quality metrics are not a production claim.
- Review/mapping memory is in-process; no review UI or durable audit store is included.
- Thresholds and survivorship policy require validation per target data domain.
- `bsl/MasterDataMapping.bsl` is an illustrative configuration-mapped adapter, not runtime-tested on 1C.
