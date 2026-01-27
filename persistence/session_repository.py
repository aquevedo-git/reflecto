import sqlite3
import json
import datetime
from uuid import uuid4
from typing import List, Optional
from .models import SessionRecord




class SessionRepository:
    def __init__(self, db_path: str = 'sessions.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # Sessions table (existing)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    data TEXT NOT NULL,
                    version TEXT NOT NULL
                )
            ''')

            # Event journal table (C.1)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_events (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    source TEXT NOT NULL
                )
            """)

            # Daily snapshots table (C.2)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_snapshots (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    day TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    snapshot TEXT NOT NULL,
                    version TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_snapshots_user_day
                ON daily_snapshots (user_id, day)
            """)

                        # Avatar state table (C.3)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS avatar_state (
                    user_id TEXT PRIMARY KEY,
                    updated_at TEXT NOT NULL,
                    state TEXT NOT NULL,
                    version TEXT NOT NULL
                )
            """)



    # ----------------------------
    # Session persistence (existing)
    # ----------------------------

    def save(self, session_record: SessionRecord) -> str:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT INTO sessions (id, user_id, created_at, data, version) VALUES (?, ?, ?, ?, ?)',
                (
                    session_record.id,
                    session_record.user_id,
                    session_record.created_at,
                    json.dumps(session_record.data),
                    session_record.version
                )
            )
        return session_record.id

    def get(self, session_id: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                'SELECT id, user_id, created_at, data, version FROM sessions WHERE id = ?',
                (session_id,)
            )
            row = cur.fetchone()
            if row:
                return {
                    'id': row[0],
                    'user_id': row[1],
                    'created_at': row[2],
                    'data': json.loads(row[3]),
                    'version': row[4]
                }
            return None

    def list_for_user(self, user_id: str) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                'SELECT id, user_id, created_at, data, version '
                'FROM sessions WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            )
            return [
                {
                    'id': row[0],
                    'user_id': row[1],
                    'created_at': row[2],
                    'data': json.loads(row[3]),
                    'version': row[4]
                }
                for row in cur.fetchall()
            ]

    # ----------------------------
    # Event journal (C.1)
    # ----------------------------

    def append_event(self, event: dict):
        """
        Append-only event journal write.
        NEVER update or overwrite events.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO session_events (
                    id, session_id, timestamp, type, payload, source
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event["id"],
                event["session_id"],
                event["timestamp"],
                event["type"],
                json.dumps(event["payload"]),
                event["source"]
            ))

    def get_events(self, session_id: str) -> List[dict]:
        """
        Read event journal in chronological order for replay.
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                SELECT id, session_id, timestamp, type, payload, source
                FROM session_events
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """, (session_id,))
            return [
                {
                    "id": r[0],
                    "session_id": r[1],
                    "timestamp": r[2],
                    "type": r[3],
                    "payload": json.loads(r[4]),
                    "source": r[5]
                }
                for r in cur.fetchall()
            ]
        
    # ----------------------------
    # Daily snapshots (C.2)
    # ----------------------------

    def upsert_daily_snapshot(self, user_id: str, day: str, snapshot: dict, version: str = "v1") -> str:
        snapshot_id = f"snap_{uuid4()}"
        created_at = datetime.datetime.utcnow().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO daily_snapshots (
                    id, user_id, day, created_at, snapshot, version
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id,
                user_id,
                day,
                created_at,
                json.dumps(snapshot),
                version
            ))

        return snapshot_id

    def get_daily_snapshot(self, user_id: str, day: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                SELECT id, user_id, day, created_at, snapshot, version
                FROM daily_snapshots
                WHERE user_id = ? AND day = ?
                LIMIT 1
            """, (user_id, day))
            row = cur.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "user_id": row[1],
                "day": row[2],
                "created_at": row[3],
                "snapshot": json.loads(row[4]),
                "version": row[5],
            }

    def list_daily_snapshots(self, user_id: str, limit: int = 60) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                SELECT id, user_id, day, created_at, snapshot, version
                FROM daily_snapshots
                WHERE user_id = ?
                ORDER BY day DESC
                LIMIT ?
            """, (user_id, limit))

            return [
                {
                    "id": r[0],
                    "user_id": r[1],
                    "day": r[2],
                    "created_at": r[3],
                    "snapshot": json.loads(r[4]),
                    "version": r[5],
                }
                for r in cur.fetchall()
            ]

    def get_events_for_user_day(self, user_id: str, day: str) -> List[dict]:
        """
        C.2 helper: get all events for all sessions belonging to user, filtered to UTC day prefix.
        (We’ll upgrade to a more direct query later by storing user_id on events.)
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                SELECT id FROM sessions
                WHERE user_id = ?
            """, (user_id,))
            session_ids = [r[0] for r in cur.fetchall()]

        if not session_ids:
            return []

        placeholders = ",".join(["?"] * len(session_ids))
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(f"""
                SELECT id, session_id, timestamp, type, payload, source
                FROM session_events
                WHERE session_id IN ({placeholders})
                  AND timestamp LIKE ?
                ORDER BY timestamp ASC
            """, (*session_ids, f"{day}%"))

            return [
                {
                    "id": r[0],
                    "session_id": r[1],
                    "timestamp": r[2],
                    "type": r[3],
                    "payload": json.loads(r[4]),
                    "source": r[5],
                }
                for r in cur.fetchall()
            ]

    # ----------------------------
    # Avatar state (C.3)
    # ----------------------------

    def get_avatar_state(self, user_id: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                SELECT user_id, updated_at, state, version
                FROM avatar_state
                WHERE user_id = ?
                LIMIT 1
            """, (user_id,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "user_id": row[0],
                "updated_at": row[1],
                "state": json.loads(row[2]),
                "version": row[3],
            }

    def upsert_avatar_state(self, user_id: str, state: dict, version: str = "v1") -> None:
        updated_at = datetime.datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO avatar_state (user_id, updated_at, state, version)
                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                updated_at,
                json.dumps(state),
                version
            ))

