from master_data.resolution import *


def company(ref, name="ООО Ромашка", inn="123", source="1c", **kw):
    return Record(source, ref, "company", name, inn=inn, **kw)


def product(ref, skuval="ABC-123", brand="ACME", source="s", **kw):
    return Record(source, ref, "product", "Widget", sku=skuval, brand=brand, **kw)


def test_company_and_product_normalization():
    assert (
        company_name('ООО "Ромашка"') == "РОМАШКА"
        and sku("abc - 123") == "ABC123"
        and product_name("Widget, 1 шт") == "WIDGET, 1"
    )


def test_exact_identifiers_auto_and_conflicts():
    assert (
        score(company("a"), company("b", name="Ромашка ООО", source="erp")).decision
        == "AUTO_MATCH"
    )
    assert score(company("a", inn="1"), company("b", inn="2")).decision == "CONFLICT"
    assert score(product("a"), product("b", brand="OTHER")).decision == "CONFLICT"


def test_blocking_does_not_generate_all_pairs():
    rows = [
        company("a", inn="1"),
        company("b", inn="1"),
        company("c", name="ООО Ирис", inn="9"),
    ]
    candidates = Resolver().candidates(rows)
    assert len(candidates) == 1 and candidates[0].blocks == (
        "company-name:РОМАШКА",
        "inn:1",
    )


def test_prior_rejection_and_idempotent_mapping():
    a, b = company("a"), company("b", source="erp")
    resolver = Resolver()
    resolver.reject(a, b)
    assert resolver.propose(a, b).reasons == ["prior rejection remembered"]
    assert resolver.apply("1c", "a", "entity1") == resolver.apply("1c", "a", "entity1")


def test_mapping_conflict_and_survivorship():
    r = Resolver()
    r.apply("1c", "a", "e1")
    try:
        r.apply("1c", "a", "e2")
        assert False
    except ValueError:
        pass
    r.set_field("e", "name", Provenance("parser", "supplier", "2026-01-02", False, 0.9))
    r.set_field("e", "name", Provenance("legal", "1c", "2026-01-01", True, 0.8))
    assert r.canonical_value("e", "name") == "legal"


def test_false_transitive_merge_is_blocked():
    a = company("a", inn="1")
    b = company("b", inn="1", source="erp")
    c = company("c", inn="2", source="crm")
    m = safe_components([(a.key, b.key), (b.key, c.key)], [a, b, c])
    assert m[a.key] == m[b.key] and m[c.key] != m[a.key]


def test_evaluation_metrics():
    result = evaluate(
        {
            ("a", "b"): "AUTO_MATCH",
            ("c", "d"): "AUTO_MATCH",
            ("e", "f"): "MANUAL_REVIEW",
        },
        {("a", "b"), ("x", "y")},
    )
    assert (
        result["precision"] == 0.5
        and result["recall"] == 0.5
        and result["false_merge_rate"] == 0.5
        and result["manual_review_rate"] == 1 / 3
    )


def test_deterministic_10k_benchmark_contract():
    from scripts.benchmark import generate, run

    records, truth = generate(10_000)
    result = run(records, truth)
    assert (
        len(records) == 10_000
        and len(truth) == 5_000
        and result["candidate_pairs"] < 60_000
        and result["f1"] > 0.99
    )
