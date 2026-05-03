"""
Path: src/infrastructure/sqlite3/sqlite_historypy
"""

import sqlite3
import json
import asyncio
from datetime import datetime
from typing import List
from src.use_cases.ports.interfaces import ChatHistoryGateway, ChatMessage, LoggerPort

class SQLiteHistoryAdapter(ChatHistoryGateway):
    def __init__(self, db_path: str, logger: LoggerPort):
        self.db_path = db_path
        self.logger = logger
        self._init_db()

    def _init_db(self):
        """Inicializa las tablas si no existen."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    user_id INTEGER,
                    role TEXT,
                    content TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        self.logger.info(f"🗄️ Base de datos inicializada en: {self.db_path}")

    async def save_message(self, message: ChatMessage) -> None:
        """Guarda un mensaje de forma asíncrona."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._save_message_sync, message)

    def _save_message_sync(self, message: ChatMessage):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO history (chat_id, user_id, role, content, session_id, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                message.chat_id,
                message.user_id,
                message.role,
                message.text,
                message.session_id,
                json.dumps(message.metadata) if message.metadata else None,
                message.timestamp or datetime.now()
            ))
            conn.commit()

    async def get_recent_history(self, chat_id: int, limit: int = 10) -> List[ChatMessage]:
        """Recupera el historial reciente de forma asíncrona."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_recent_history_sync, chat_id, limit)

    def _get_recent_history_sync(self, chat_id: int, limit: int = 10) -> List[ChatMessage]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM history 
                WHERE chat_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (chat_id, limit))
            
            rows = cursor.fetchall()
            messages = []
            for row in reversed(rows):
                messages.append(ChatMessage(
                    chat_id=row['chat_id'],
                    user_id=row['user_id'],
                    role=row['role'],
                    text=row['content'],
                    session_id=row['session_id'],
                    timestamp=row['timestamp'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else None
                ))
            return messages
