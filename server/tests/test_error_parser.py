import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agents.error_parser import parse_error


def test_parse_python_stack_trace():
    parsed = parse_error(
        "service=payments 2026-11-19T10:20:30Z "
        "DatabaseTimeoutError in server/db.py:42"
    )

    assert parsed["service"] == "payments"
    assert parsed["error_type"] == "DatabaseTimeoutError"
    assert "server/db.py:42" in parsed["file_paths"]


def test_parse_javascript_stack_trace():
    parsed = parse_error(
        "service checkout TypeError at src/components/Checkout.jsx:18:4"
    )

    assert parsed["service"] == "checkout"
    assert parsed["error_type"] == "TypeError"
    assert "src/components/Checkout.jsx:18:4" in parsed["file_paths"]


def test_parse_unknown_fields_without_aborting():
    parsed = parse_error("The worker returned an unexpected response.")

    assert parsed["service"] == "unknown"
    assert parsed["error_type"] == "unknown"
    assert parsed["file_paths"] == []
