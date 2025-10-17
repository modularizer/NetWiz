# Backend Scripts

This directory contains utility scripts for maintaining the backend project.

## Scripts

### `sync_metadata.py`

Synchronizes metadata from `__init__.py` to `pyproject.toml` to keep them in sync.
The `__init__.py` file is considered the source of truth for project metadata.

#### Usage

```bash
# Sync metadata (make changes)
python scripts/sync_metadata.py

# Check for differences without making changes
python scripts/sync_metadata.py --check

# Show what would be changed (dry run)
python scripts/sync_metadata.py --dry-run

# Use wrapper script
./scripts/sync
./scripts/sync --check
./scripts/sync --dry-run
```

#### Features

- **Source of Truth**: `__init__.py` is the authoritative source
- **Automatic Mapping**: Maps dunder variables to appropriate pyproject.toml fields
- **Safe Operations**: Dry-run mode to preview changes
- **Difference Detection**: Check mode to see if files are in sync
- **Comprehensive Updates**: Updates version, description, author, license, URLs, and classifiers

#### Mapped Fields

| `__init__.py` | `pyproject.toml` | Description |
|---------------|------------------|-------------|
| `__version__` | `project.version` | Package version |
| `__description__` | `project.description` | Package description |
| `__author__` | `project.authors[0].name` | Author name |
| `__email__` | `project.authors[0].email` | Author email |
| `__license__` | `project.license.text` | License text |
| `__url__` | `project.urls.*` | Repository and related URLs |
| `__status__` | `project.classifiers` | Development status classifier |

#### Examples

**Check if files are in sync:**
```bash
python scripts/sync_metadata.py --check
```

**Preview changes:**
```bash
python scripts/sync_metadata.py --dry-run
```

**Sync metadata:**
```bash
python scripts/sync_metadata.py
```

**Using Makefile:**
```bash
make sync-metadata    # Sync metadata
make check-metadata   # Check for differences
```

## Development Workflow

1. **Update metadata** in `__init__.py`
2. **Run sync script** to update `pyproject.toml`
3. **Commit changes** to both files

This ensures that:
- `__init__.py` remains the single source of truth
- `pyproject.toml` stays in sync automatically
- No manual duplication of metadata
- Consistent versioning across the project

## Dependencies

The sync script requires:
- `tomli-w` for writing TOML files
- `ast` (built-in) for parsing Python files
- `argparse` (built-in) for command-line arguments

Install development dependencies:
```bash
pip install -e .[dev]
```
