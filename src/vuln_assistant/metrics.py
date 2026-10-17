"""Case-level binary metrics required by the supervisor: accuracy, precision, recall.

Unit of evaluation: one source file (case) with respect to its labelled weakness family.
A case is predicted positive when at least one detection of that family is reported in
it. Counts are always returned with the ratios so denominators stay visible; an undefined
ratio (zero denominator) is None rather than 0.
"""


def confusion(expected: list[bool], predicted: list[bool]) -> dict[str, int]:
    if len(expected) != len(predicted):
        raise ValueError("expected and predicted must have the same length")
    pairs = list(zip(expected, predicted, strict=True))
    return {
        "tp": sum(e and p for e, p in pairs),
        "fp": sum(not e and p for e, p in pairs),
        "tn": sum(not e and not p for e, p in pairs),
        "fn": sum(e and not p for e, p in pairs),
    }


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def scores(counts: dict[str, int]) -> dict:
    tp, fp, tn, fn = counts["tp"], counts["fp"], counts["tn"], counts["fn"]
    return {
        **counts,
        "n": tp + fp + tn + fn,
        "accuracy": _ratio(tp + tn, tp + fp + tn + fn),
        "precision": _ratio(tp, tp + fp),
        "recall": _ratio(tp, tp + fn),
    }


def evaluate(expected: list[bool], predicted: list[bool]) -> dict:
    return scores(confusion(expected, predicted))
