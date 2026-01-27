from collections import defaultdict
from typing import List, Dict
from api.contracts.write import ActionWrite

# session_id -> actions
_ACTIONS: Dict[str, List[ActionWrite]] = defaultdict(list)


def add_action(session_id: str, action: ActionWrite) -> int:
    _ACTIONS[session_id].append(action)
    return len(_ACTIONS[session_id])


def get_actions(session_id: str) -> List[ActionWrite]:
    return list(_ACTIONS.get(session_id, []))
