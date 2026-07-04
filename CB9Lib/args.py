#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
#
# Filename: args.py
# Project: Shared Library
# Version: 1.3
# Description: Command-line argument parsing utilities for Cloud Box 9 projects.
# Maintainer: Cloud Box 9 Inc.
# Last Modified Date: 2025-10-25
# -----------------------------------------------------------------------------
# Function List:
# -----------------------------------------------------------------------------
# parse_simple_args(expected_args: List[str] = None) -> Dict[str, Any]
#     Simple argument parser for scripts
#     expected_args: List of expected argument names
#
# CB9ArgParser(name: str, version: str, description: str = "")
#     Enhanced argument parser with CB9Lib styling
#     name: Script/program name
#     version: Version string
#     description: Description text
#
# get_script_name() -> str
#     Get the name of the running script
#
# get_all_args() -> List[str]
#     Get all command-line arguments (excluding script name)
# -----------------------------------------------------------------------------

import argparse
import sys
from typing import Any, Dict, List


def parse_simple_args(expected_args: List[str] = None) -> Dict[str, Any]:
    """
    Simple argument parser for scripts.

    Args:
        expected_args: List of expected argument names

    Returns:
        Dictionary of argument names to values

    Example:
        >>> # Script called as: python script.py db1 db2 --dry-run
        >>> args = parse_simple_args(['database', 'target'])
        >>> # Returns: {'database': 'db1', 'target': 'db2', 'dry_run': True}
    """
    args = {}
    positional = []
    flags = []

    for arg in sys.argv[1:]:
        if arg.startswith('--'):
            flag_name = arg[2:].replace('-', '_')
            flags.append(flag_name)
        elif arg.startswith('-'):
            flag_name = arg[1:]
            flags.append(flag_name)
        else:
            positional.append(arg)

    if expected_args:
        for i, name in enumerate(expected_args):
            if i < len(positional):
                args[name] = positional[i]
            else:
                args[name] = None
    else:
        for i, val in enumerate(positional):
            args[f'arg{i}'] = val

    for flag in flags:
        args[flag] = True

    return args


class CB9ArgParser:
    """
    Enhanced argument parser with CB9Lib styling.

    Example:
        >>> parser = CB9ArgParser("Backup Manager", "v2.0")
        >>> parser.add_argument('database', help='Database name')
        >>> parser.add_argument('--dry-run', action='store_true', help='Test mode')
        >>> parser.add_argument('--verbose', '-v', action='store_true')
        >>> args = parser.parse()
    """

    def __init__(self, name: str, version: str, description: str = ""):
        """
        Initialize argument parser.

        Args:
            name: Script/program name
            version: Version string
            description: Description text
        """
        self.name = name
        self.version = version

        desc = f"{name} {version}"
        if description:
            desc += f"\n{description}"

        self.parser = argparse.ArgumentParser(
            description=desc,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        self.parser.add_argument(
            '--version',
            action='version',
            version=f'{name} {version}'
        )

    def add_argument(self, *args, **kwargs):
        """Add an argument (passes through to argparse)."""
        return self.parser.add_argument(*args, **kwargs)

    def parse(self) -> argparse.Namespace:
        """Parse arguments and return namespace."""
        return self.parser.parse_args()

    def parse_dict(self) -> Dict[str, Any]:
        """Parse arguments and return as dictionary."""
        return vars(self.parser.parse_args())


def get_script_name() -> str:
    """Get the name of the running script."""
    return sys.argv[0]


def get_all_args() -> List[str]:
    """Get all command-line arguments (excluding script name)."""
    return sys.argv[1:]
