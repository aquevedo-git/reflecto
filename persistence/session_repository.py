import sqlite3
import json
from typing import List, Optional
from .models import SessionRecord

class SessionRepository:
    def __init__(self, db_path: str = 'sessions.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    data TEXT NOT NULL,
                    version TEXT NOT NULL
                )
            ''')

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
            cur = conn.execute('SELECT id, user_id, created_at, data, version FROM sessions WHERE id = ?', (session_id,))
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
            cur = conn.execute('SELECT id, user_id, created_at, data, version FROM sessions WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
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
