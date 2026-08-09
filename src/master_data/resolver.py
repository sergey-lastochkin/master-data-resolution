from __future__ import annotations

from collections import defaultdict
from difflib import SequenceMatcher

from .models import Candidate, Provenance, Record, Resolution
from .normalize import blocks, company_name, product_name, sku, text


def features(a: Record, b: Record) -> dict[str, object]:
    same_kind = a.kind == b.kind
    name = lambda x: company_name(x) if a.kind == "company" else product_name(x)
    return {
        "same_kind": same_kind,
        "inn_exact": bool(a.inn and a.inn == b.inn),
        "inn_conflict": bool(a.inn and b.inn and a.inn != b.inn),
        "kpp_exact": bool(a.kpp and a.kpp == b.kpp),
        "bank_exact": bool(a.bank_account and a.bank_account == b.bank_account),
        "bank_conflict": bool(
            a.bank_account and b.bank_account and a.bank_account != b.bank_account
        ),
        "sku_exact": bool(a.sku and sku(a.sku) == sku(b.sku)),
        "brand_match": bool(a.brand and text(a.brand) == text(b.brand)),
        "brand_conflict": bool(a.brand and b.brand and text(a.brand) != text(b.brand)),
        "mfg_exact": bool(
            a.manufacturer_sku and sku(a.manufacturer_sku) == sku(b.manufacturer_sku)
        ),
        "unit_match": bool(a.unit and text(a.unit) == text(b.unit)),
        "pack_match": bool(a.pack_size and a.pack_size == b.pack_size),
        "name_similarity": SequenceMatcher(None, name(a.name), name(b.name)).ratio(),
    }


def score(a: Record, b: Record) -> Resolution:
    f = features(a, b)
    if not f["same_kind"]:
        return Resolution("CONFLICT", 0, f, ["different entity kinds"])
    if (
        f["inn_conflict"]
        or f["bank_conflict"]
        or (f["sku_exact"] and f["brand_conflict"])
    ):
        return Resolution("CONFLICT", 0, f, ["hard identifier conflict"])
    value = 0
    reasons = []
    for key, weight, label in [
        ("inn_exact", 0.70, "INN exact"),
        ("kpp_exact", 0.08, "KPP exact"),
        ("bank_exact", 0.10, "bank exact"),
        ("sku_exact", 0.55, "SKU exact"),
        ("unit_match", 0.04, "unit"),
        ("pack_match", 0.04, "pack"),
    ]:
        if f[key]:
            value += weight
            reasons.append(f"{label} +{weight:.2f}")
    if f["mfg_exact"] and f["brand_match"]:
        value += 0.35
        reasons.append("manufacturer SKU + brand +0.35")
    contribution = f["name_similarity"] * 0.20
    value = min(1, value + contribution)
    reasons.append(f"name similarity +{contribution:.2f}")
    auto = (f["inn_exact"] or (f["sku_exact"] and f["brand_match"])) and value >= 0.89
    decision = (
        "AUTO_MATCH" if auto else "MANUAL_REVIEW" if value >= 0.45 else "NO_MATCH"
    )
    return Resolution(decision, round(value, 4), f, reasons)


class Resolver:
    def __init__(self) -> None:
        self.rejections: set[tuple[str, str]] = set()
        self.mappings: dict[tuple[str, str], str] = {}
        self.provenance: dict[str, dict[str, list[Provenance]]] = defaultdict(
            lambda: defaultdict(list)
        )

    def pairkey(self, a: Record, b: Record) -> tuple[str, str]:
        return tuple(sorted((a.key, b.key)))

    def candidates(self, records: list[Record]) -> list[Candidate]:
        index = defaultdict(list)
        pairs = {}
        for record in records:
            for block in blocks(record):
                for prior in index[block]:
                    if prior.kind == record.kind:
                        pairs.setdefault(
                            self.pairkey(record, prior), (record, prior, set())
                        )[2].add(block)
                index[block].append(record)
        return [Candidate(a, b, tuple(sorted(hits))) for a, b, hits in pairs.values()]

    def propose(self, a: Record, b: Record) -> Resolution:
        if self.pairkey(a, b) in self.rejections:
            return Resolution("NO_MATCH", 0, {}, ["prior rejection remembered"])
        return score(a, b)

    def reject(self, a: Record, b: Record) -> None:
        self.rejections.add(self.pairkey(a, b))

    def confirm(self, canonical_id: str, *records: Record) -> str:
        for record in records:
            self.apply(record.source, record.ref, canonical_id)
        return canonical_id

    def apply(self, source: str, ref: str, canonical: str) -> str:
        old = self.mappings.get((source, ref))
        if old and old != canonical:
            raise ValueError("mapping conflict")
        self.mappings[(source, ref)] = canonical
        return canonical

    def set_field(self, entity: str, field: str, provenance: Provenance) -> None:
        self.provenance[entity][field].append(provenance)

    def canonical_value(self, entity: str, field: str) -> str | None:
        values = self.provenance[entity][field]
        return (
            max(values, key=lambda x: (x.verified, x.confidence, x.observed_at)).value
            if values
            else None
        )


def safe_components(
    edges: list[tuple[str, str]], records: list[Record]
) -> dict[str, str]:
    by_key = {r.key: r for r in records}
    parent = {key: key for key in by_key}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            continue
        left = [by_key[k] for k in by_key if find(k) == ra]
        right = [by_key[k] for k in by_key if find(k) == rb]
        if any(score(x, y).decision == "CONFLICT" for x in left for y in right):
            continue
        parent[rb] = ra
    return {key: find(key) for key in by_key}
