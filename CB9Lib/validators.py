#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
#
# Filename: validators.py
# Project: Shared Library
# Version: 1.3
# Description: Input validation utilities for Cloud Box 9 projects.
# Maintainer: Cloud Box 9 Inc.
# Last Modified Date: 2025-10-25
# -----------------------------------------------------------------------------
# Function List:
# -----------------------------------------------------------------------------
# is_valid_email(email: str) -> bool
#     Validate email address format
#
# is_valid_number(value: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool
#     Validate number and optional range
#
# is_valid_integer(value: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> bool
#     Validate integer and optional range
#
# is_valid_path(path: str, must_exist: bool = False, must_be_file: bool = False, must_be_dir: bool = False) -> bool
#     Validate file/directory path
#
# is_valid_ip(ip: str, version: int = 4) -> bool
#     Validate IP address (IPv4 or IPv6)
#
# is_valid_hostname(hostname: str) -> bool
#     Validate hostname format
#
# is_valid_port(port: str) -> bool
#     Validate port number (1-65535)
#
# validate_input(prompt: str, validator: Callable[[str], bool], error_msg: str = "Invalid input. Please try again.", max_attempts: int = 3) -> Optional[str]
#     Prompt for input with validation
#
# validate_choice(prompt: str, valid_choices: list, case_sensitive: bool = False) -> Optional[str]
#     Prompt for input from a list of valid choices
# -----------------------------------------------------------------------------

import re
from pathlib import Path
from typing import Optional, Callable


def is_valid_email(email: str) -> bool:
    """
    Validate email address format.

    Example:
        >>> is_valid_email("user@example.com")  # True
        >>> is_valid_email("invalid.email")      # False
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_number(value: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
    """
    Validate number and optional range.

    Example:
        >>> is_valid_number("42", min_val=0, max_val=100)  # True
        >>> is_valid_number("150", min_val=0, max_val=100)  # False
    """
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            return False
        if max_val is not None and num > max_val:
            return False
        return True
    except ValueError:
        return False


def is_valid_integer(value: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> bool:
    """
    Validate integer and optional range.

    Example:
        >>> is_valid_integer("42", min_val=0, max_val=100)  # True
        >>> is_valid_integer("3.14", min_val=0, max_val=100)  # False
    """
    try:
        num = int(value)
        if min_val is not None and num < min_val:
            return False
        if max_val is not None and num > max_val:
            return False
        return True
    except ValueError:
        return False


def is_valid_path(path: str, must_exist: bool = False, must_be_file: bool = False, must_be_dir: bool = False) -> bool:
    """
    Validate file/directory path.

    Args:
        path: Path to validate
        must_exist: Path must exist
        must_be_file: Path must be a file
        must_be_dir: Path must be a directory

    Example:
        >>> is_valid_path("/tmp/backup.tar", must_exist=True, must_be_file=True)
    """
    p = Path(path)

    if must_exist and not p.exists():
        return False

    if must_be_file and (not p.exists() or not p.is_file()):
        return False

    if must_be_dir and (not p.exists() or not p.is_dir()):
        return False

    return True


def is_valid_ip(ip: str, version: int = 4) -> bool:
    """
    Validate IP address (IPv4 or IPv6).

    Example:
        >>> is_valid_ip("192.168.1.1")     # True
        >>> is_valid_ip("999.999.999.999") # False
    """
    if version == 4:
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, ip))
    elif version == 6:
        # Simplified IPv6 validation
        pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        return bool(re.match(pattern, ip))
    return False


def is_valid_hostname(hostname: str) -> bool:
    """
    Validate hostname format.

    Example:
        >>> is_valid_hostname("server.example.com")  # True
    """
    if len(hostname) > 255:
        return False

    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
    return bool(re.match(pattern, hostname))


def is_valid_port(port: str) -> bool:
    """
    Validate port number (1-65535).

    Example:
        >>> is_valid_port("3306")  # True
        >>> is_valid_port("99999") # False
    """
    return is_valid_integer(port, min_val=1, max_val=65535)


def validate_input(prompt: str, validator: Callable[[str], bool],
                  error_msg: str = "Invalid input. Please try again.",
                  max_attempts: int = 3) -> Optional[str]:
    """
    Prompt for input with validation.

    Args:
        prompt: Input prompt text
        validator: Function that returns True if input is valid
        error_msg: Error message for invalid input
        max_attempts: Maximum attempts (0 = unlimited)

    Returns:
        Valid input string, or None if max attempts exceeded

    Example:
        >>> email = validate_input(
        >>>     "Enter email:",
        >>>     is_valid_email,
        >>>     "Invalid email format"
        >>> )
    """
    from CB9Lib.colors import color_text, RED

    attempts = 0
    while max_attempts == 0 or attempts < max_attempts:
        user_input = input(f"{prompt} ").strip()

        if validator(user_input):
            return user_input

        print(color_text(error_msg, fg=RED))
        attempts += 1

    return None


def validate_choice(prompt: str, valid_choices: list, case_sensitive: bool = False) -> Optional[str]:
    """
    Prompt for input from a list of valid choices.

    Example:
        >>> env = validate_choice("Environment (dev/prod):", ["dev", "prod"])
    """
    def validator(value):
        if case_sensitive:
            return value in valid_choices
        else:
            return value.lower() in [c.lower() for c in valid_choices]

    choices_str = "/".join(valid_choices)
    error = f"Please enter one of: {choices_str}"

    result = validate_input(f"{prompt} ({choices_str})", validator, error)

    if result and not case_sensitive:
        # Return the properly-cased version
        for choice in valid_choices:
            if choice.lower() == result.lower():
                return choice

    return result
