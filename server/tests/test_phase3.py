import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agents.change_correlator import change_correlator
from src.agents.pipeline import build_retrieval_pipeline
from src.services.github_service import GitHubServiceError


def test_change_correlator_warns_without_repository():
    result = change_correlator({"warnings": []})

    assert result["recent_commits"] == []
    assert "No GitHub repository URL was provided." in result["warnings"]


def test_change_correlator_warns_when_github_fails():
    with patch(
        "src.agents.change_correlator.get_recent_commits",
        side_effect=GitHubServiceError("GitHub could not be reached."),
    ):
        result = change_correlator(
            {
                "repo_url": "https://github.com/example/project",
                "parsed_error": {"error_message": "failure", "file_paths": []},
            }
        )

    assert result["recent_commits"] == []
    assert result["warnings"] == ["GitHub could not be reached."]


def test_retrieval_pipeline_wires_three_nodes():
    with patch(
        "src.agents.history_retriever.retrieve_similar_incidents",
        return_value=[],
    ), patch(
        "src.agents.change_correlator.get_recent_commits",
        return_value=[],
    ):
        result = build_retrieval_pipeline().invoke(
            {
                "raw_input": "service=checkout TypeError in src/checkout.js:10",
                "repo_url": "https://github.com/example/project",
            }
        )

    assert result["parsed_error"]["service"] == "checkout"
    assert result["retrieved_incidents"] == []
    assert result["recent_commits"] == []
