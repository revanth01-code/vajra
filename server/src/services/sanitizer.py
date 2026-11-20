import re


_AWS_KEY_PATTERN = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
_DATABASE_PASSWORD_PATTERN = re.compile(
    r"(?P<prefix>(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://"
    r"[^/\s:@]+:)(?P<password>[^@\s]+)(?=@)"
)
_PRIVATE_IP_PATTERN = re.compile(
    r"\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b"
)
_BEARER_PATTERN = re.compile(
    r"(?i)(\bBearer\s+)[A-Za-z0-9._~+/=-]+"
)


def sanitize_text(text: str) -> str:
    sanitized = _AWS_KEY_PATTERN.sub("[REDACTED]", text)
    sanitized = _DATABASE_PASSWORD_PATTERN.sub(
        lambda match: f"{match.group('prefix')}[REDACTED]@", sanitized
    )
    sanitized = _PRIVATE_IP_PATTERN.sub("[REDACTED]", sanitized)
    return _BEARER_PATTERN.sub(r"\1[REDACTED]", sanitized)
