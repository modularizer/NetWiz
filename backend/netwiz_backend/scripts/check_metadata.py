#!/usr/bin/env python3
"""
Check metadata script wrapper

This script runs the sync_metadata script with --check flag
"""

import sys

from .sync_metadata import main

if __name__ == "__main__":
    # Add --check argument
    sys.argv.append("--check")
    main()
