import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agents.pipeline import build_pipeline
from src.services.anthropic_service import (
    generate_hypotheses,
    generate_report,
)


HYPOTHESIS_XML = """
<hypotheses>
  <hypothesis rank="1" confidence="0.82">
    <cause>Connection pool exhaustion</cause>
    <evidence>Database timeout and pool wait metrics align.</evidence>
    <fix>Increase pool capacity after reducing connection hold time.</fix>
  </hypothesis>
  <hypothesis rank="2" confidence="0.55">
    <cause>Slow database query</cause>
    <evidence>The error occurs during a database request.</evidence>
    <fix>Inspect and optimize the slow query.</fix>
  </hypothesis>
  <hypothesis rank="3" confidence="0.21">
    <cause>Recent deployment regression</cause>
    <evidence>A deployment occurred before the incident.</evidence>
    <fix>Compare the release with the previous version.</fix>
  </hypothesis>
</hypotheses>
"""


def test_hypothesis_api_response_is_parsed():
    state = {
        "parsed_error": {},
        "retrieved_incidents": [],
        "recent_commits": [],
    }
    with patch("src.services.anthropic_service._call_groq", return_value=HYPOTHESIS_XML):
        hypotheses = generate_hypotheses(state)

    assert len(hypotheses) == 3
    assert hypotheses[0]["rank"] == 1
    assert hypotheses[0]["confidence"] == 0.82
    assert hypotheses[1]["cause"] == "Slow database query"


def test_api_failure_returns_fallbacks():
    state = {"parsed_error": {}, "retrieved_incidents": [], "recent_commits": []}
    with patch(
        "src.services.anthropic_service._call_groq",
        side_effect=RuntimeError("missing key"),
    ):
        hypotheses = generate_hypotheses(state)
        report = generate_report({"parsed_error": {}, "hypotheses": hypotheses})

    assert len(hypotheses) == 1
    assert hypotheses[0]["confidence"] == 0.0
    assert "Groq API unavailable" in report


def test_full_pipeline_passes_state_through_five_nodes():
    with patch(
        "src.agents.history_retriever.retrieve_similar_incidents",
        return_value=[],
    ), patch(
        "src.agents.change_correlator.get_recent_commits",
        return_value=[],
    ), patch(
        "src.agents.hypothesis_agent.generate_hypotheses",
        return_value=[{
            "rank": 1,
            "confidence": 0.8,
            "cause": "Test cause",
            "evidence": "Test evidence",
            "fix": "Test fix",
        }],
    ), patch(
        "src.agents.report_writer.generate_report",
        return_value="# Test report",
    ):
        result = build_pipeline().invoke(
            {
                "raw_input": "service=checkout DatabaseTimeoutError in src/db.py:10",
                "repo_url": "https://github.com/example/project",
            }
        )

    assert result["hypotheses"][0]["cause"] == "Test cause"
    assert result["report_markdown"] == "# Test report"
