"""
Path: tests/test_web_api.py
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from src.infrastructure.fastapi.app import create_app
from src.interface_adapters.controllers.telegram_controller import TelegramController

@pytest.fixture
def mock_controller():
    return MagicMock(spec=TelegramController)

@pytest.fixture
def client(mock_controller):
    app = create_app(controller=mock_controller)
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_webhook_success(client, mock_controller):
    # handle_webhook ahora devuelve (ChatMessage, trace_id)
    mock_controller.handle_webhook = AsyncMock(return_value=(MagicMock(), "TR-123"))
    
    response = client.post(
        "/webhook",
        json={"update_id": 1},
        headers={"x-telegram-bot-api-secret-token": "secret"}
    )
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_controller.execute_task.assert_called_once()

def test_webhook_forbidden(client, mock_controller):
    mock_controller.handle_webhook = AsyncMock(side_effect=PermissionError())
    
    response = client.post(
        "/webhook",
        json={"update_id": 1}
    )
    
    assert response.status_code == 403
    assert response.json() == {"status": "forbidden"}

def test_webhook_internal_error(client, mock_controller):
    # Errores inesperados devuelven status: error en el try/except de la ruta
    mock_controller.handle_webhook = AsyncMock(side_effect=Exception("Crash"))
    
    response = client.post(
        "/webhook",
        json={"update_id": 1}
    )
    
    assert response.status_code == 200 # Porque el try/except interno atrapa y devuelve JSON con status error
    assert response.json()["status"] == "error"
