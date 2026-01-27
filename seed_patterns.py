from persistence.session_repository import SessionRepository
import datetime
import uuid

SESSION_ID = "d7255ec0-7bad-4ef9-b83f-3a11edae380e"


repo = SessionRepository()

for i in range(3):
    day = (datetime.datetime.utcnow() - datetime.timedelta(days=i)).isoformat()[:10]

    repo.append_event({
        "id": str(uuid.uuid4()),
        "session_id": "demo",
        "timestamp": day + "T09:00:00",
        "type": "presence",
        "payload": {"state": "focused"},
        "source": "test"
    })

    repo.append_event({
        "id": str(uuid.uuid4()),
        "session_id": "demo",
        "timestamp": day + "T12:00:00",
        "type": "skills",
        "payload": {"focus": 95},
        "source": "test"
    })

print("Seeded pattern events")
