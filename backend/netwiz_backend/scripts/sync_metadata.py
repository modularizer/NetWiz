#!/usr/bin/env python3
"""
Sync metadata from __init__.py to pyproject.toml and requirements.txt to dependencies

This script reads metadata from the __init__.py file and requirements from requirements.txt,
then updates the pyproject.toml file to keep them in sync. Both __init__.py and requirements.txt
are considered the source of truth.

Usage:
    python scripts/sync_metadata.py
    python scripts/sync_metadata.py --dry-run
    python scripts/sync_metadata.py --check
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import Any

import tomli_w
import tomllib

try:
    from netwiz_backend import *  # noqa: F403
except ImportError as e:
    print(f"Error importing from netwiz_backend: {e}")
    sys.exit(1)


backend_dir = Path(__file__).parent.parent.parent


def parse_requirements_txt(file_path: Path) -> tuple[list[str], list[str]]:
    """
    Parse requirements.txt file and extract dependencies.

    Args:
        file_path: Path to the requirements.txt file

    Returns:
        Tuple of (dependencies, dev_dependencies)
    """
    dependencies = []
    dev_dependencies = []

    if not file_path.exists():
        return dependencies, dev_dependencies

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Skip include directives
            if line.startswith("-r ") or line.startswith("--"):
                continue
            dependencies.append(line)

    return dependencies, dev_dependencies


def parse_requirements_dev_txt(file_path: Path) -> list[str]:
    """
    Parse requirements-dev.txt file and extract dev dependencies.

    Args:
        file_path: Path to the requirements-dev.txt file

    Returns:
        List of dev dependency strings
    """
    dev_dependencies = []

    if not file_path.exists():
        return dev_dependencies

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Skip include directives
            if line.startswith("-r ") or line.startswith("--"):
                continue
            dev_dependencies.append(line)

    return dev_dependencies


def parse_init_py(file_path: Path) -> dict[str, Any]:
    """
    Parse __init__.py file and extract metadata from dunder variables.

    Args:
        file_path: Path to the __init__.py file

    Returns:
        Dictionary containing the extracted metadata
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Parse the AST to extract string literals
    tree = ast.parse(content)

    metadata = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith("__"):
                    if isinstance(node.value, ast.Constant) and isinstance(
                        node.value.value, str
                    ):
                        metadata[target.id] = node.value.value
                    elif isinstance(node.value, ast.Str):  # Python < 3.8 compatibility
                        metadata[target.id] = node.value.s

    return metadata


def load_pyproject_toml(file_path: Path) -> dict[str, Any]:
    """
    Load and parse pyproject.toml file.

    Args:
        file_path: Path to the pyproject.toml file

    Returns:
        Dictionary containing the parsed TOML data
    """
    with open(file_path, "rb") as f:
        return tomllib.load(f)


def update_pyproject_metadata(
    pyproject_data: dict[str, Any],
    metadata: dict[str, Any],
    dependencies: list[str],
    dev_dependencies: list[str],
) -> dict[str, Any]:
    """
    Update pyproject.toml data with metadata from __init__.py and dependencies from requirements files.

    Args:
        pyproject_data: Current pyproject.toml data
        metadata: Metadata from __init__.py
        dependencies: Dependencies from requirements.txt
        dev_dependencies: Dev dependencies from requirements-dev.txt

    Returns:
        Updated pyproject.toml data
    """
    # Ensure project section exists
    if "project" not in pyproject_data:
        pyproject_data["project"] = {}

    # Map __init__.py dunders to pyproject.toml fields
    # (This mapping is used for reference but not currently implemented)

    # Update basic fields
    if "__version__" in metadata:
        pyproject_data["project"]["version"] = metadata["__version__"]

    if "__description__" in metadata:
        pyproject_data["project"]["description"] = metadata["__description__"]

    # Handle license
    if "__license__" in metadata:
        pyproject_data["project"]["license"] = {"text": metadata["__license__"]}

    # Handle authors (convert to list format)
    if "__author__" in metadata and "__email__" in metadata:
        pyproject_data["project"]["authors"] = [
            {"name": metadata["__author__"], "email": metadata["__email__"]}
        ]
        pyproject_data["project"]["maintainers"] = [
            {"name": metadata["__author__"], "email": metadata["__email__"]}
        ]

    # Handle URLs
    if "__url__" in metadata:
        if "urls" not in pyproject_data["project"]:
            pyproject_data["project"]["urls"] = {}

        # Extract repository URL and create standard URLs
        repo_url = metadata["__url__"]
        if repo_url.startswith("https://github.com/"):
            pyproject_data["project"]["urls"]["Homepage"] = repo_url
            pyproject_data["project"]["urls"]["Repository"] = repo_url
            pyproject_data["project"]["urls"]["Issues"] = f"{repo_url}/issues"
            pyproject_data["project"]["urls"]["Documentation"] = f"{repo_url}#readme"
            pyproject_data["project"]["urls"][
                "Changelog"
            ] = f"{repo_url}/blob/main/CHANGELOG.md"

    # Handle development status classifier
    if "__status__" in metadata:
        status = metadata["__status__"].lower()
        if "classifiers" not in pyproject_data["project"]:
            pyproject_data["project"]["classifiers"] = []

        # Map status to appropriate classifier
        status_mapping = {
            "development": "Development Status :: 3 - Alpha",
            "alpha": "Development Status :: 3 - Alpha",
            "beta": "Development Status :: 4 - Beta",
            "stable": "Development Status :: 5 - Production/Stable",
            "production": "Development Status :: 5 - Production/Stable",
        }

        if status in status_mapping:
            classifier = status_mapping[status]
            # Remove existing development status classifiers
            pyproject_data["project"]["classifiers"] = [
                c
                for c in pyproject_data["project"]["classifiers"]
                if not c.startswith("Development Status ::")
            ]
            # Add new classifier at the beginning
            pyproject_data["project"]["classifiers"].insert(0, classifier)

    # Update dependencies from requirements.txt
    if dependencies:
        pyproject_data["project"]["dependencies"] = dependencies
        print(
            f"Updated dependencies: {len(dependencies)} packages from requirements.txt"
        )

    # Update dev dependencies from requirements-dev.txt
    if dev_dependencies:
        if "optional-dependencies" not in pyproject_data["project"]:
            pyproject_data["project"]["optional-dependencies"] = {}
        pyproject_data["project"]["optional-dependencies"]["dev"] = dev_dependencies
        print(
            f"Updated dev dependencies: {len(dev_dependencies)} packages from requirements-dev.txt"
        )

    return pyproject_data


def write_pyproject_toml(file_path: Path, data: dict[str, Any]) -> None:
    """
    Write pyproject.toml file with updated data.

    Args:
        file_path: Path to the pyproject.toml file
        data: Data to write
    """
    with open(file_path, "wb") as f:
        tomli_w.dump(data, f)


def check_differences(
    init_metadata: dict[str, Any],
    pyproject_data: dict[str, Any],
    dependencies: list[str],
    dev_dependencies: list[str],
) -> bool:
    """
    Check if there are differences between source files and pyproject.toml.

    Args:
        init_metadata: Metadata from __init__.py
        pyproject_data: Data from pyproject.toml
        dependencies: Dependencies from requirements.txt
        dev_dependencies: Dev dependencies from requirements-dev.txt

    Returns:
        True if there are differences, False otherwise
    """
    differences = []

    # Check version
    if "__version__" in init_metadata:
        pyproject_version = pyproject_data.get("project", {}).get("version", "")
        if init_metadata["__version__"] != pyproject_version:
            differences.append(
                f"Version: {init_metadata['__version__']} != {pyproject_version}"
            )

    # Check description
    if "__description__" in init_metadata:
        pyproject_desc = pyproject_data.get("project", {}).get("description", "")
        if init_metadata["__description__"] != pyproject_desc:
            differences.append(
                f"Description: {init_metadata['__description__']} != {pyproject_desc}"
            )

    # Check author
    if "__author__" in init_metadata:
        pyproject_authors = pyproject_data.get("project", {}).get("authors", [])
        if pyproject_authors and isinstance(pyproject_authors[0], dict):
            pyproject_author = pyproject_authors[0].get("name", "")
            if init_metadata["__author__"] != pyproject_author:
                differences.append(
                    f"Author: {init_metadata['__author__']} != {pyproject_author}"
                )

    # Check dependencies
    pyproject_deps = pyproject_data.get("project", {}).get("dependencies", [])
    if set(dependencies) != set(pyproject_deps):
        differences.append(
            f"Dependencies: {len(dependencies)} in requirements.txt vs {len(pyproject_deps)} in pyproject.toml"
        )

    # Check dev dependencies
    pyproject_dev_deps = (
        pyproject_data.get("project", {})
        .get("optional-dependencies", {})
        .get("dev", [])
    )
    if set(dev_dependencies) != set(pyproject_dev_deps):
        differences.append(
            f"Dev Dependencies: {len(dev_dependencies)} in requirements-dev.txt vs {len(pyproject_dev_deps)} in pyproject.toml"
        )

    if differences:
        print("Found differences:")
        for diff in differences:
            print(f"  - {diff}")
        return True

    print("No differences found. Files are in sync.")
    return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Sync metadata from __init__.py to pyproject.toml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/sync_metadata.py          # Sync metadata
  python scripts/sync_metadata.py --dry-run  # Show what would be changed
  python scripts/sync_metadata.py --check    # Check for differences only
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for differences without making changes",
    )

    parser.add_argument(
        "--init-file",
        default="__init__.py",
        help="Path to __init__.py file (default: __init__.py)",
    )

    parser.add_argument(
        "--pyproject-file",
        default="pyproject.toml",
        help="Path to pyproject.toml file (default: pyproject.toml)",
    )

    parser.add_argument(
        "--requirements-file",
        default="requirements.txt",
        help="Path to requirements.txt file (default: requirements.txt)",
    )

    parser.add_argument(
        "--requirements-dev-file",
        default="requirements-dev.txt",
        help="Path to requirements-dev.txt file (default: requirements-dev.txt)",
    )

    args = parser.parse_args()

    # Get file paths
    init_file = backend_dir / "netwiz_backend" / args.init_file
    pyproject_file = backend_dir / args.pyproject_file
    requirements_file = backend_dir / args.requirements_file
    requirements_dev_file = backend_dir / args.requirements_dev_file

    # Check if files exist
    if not init_file.exists():
        print(f"Error: {init_file} not found")
        sys.exit(1)

    if not pyproject_file.exists():
        print(f"Error: {pyproject_file} not found")
        sys.exit(1)

    try:
        # Parse __init__.py
        print(f"Reading metadata from {init_file}")
        init_metadata = parse_init_py(init_file)

        # Parse requirements.txt
        print(f"Reading dependencies from {requirements_file}")
        dependencies, _ = parse_requirements_txt(requirements_file)

        # Parse requirements-dev.txt
        print(f"Reading dev dependencies from {requirements_dev_file}")
        dev_dependencies = parse_requirements_dev_txt(requirements_dev_file)

        # Load pyproject.toml
        print(f"Reading {pyproject_file}")
        pyproject_data = load_pyproject_toml(pyproject_file)

        if args.check:
            # Just check for differences
            has_differences = check_differences(
                init_metadata, pyproject_data, dependencies, dev_dependencies
            )
            sys.exit(1 if has_differences else 0)

        # Check for differences
        has_differences = check_differences(
            init_metadata, pyproject_data, dependencies, dev_dependencies
        )

        if not has_differences:
            print("Files are already in sync. No changes needed.")
            sys.exit(0)

        if args.dry_run:
            print("\nDry run mode - would make the following changes:")
            updated_data = update_pyproject_metadata(
                pyproject_data.copy(), init_metadata, dependencies, dev_dependencies
            )

            # Show key changes
            print(
                f"  Version: {pyproject_data.get('project', {}).get('version', 'N/A')} -> {updated_data.get('project', {}).get('version', 'N/A')}"
            )
            print(
                f"  Description: {pyproject_data.get('project', {}).get('description', 'N/A')} -> {updated_data.get('project', {}).get('description', 'N/A')}"
            )
            print(
                f"  Author: {pyproject_data.get('project', {}).get('authors', [{}])[0].get('name', 'N/A')} -> {updated_data.get('project', {}).get('authors', [{}])[0].get('name', 'N/A')}"
            )
            print(
                f"  Dependencies: {len(pyproject_data.get('project', {}).get('dependencies', []))} -> {len(dependencies)}"
            )
            print(
                f"  Dev Dependencies: {len(pyproject_data.get('project', {}).get('optional-dependencies', {}).get('dev', []))} -> {len(dev_dependencies)}"
            )
            sys.exit(0)

        # Update pyproject.toml
        print("Updating pyproject.toml...")
        updated_data = update_pyproject_metadata(
            pyproject_data, init_metadata, dependencies, dev_dependencies
        )
        write_pyproject_toml(pyproject_file, updated_data)

        print(
            "✅ Successfully synced metadata from __init__.py and dependencies from requirements.txt to pyproject.toml"
        )

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
