#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
#
# Filename: globals.py
# Project: Shared Library
# Description: Contains reusable global settings and constants.
# Maintainer: Cloud Box 9 Inc.
# Last Modified Date: 2025-10-22
# -----------------------------------------------------------------------------

import os
from datetime import datetime

# -----------------------------------------------------------------------------
# GLOBAL PATHS
# -----------------------------------------------------------------------------
ROOT_DIR = os.path.expanduser("~/Documents/script")
LOG_DIR = os.path.expanduser("~/Documents/log")
TEMP_DIR = os.path.join(ROOT_DIR, "temp")

# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------
def get_timestamp():
    """Return formatted current timestamp."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def print_banner(title: str):
    """Prints a standard header banner."""
    # Import colors locally to avoid circular import
    from CB9Lib.colors import BOLD, CYAN, RESET
    print(f"{BOLD}{CYAN}{'-'*60}")
    print(f"{title.center(60)}")
    print(f"{'-'*60}{RESET}")

# -----------------------------------------------------------------------------
# DEFAULT SETTINGS
# -----------------------------------------------------------------------------
SETTINGS = {
    "project": "SharedLibrary",
    "version": "1.2",
    "log_folder": LOG_DIR,
    "temp_folder": TEMP_DIR
}