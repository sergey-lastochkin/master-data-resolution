from __future__ import annotations


def evaluate(
    predictions: dict[tuple[str, str], str], truth: set[tuple[str, str]]
) -> dict[str, float]:
    auto = {pair for pair, decision in predictions.items() if decision == "AUTO_MATCH"}
    tp = len(auto & truth)
    fp = len(auto - truth)
    fn = len(truth - auto)
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    review = sum(x == "MANUAL_REVIEW" for x in predictions.values()) / max(
        1, len(predictions)
    )
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "precision_auto_match": precision,
        "manual_review_rate": review,
        "false_merge_rate": fp / max(1, len(auto)),
    }
