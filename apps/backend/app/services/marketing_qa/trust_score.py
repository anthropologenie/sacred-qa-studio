def compute_score(results: list[dict]) -> int:
    # simple: pass=1, warning=0.5, fail=0
    weights = {"pass":1.0,"warning":0.5,"fail":0.0}
    if not results: return 0
    s = sum(weights.get(r.get("status","fail"),0) for r in results)
    return round(100 * s / len(results))
