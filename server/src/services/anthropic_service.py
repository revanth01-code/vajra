import json
from xml.etree import ElementTree

import anthropic

from src.config.anthropic_client import get_anthropic_client


MODEL_NAME = "claude-sonnet-4-6"


def _response_text(response: object) -> str:
    content = getattr(response, "content", [])
    for block in content:
        text = getattr(block, "text", None)
        if text:
            return text.strip()
    raise ValueError("Claude returned an empty response.")


def _fallback_hypotheses() -> list[dict[str, object]]:
    return [
        {
            "rank": 1,
            "confidence": 0.0,
            "cause": "Investigation failed - Claude API unavailable",
            "evidence": "No Claude-generated evidence is available.",
            "fix": "Retry the investigation when the Claude API is available.",
        }
    ]


def _hypothesis_prompt(
    parsed_error: dict[str, object],
    retrieved_incidents: list[dict[str, object]],
    recent_commits: list[dict[str, object]],
) -> str:
    context = {
        "parsed_error": parsed_error,
        "retrieved_incidents": retrieved_incidents,
        "recent_commits": recent_commits,
    }
    return (
        "Analyze this production incident as a senior SRE with 10 years of "
        "production debugging experience.\n"
        "Return exactly three root-cause hypotheses ranked 1 through 3. "
        "Use confidence values from 0 to 1 that reflect the evidence. "
        "Do not claim certainty beyond the supplied evidence.\n"
        "Return only this XML shape, with no Markdown or surrounding prose:\n"
        "<hypotheses><hypothesis><rank>1</rank><confidence>0.0</confidence>"
        "<cause>...</cause><evidence>...</evidence><fix>...</fix>"
        "</hypothesis></hypotheses>\n\n"
        f"Structured incident context:\n{json.dumps(context, indent=2, default=str)}"
    )


def _parse_hypotheses(xml_text: str) -> list[dict[str, object]]:
    start = xml_text.find("<hypotheses")
    end = xml_text.rfind("</hypotheses>")
    if start < 0 or end < 0:
        raise ValueError("Claude response did not contain hypotheses XML.")
    root = ElementTree.fromstring(xml_text[start : end + len("</hypotheses>")])
    hypotheses: list[dict[str, object]] = []

    for element in root.findall("hypothesis"):
        rank_text = element.findtext("rank") or element.get("rank")
        confidence_text = element.findtext("confidence") or element.get("confidence")
        cause = (element.findtext("cause") or "").strip()
        evidence = (element.findtext("evidence") or "").strip()
        fix = (element.findtext("fix") or "").strip()
        if not rank_text or not confidence_text or not cause or not evidence or not fix:
            raise ValueError("Claude returned an incomplete hypothesis.")
        rank = int(rank_text)
        confidence = float(confidence_text)
        if rank not in {1, 2, 3} or not 0 <= confidence <= 1:
            raise ValueError("Claude returned an invalid hypothesis rank or confidence.")
        hypotheses.append(
            {
                "rank": rank,
                "confidence": confidence,
                "cause": cause,
                "evidence": evidence,
                "fix": fix,
            }
        )

    if len(hypotheses) != 3 or {item["rank"] for item in hypotheses} != {1, 2, 3}:
        raise ValueError("Claude must return exactly three ranked hypotheses.")
    return sorted(hypotheses, key=lambda item: int(item["rank"]))


def generate_hypotheses(
    parsed_error: dict[str, object],
    retrieved_incidents: list[dict[str, object]],
    recent_commits: list[dict[str, object]],
) -> list[dict[str, object]]:
    client = get_anthropic_client()
    if client is None:
        return _fallback_hypotheses()

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=700,
            system="You produce strictly valid XML for incident root-cause analysis.",
            messages=[{"role": "user", "content": _hypothesis_prompt(
                parsed_error, retrieved_incidents, recent_commits
            )}],
        )
        return _parse_hypotheses(_response_text(response))
    except (anthropic.APIError, ElementTree.ParseError, TypeError, ValueError):
        return _fallback_hypotheses()


def _report_prompt(
    parsed_error: dict[str, object],
    top_hypothesis: dict[str, object],
    hypotheses: list[dict[str, object]],
) -> str:
    return (
        "Write a concise production incident report in Markdown. Include a title, "
        "timeline summary, the evidence-based top root cause, estimated impact, "
        "immediate remediation, and permanent fix recommendation. Do not invent "
        "facts that are absent from the context.\n\n"
        f"Parsed error:\n{json.dumps(parsed_error, indent=2, default=str)}\n\n"
        f"Top hypothesis:\n{json.dumps(top_hypothesis, indent=2, default=str)}\n\n"
        f"All hypotheses:\n{json.dumps(hypotheses, indent=2, default=str)}"
    )


def _fallback_report(top_hypothesis: dict[str, object]) -> str:
    cause = top_hypothesis.get("cause", "No root cause available.")
    fix = top_hypothesis.get("fix", "Retry after the Claude API becomes available.")
    return (
        "# Incident Investigation\n\n"
        "## Root cause\n"
        f"{cause}\n\n"
        "## Immediate remediation\n"
        f"{fix}\n\n"
        "> Claude API unavailable; report generation was not completed."
    )


def generate_report(
    parsed_error: dict[str, object],
    top_hypothesis: dict[str, object],
    hypotheses: list[dict[str, object]],
) -> str:
    client = get_anthropic_client()
    if client is None:
        return _fallback_report(top_hypothesis)

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=700,
            system="You write factual Markdown production incident reports.",
            messages=[{"role": "user", "content": _report_prompt(
                parsed_error, top_hypothesis, hypotheses
            )}],
        )
        return _response_text(response)
    except (anthropic.APIError, TypeError, ValueError):
        return _fallback_report(top_hypothesis)
