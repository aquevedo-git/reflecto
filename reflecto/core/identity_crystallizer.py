from datetime import datetime
from collections import defaultdict
from reflecto.core.identity_schema import empty_identity

CRYSTAL_THRESHOLD = 3     # days
DECAY_RATE = 0.9          # forgetting

def crystallize(identity: dict, patterns: dict, day: str) -> dict:
    if not identity:
        identity = empty_identity()

    confidence = identity.get("confidence", defaultdict(float))
    evidence = identity.get("evidence", defaultdict(int))

    for category, items in patterns.items():
        for item in items:
            key = f"{category}:{item}"
            evidence[key] += 1
            confidence[key] += 1

    # decay unused traits
    for key in list(confidence.keys()):
        if key not in [f"{c}:{i}" for c in patterns for i in patterns[c]]:
            confidence[key] *= DECAY_RATE

    # promote to crystallized identity
    crystallized = defaultdict(list)
    for key, count in evidence.items():
        if count >= CRYSTAL_THRESHOLD:
            cat, val = key.split(":", 1)
            crystallized[cat].append(val)

    identity.update({
        **crystallized,
        "confidence": dict(confidence),
        "evidence": dict(evidence),
        "last_updated": day
    })

    return identity
