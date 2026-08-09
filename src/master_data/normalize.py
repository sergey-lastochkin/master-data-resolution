from __future__ import annotations

import re
import unicodedata

from .models import Record

LEGAL = {"ООО", "АО", "ЗАО", "ОАО", "OAO", "LLC", "INC"}


def text(value: str) -> str:
    return " ".join(
        unicodedata.normalize("NFKC", value or "")
        .upper()
        .replace('"', " ")
        .replace("'", " ")
        .split()
    )


def company_name(value: str) -> str:
    return " ".join(x for x in re.split(r"\W+", text(value)) if x and x not in LEGAL)


def product_name(value: str) -> str:
    return re.sub(r"\b(ШТ|КГ|УПАКОВКА)\b", "", text(value)).strip()


def sku(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text(value))


def digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def blocks(record: Record) -> set[str]:
    """Multiple compact keys preserve recall while comparisons scale with candidate buckets."""
    out = set()
    if record.kind == "company":
        if record.inn:
            out.add("inn:" + digits(record.inn))
        if record.phone:
            out.add("phone:" + digits(record.phone)[-7:])
        if record.email and "@" in record.email:
            out.add("domain:" + record.email.lower().split("@")[-1])
        normalized = company_name(record.name)
        # Full normalised name avoids a pathological common-prefix bucket.
        if normalized:
            out.add("company-name:" + normalized)
    else:
        if record.sku:
            out.add("sku:" + sku(record.sku))
        if record.manufacturer_sku and record.brand:
            out.add("mfg:" + sku(record.manufacturer_sku) + ":" + text(record.brand))
        normalized = product_name(record.name)
        if normalized:
            out.add("product-name:" + normalized)
    return out
