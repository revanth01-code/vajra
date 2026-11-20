from typing import Any

from src.services.github_service import GitHubServiceError, get_recent_commits


def change_correlator(state: dict[str, Any]) -> dict[str, Any]:
    repo_url = state.get("repo_url")
    if not repo_url:
        return {
            "recent_commits": [],
            "warnings": [*state.get("warnings", []), "No GitHub repository URL was provided."],
        }

    parsed_error = state.get("parsed_error", {})
    try:
        commits = get_recent_commits(
            repo_url=repo_url,
            error_message=parsed_error.get("error_message", ""),
            file_paths=parsed_error.get("file_paths", []),
        )
        return {"recent_commits": commits}
    except GitHubServiceError as error:
        return {
            "recent_commits": [],
            "warnings": [*state.get("warnings", []), str(error)],
        }
