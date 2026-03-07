def precision_at_k(actual: list, predicted: list, k: int) -> float:
    """ Evaluates how many of the top K predictions were actually relevant. """
    if not predicted or not actual: return 0.0
    k_predicted = predicted[:k]
    relevant_hits = len(set(k_predicted).intersection(set(actual)))
    return round(relevant_hits / k, 3)

def recall_at_k(actual: list, predicted: list, k: int) -> float:
    """ Evaluates how many of the relevant items were successfully predicted within the top K. """
    if not predicted or not actual: return 0.0
    k_predicted = predicted[:k]
    relevant_hits = len(set(k_predicted).intersection(set(actual)))
    return round(relevant_hits / len(actual), 3)

def confidence_analysis(confidence_scores: list) -> dict:
    """ Aggregates raw confidence telemetry across a batch of queries """
    if not confidence_scores: return {"mean": 0, "min": 0, "max": 0}
    return {
        "mean_confidence": round(sum(confidence_scores) / len(confidence_scores), 2),
        "min_confidence": min(confidence_scores),
        "max_confidence": max(confidence_scores)
    }

def hallucination_rate(hallucination_scores: list, threshold=0.3) -> float:
    """ Calculates what percentage of queries exhibited hallucination above a given severity threshold """
    if not hallucination_scores: return 0.0
    violations = len([s for s in hallucination_scores if s >= threshold])
    return round((violations / len(hallucination_scores)) * 100, 2)
