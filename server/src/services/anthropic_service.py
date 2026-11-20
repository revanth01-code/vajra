import xml.etree.ElementTree as ET
from typing import Any

from src.config.anthropic_client import get_client


MODEL = "openai/gpt-oss-120b"

HYPOTHESIS_SYSTEM = """You are a senior SRE with 10 years of production debugging experience.
Analyze the incident and return EXACTLY this XML structure with exactly 3 hypotheses.
Return raw XML only, no markdown, no explanation, nothing else before or after the XML.

<hypotheses>
<hypothesis rank="1" confidence="0.91">
<cause>specific root cause here</cause>
<evidence>specific evidence from the data provided</evidence>
<fix>specific actionable fix</fix>
</hypothesis>
<hypothesis rank="2" confidence="0.61">
<cause>second most likely cause</cause>
<evidence>evidence for this hypothesis</evidence>
<fix>fix for this hypothesis</fix>
</hypothesis>
<hypothesis rank="3" confidence="0.28">
<cause>third possibility</cause>
<evidence>evidence for third hypothesis</evidence>
<fix>fix for third hypothesis</fix>
</hypothesis>
</hypotheses>"""

REPORT_SYSTEM = """You are a senior SRE writing a production incident report.
Write a clear markdown report. Use these exact section headers:
# Incident Report — [service name]
## Timeline
## Root Cause
## Impact
## Immediate Fix
## Permanent Fix
Return only the markdown, nothing else."""


def _call_groq(system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
    response = get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    return response.choices[0].message.content


def _fallback_hypotheses() -> list[dict[str, Any]]:
    return [
        {
            "rank": 1,
            "confidence": 0.0,
            "cause": "Investigation failed - Groq API unavailable",
            "evidence": "No AI-generated evidence is available.",
            "fix": "Retry the investigation when the Groq API is available.",
        }
    ]


def _fallback_report() -> str:
    return "Groq API unavailable; report generation was not completed."


def generate_hypotheses(state: dict[str, Any]) -> list[dict[str, Any]]:
    parsed = state.get("parsed_error", {})
    incidents = state.get("retrieved_incidents", [])
    commits = state.get("recent_commits", [])

    incidents_text = "\n".join(
        f'- [{i["service_type"]}] Cause: {i["root_cause"]} | Fix: {i["fix_applied"]}'
        for i in incidents
    ) or "No similar incidents found."

    commits_text = "\n".join(
        f'- {"[SUSPICIOUS] " if c.get("suspicious") else ""}{c["sha"][:7]} {c["message"]}'
        for c in commits
    ) or "No recent commits provided."

    user_prompt = f"""INCIDENT:
Service: {parsed.get("service", "unknown")}
Error Type: {parsed.get("error_type", "unknown")}
Message: {parsed.get("error_message", "unknown")}
File Paths: {", ".join(parsed.get("file_paths", []))}
Timestamp: {parsed.get("timestamp", "unknown")}

SIMILAR PAST INCIDENTS:
{incidents_text}

RECENT GIT COMMITS:
{commits_text}

Return the XML hypotheses now."""

    try:
        raw = _call_groq(HYPOTHESIS_SYSTEM, user_prompt, max_tokens=1200)
        start = raw.find("<hypotheses>")
        end = raw.find("</hypotheses>") + len("</hypotheses>")
        if start == -1 or end < len("</hypotheses>"):
            return _fallback_hypotheses()
        root = ET.fromstring(raw[start:end])
        results = []
        for h in root.findall("hypothesis"):
            try:
                confidence = float(h.get("confidence", "0"))
                confidence = max(0.0, min(1.0, confidence))
            except ValueError:
                confidence = 0.0
            results.append(
                {
                    "rank": int(h.get("rank", len(results) + 1)),
                    "confidence": confidence,
                    "cause": (h.findtext("cause") or "").strip(),
                    "evidence": (h.findtext("evidence") or "").strip(),
                    "fix": (h.findtext("fix") or "").strip(),
                }
            )
        return results if results else _fallback_hypotheses()
    except Exception:
        return _fallback_hypotheses()


def generate_report(state: dict[str, Any]) -> str:
    parsed = state.get("parsed_error", {})
    hypotheses = state.get("hypotheses", [])
    top = hypotheses[0] if hypotheses else {}

    user_prompt = f"""Write an incident report for this production incident.

Service: {parsed.get("service", "unknown")}
Error: {parsed.get("error_type", "unknown")} — {parsed.get("error_message", "")}
Timestamp: {parsed.get("timestamp", "unknown")}

Top Root Cause ({int(top.get("confidence", 0) * 100)}% confidence):
{top.get("cause", "Unknown")}

Evidence:
{top.get("evidence", "None")}

Recommended Fix:
{top.get("fix", "None")}

Write the full markdown incident report now."""

    try:
        return _call_groq(REPORT_SYSTEM, user_prompt, max_tokens=800)
    except Exception:
        return _fallback_report()
