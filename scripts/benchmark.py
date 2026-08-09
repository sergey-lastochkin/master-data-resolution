"""Deterministic synthetic 10k benchmark; it intentionally contains no customer data."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from master_data.metrics import evaluate
from master_data.models import Record
from master_data.resolver import Resolver


def generate(total=10_000):
    if total % 2:
        raise ValueError("total must be even")
    records = []
    truth = set()
    for i in range(total // 2):
        if i % 2:
            left = Record(
                "1c",
                f"{i}:a",
                "product",
                f"Product {i}",
                "",
                sku=f"SKU-{i:05d}",
                brand=f"Brand{i % 23}",
                manufacturer_sku=f"M-{i:05d}",
                unit="шт",
                pack_size="1",
            )
            right = Record(
                "erp",
                f"{i}:b",
                "product",
                f"product {i}",
                "",
                sku=f"sku {i:05d}",
                brand=f"Brand{i % 23}",
                manufacturer_sku=f"M{i:05d}",
                unit="шт",
                pack_size="1",
            )
        else:
            left = Record(
                "1c",
                f"{i}:a",
                "company",
                f"ООО Компания {i}",
                inn=f"SYNTH-INN-{i:05d}",
                kpp=f"SYNTH-KPP-{i % 100:02d}",
            )
            right = Record(
                "erp",
                f"{i}:b",
                "company",
                f"Компания {i} ООО",
                inn=f"SYNTH-INN-{i:05d}",
                kpp=f"SYNTH-KPP-{i % 100:02d}",
            )
        records += [left, right]
        truth.add(tuple(sorted((left.key, right.key))))
    return records, truth


def run(records, truth):
    resolver = Resolver()
    started = time.perf_counter()
    predictions = {}
    for candidate in resolver.candidates(records):
        predictions[resolver.pairkey(candidate.left, candidate.right)] = (
            resolver.propose(candidate.left, candidate.right).decision
        )
    return {
        "records": len(records),
        "candidate_pairs": len(predictions),
        "seconds": round(time.perf_counter() - started, 4),
        **evaluate(predictions, truth),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=10_000)
    args = parser.parse_args()
    print(run(*generate(args.records)))
