import pytest
import os
import sqlite3
from unittest.mock import MagicMock
from src.infrastructure.sqlite3.sqlite_history import SQLiteHistoryAdapter
from src.entities.chat import ChatMessage
from src.use_cases.ports.interfaces import LoggerPort

@pytest.fixture
def temp_db():
    db_path = "tests/test_history.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def mock_logger():
    return MagicMock(spec=LoggerPort)

@pytest.mark.asyncio
async def test_sqlite_history_save_and_get(temp_db, mock_logger):
    adapter = SQLiteHistoryAdapter(db_path=temp_db, logger=mock_logger)
    
    msg = ChatMessage(
        chat_id=123,
        user_id=456,
        text="hola",
        role="user",
        session_id="chat_123",
        metadata={"key": "value"}
    )
    
    await adapter.save_message(msg)
    
    history = await adapter.get_recent_history(123)
    assert len(history) == 1
    assert history[0].text == "hola"
    assert history[0].role == "user"
    assert history[0].metadata == {"key": "value"}

@pytest.mark.asyncio
async def test_sqlite_history_limit(temp_db, mock_logger):
    adapter = SQLiteHistoryAdapter(db_path=temp_db, logger=mock_logger)
    
    for i in range(15):
        msg = ChatMessage(chat_id=1, user_id=1, text=f"msg {i}", role="user")
        await adapter.save_message(msg)
        
    history = await adapter.get_recent_history(1, limit=5)
    assert len(history) == 5
    # Deberían ser los últimos 5, y el último debería ser "msg 14"
    assert history[-1].text == "msg 14"

@pytest.mark.asyncio
async def test_sqlite_history_order(temp_db, mock_logger):
    adapter = SQLiteHistoryAdapter(db_path=temp_db, logger=mock_logger)
    
    await adapter.save_message(ChatMessage(chat_id=1, user_id=1, text="primero", role="user"))
    await adapter.save_message(ChatMessage(chat_id=1, user_id=1, text="segundo", role="user"))
    
    history = await adapter.get_recent_history(1)
    assert history[0].text == "primero"
    assert history[1].text == "segundo"

def test_sqlite_history_init_logging(temp_db, mock_logger):
    SQLiteHistoryAdapter(db_path=temp_db, logger=mock_logger)
    mock_logger.info.assert_called_with(f"🗄️ Base de datos inicializada en: {temp_db}")
