import re
from typing import Any


_SERVICE_PATTERNS = (
    re.compile(r"\bservice(?:\s+name)?\s*[:=]\s*([A-Za-z0-9._/-]+)", re.IGNORECASE),
    re.compile(r"\b(?:service|app|application)\s+([A-Za-z0-9._/-]+)", re.IGNORECASE),
)
_ERROR_TYPE_PATTERN = re.compile(
    r"\b([A-Za-z][A-Za-z0-9]*(?:Error|Exception|Failure|Timeout))\b"
)
_TIMESTAMP_PATTERNS = (
    re.compile(r"\b\d{4}-\d{2}-\d{2}[T ][0-9:.+-]+(?:Z)?\b"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
)
_FILE_PATH_PATTERN = re.compile(
    r"(?<![\w.-])(?:[A-Za-z]:[\\/])?[\w./\\-]+"
    r"\.(?:jsx|tsx|yaml|yml|json|py|js|ts|java|go|rb|rs|sql)"
    r"(?::\d+(?::\d+)?)?"
)


def _first_match(patterns: tuple[re.Pattern[str], ...], text: str) -> str:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1) if match.lastindex else match.group(0)
    return ""


def parse_error(raw_text: str) -> dict[str, Any]:
    service = _first_match(_SERVICE_PATTERNS, raw_text) or "unknown"
    error_type = _first_match((_ERROR_TYPE_PATTERN,), raw_text) or "unknown"
    timestamp = _first_match(_TIMESTAMP_PATTERNS, raw_text)
    file_paths = list(dict.fromkeys(match.group(0) for match in _FILE_PATH_PATTERN.finditer(raw_text)))

    return {
        "service": service,
        "error_type": error_type,
        "error_message": raw_text.strip(),
        "file_paths": file_paths,
        "timestamp": timestamp or None,
        "raw_text": raw_text,
    }


def error_parser(state: dict[str, Any]) -> dict[str, Any]:
    return {"parsed_error": parse_error(state.get("raw_input", ""))}
