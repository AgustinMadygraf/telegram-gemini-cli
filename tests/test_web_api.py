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
    # Mockeamos el comportamiento asíncrono del controlador
    mock_controller.process_webhook_data = AsyncMock(return_value=MagicMock())
    
    response = client.post(
        "/webhook",
        json={"update_id": 1},
        headers={"x-telegram-bot-api-secret-token": "secret"}
    )
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_controller.execute_task.assert_called_once()

def test_webhook_forbidden(client, mock_controller):
    # Simulamos un error de permiso que el middleware debe capturar
    mock_controller.process_webhook_data = AsyncMock(side_effect=PermissionError("User 123 not allowed"))
    
    response = client.post(
        "/webhook",
        json={"update_id": 1},
        headers={"x-telegram-bot-api-secret-token": "wrong"}
    )
    
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}

def test_webhook_internal_error(client, mock_controller):
    # Simulamos un error genérico para probar el catch-all del middleware
    mock_controller.process_webhook_data = AsyncMock(side_effect=ValueError("Unexpected crash"))
    
    response = client.post(
        "/webhook",
        json={"update_id": 1}
    )
    
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
