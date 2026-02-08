from collections import defaultdict
from domain.core.identity_schema import empty_identity

CRYSTAL_THRESHOLD = 3     # days
DECAY_RATE = 0.9          # forgetting

def crystallize(identity: dict, patterns: dict, day: str) -> dict:
    base_identity = empty_identity()
    if identity:
        base_identity.update(dict(identity))

    confidence = defaultdict(float, base_identity.get("confidence", {}))
    evidence = defaultdict(int, base_identity.get("evidence", {}))

    for category in sorted(patterns.keys()):
        items = patterns.get(category, []) or []
        for item in sorted(items):
            key = f"{category}:{item}"
            evidence[key] += 1
            confidence[key] += 1

    # decay unused traits
    active_keys = {f"{c}:{i}" for c in patterns for i in (patterns.get(c, []) or [])}
    for key in list(confidence.keys()):
        if key not in active_keys:
            confidence[key] *= DECAY_RATE

    # promote to crystallized identity
    crystallized = defaultdict(list)
    for key, count in evidence.items():
        if count >= CRYSTAL_THRESHOLD:
            cat, val = key.split(":", 1)
            crystallized[cat].append(val)

    updated_identity = dict(base_identity)
    updated_identity.update({
        **crystallized,
        "confidence": dict(confidence),
        "evidence": dict(evidence),
        "last_updated": day
    })

    return updated_identity
