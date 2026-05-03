"""
Path: tests/test_output_sanitizer.py
"""
import pytest
from src.use_cases.services.output_sanitizer import OutputSanitizerService

def test_sanitize_real_world_noise():
    sanitizer = OutputSanitizerService()
    
    noise_input = (
        "Error executing tool list_directory: Path not in workspace: Attempted path \"/home/agustin/proyectos_software\" "
        "resolves outside the allowed workspace directories\n"
        "\n"
        "Error executing tool read_file: File not found.\n"
        "\n"
        "Hello! I'm Gemini CLI. How can I assist you today?\n"
    )
    
    clean_output = sanitizer.sanitize(noise_input)
    
    assert "Error executing tool" not in clean_output
    assert "Path not in workspace" not in clean_output
    assert "Hello! I'm Gemini CLI." in clean_output
    # No debe haber bloques de líneas vacías excesivas al principio
    assert clean_output.startswith("Hello!")

def test_sanitize_control_characters():
    sanitizer = OutputSanitizerService()
    # \x02 es ^B. Simulamos ruido en una línea y respuesta en otra
    input_with_ctrl = "\x02\x02Ripgrep is not available.\nHello. How can I help?"
    output = sanitizer.sanitize(input_with_ctrl)
    assert "Ripgrep" not in output
    assert "Hello." in output

def test_sanitize_json_fragments():
    sanitizer = OutputSanitizerService()
    noise = "}\n],\nHello"
    output = sanitizer.sanitize(noise)
    assert output == "Hello"

def test_sanitize_empty_result():
    sanitizer = OutputSanitizerService()
    noise = "at node:internal/process\nerrno: -111"
    output = sanitizer.sanitize(noise)
    assert output == ""
