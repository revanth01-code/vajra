from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from github import Github
from github.GithubException import GithubException
from requests import RequestException

from src.config.env import settings


class GitHubServiceError(RuntimeError):
    """Raised when the public GitHub commit lookup cannot be completed."""


def _repository_name(repo_url: str) -> str:
    parsed = urlparse(repo_url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "github.com":
        raise GitHubServiceError("GitHub repository URL must point to github.com.")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise GitHubServiceError("GitHub repository URL must include owner and repository.")
    return f"{parts[0]}/{parts[1].removesuffix('.git')}"


def _matches_error_path(filename: str, error_message: str, file_paths: list[str]) -> bool:
    normalized_filename = filename.replace("\\", "/")
    normalized_message = error_message.replace("\\", "/")
    return normalized_filename in normalized_message or any(
        normalized_filename in path.replace("\\", "/")
        or path.replace("\\", "/") in normalized_filename
        for path in file_paths
    )


def get_recent_commits(
    repo_url: str,
    error_message: str,
    file_paths: list[str],
) -> list[dict[str, object]]:
    try:
        github_client = Github(login_or_token=settings.github_token)
        repository = github_client.get_repo(_repository_name(repo_url))
        since = datetime.now(timezone.utc) - timedelta(hours=48)
        commits: list[dict[str, object]] = []

        for commit in repository.get_commits(since=since):
            modified_files = [file.filename for file in commit.files]
            author = commit.author.login if commit.author else commit.commit.author.name
            timestamp = commit.commit.author.date
            commits.append(
                {
                    "sha": commit.sha,
                    "message": commit.commit.message.splitlines()[0],
                    "author": author,
                    "timestamp": timestamp.isoformat() if timestamp else None,
                    "modified_files": modified_files,
                    "suspicious": any(
                        _matches_error_path(filename, error_message, file_paths)
                        for filename in modified_files
                    ),
                }
            )
        return commits
    except (GithubException, RequestException) as error:
        raise GitHubServiceError("GitHub could not be reached.") from error
