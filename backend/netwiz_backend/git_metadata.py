"""
Git metadata utilities for loading build-time git information
"""

import json
import os
import subprocess
from pathlib import Path

from netwiz_backend.system.models import GitMetadata


def _run_git_command(command: list[str], cwd: Path) -> str | None:
    """
    Run a git command and return its output.

    Args:
        command: Git command as a list of strings
        cwd: Working directory to run the command in

    Returns:
        Command output as string, or None if command fails
    """
    try:
        result = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, check=True, timeout=5
        )
        return result.stdout.strip()
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        return None


def _detect_git_metadata() -> GitMetadata | None:
    """
    Detect git metadata by running git commands in the current directory.

    Returns:
        GitMetadata object if git information is available, None otherwise
    """
    try:
        # Find the git repository root
        current_dir = Path(__file__).parent
        git_root = None

        # Walk up the directory tree to find .git directory
        for path in [current_dir, *list(current_dir.parents)]:
            if (path / ".git").exists():
                git_root = path
                break

        if not git_root:
            return None

        # Get git information
        commit_hash = _run_git_command(["git", "rev-parse", "HEAD"], git_root)
        if not commit_hash:
            return None

        commit_short = _run_git_command(
            ["git", "rev-parse", "--short", "HEAD"], git_root
        )
        branch = _run_git_command(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], git_root
        )
        tag = _run_git_command(["git", "describe", "--tags", "--exact-match"], git_root)

        # Get build time (current time)
        from datetime import datetime, timezone

        build_time = datetime.now(timezone.utc).isoformat()

        return GitMetadata(
            commit_hash=commit_hash,
            commit_short=commit_short,
            branch=branch,
            tag=tag if tag else None,
            build_time=build_time,
            build_ref=f"refs/heads/{branch}" if branch else None,
            build_sha=commit_hash,
        )

    except Exception:
        # Silently fail if we can't detect git information
        return None


def load_git_metadata() -> GitMetadata | None:
    """
    Load git metadata from the build-time generated file.

    Returns:
        GitMetadata object if file exists and is valid, None otherwise
    """
    try:
        # Try to find the git metadata file
        current_dir = Path(__file__).parent
        metadata_file = current_dir / "git_metadata.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file) as f:
            data = json.load(f)

        # Only return metadata if we have at least some meaningful data
        if any(data.get(key) for key in ["commit_hash", "commit_short", "branch"]):
            return GitMetadata(**data)

    except (json.JSONDecodeError, FileNotFoundError, Exception):
        # Silently fail if we can't load the metadata
        pass

    return None


def get_git_metadata() -> GitMetadata | None:
    """
    Get git metadata with multiple fallback strategies:
    1. Load from build-time generated file (production builds)
    2. Load from environment variables (CI/CD or manual setup)
    3. Detect from git repository (development from source)

    Returns:
        GitMetadata object if available, None otherwise
    """
    # First try to load from file (production builds)
    metadata = load_git_metadata()
    if metadata:
        return metadata

    # Fallback to environment variables (CI/CD or manual setup)
    commit_hash = os.environ.get("GIT_COMMIT_HASH")
    commit_short = os.environ.get("GIT_COMMIT_SHORT")
    branch = os.environ.get("GIT_BRANCH")

    if commit_hash or commit_short or branch:
        return GitMetadata(
            commit_hash=commit_hash,
            commit_short=commit_short,
            branch=branch,
            tag=os.environ.get("GIT_TAG"),
            build_time=os.environ.get("BUILD_TIME"),
            build_ref=os.environ.get("BUILD_REF"),
            build_sha=os.environ.get("BUILD_SHA"),
        )

    # Final fallback: detect from git repository (development from source)
    return _detect_git_metadata()
