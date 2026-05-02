import pytest
from src.entities.chat import ChatMessage
from src.entities.ai import AIResponse
from src.entities.validation import ValidationReport
from src.entities.network import NetworkState

def test_chat_message_entity():
    msg = ChatMessage(chat_id=123, user_id=456, text="hola", username="testuser")
    assert msg.chat_id == 123
    assert msg.text == "hola"
    assert msg.is_command is False

def test_chat_message_is_command():
    msg = ChatMessage(chat_id=123, user_id=456, text="/reset")
    assert msg.is_command is True

def test_ai_response_entity():
    resp = AIResponse(text="respuesta", success=True)
    assert resp.text == "respuesta"
    assert resp.success is True
    assert resp.error_message is None

def test_validation_report_entity():
    report = ValidationReport()
    report.add_info("info")
    report.add_error("error")
    report.add_critical("critico")
    
    assert "info" in report.info_messages
    assert "error" in report.error_messages
    assert "critico" in report.critical_messages
    assert report.is_ok is False

def test_network_state_entity():
    state = NetworkState(webhook_url="http://test.com", is_healthy=True)
    assert state.webhook_url == "http://test.com"
    assert state.is_healthy is True
