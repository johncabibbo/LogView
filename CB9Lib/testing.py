#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
#
# Filename: testing.py
# Project: Shared Library
# Version: 1.3
# Description: Testing framework utilities for Cloud Box 9 projects.
# Maintainer: Cloud Box 9 Inc.
# Last Modified Date: 2025-10-25
# -----------------------------------------------------------------------------
# Function List:
# -----------------------------------------------------------------------------
# assert_equals(actual, expected, msg: str = "")
#     Simple assertion for equality testing
#
# assert_true(condition: bool, msg: str = "")
#     Assert that condition is True
#
# assert_false(condition: bool, msg: str = "")
#     Assert that condition is False
#
# test_suite(name: str)
#     Context manager for grouping tests
#
# mock_input(values: list)
#     Context manager to mock user input for testing
#
# capture_output()
#     Context manager to capture print statements
# -----------------------------------------------------------------------------

import sys
from io import StringIO
from contextlib import contextmanager
from typing import Any, List


# Test statistics
_test_stats = {
    'passed': 0,
    'failed': 0,
    'total': 0
}


def assert_equals(actual: Any, expected: Any, msg: str = "") -> bool:
    """
    Simple assertion for equality testing.

    Args:
        actual: The actual value
        expected: The expected value
        msg: Optional message to display

    Returns:
        True if assertion passes, False otherwise

    Example:
        >>> assert_equals(2 + 2, 4, "Addition test")
        >>> assert_equals(len([1,2,3]), 3, "List length test")
    """
    from CB9Lib.colors import color_text, GREEN, RED, BOLD

    _test_stats['total'] += 1

    if actual == expected:
        _test_stats['passed'] += 1
        status = color_text("✓ PASS", fg=GREEN, style=BOLD)
        if msg:
            print(f"{status} - {msg}")
        else:
            print(f"{status} - Expected {expected}, got {actual}")
        return True
    else:
        _test_stats['failed'] += 1
        status = color_text("✗ FAIL", fg=RED, style=BOLD)
        if msg:
            print(f"{status} - {msg}")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")
        return False


def assert_true(condition: bool, msg: str = "") -> bool:
    """
    Assert that condition is True.

    Args:
        condition: Boolean condition to test
        msg: Optional message to display

    Returns:
        True if assertion passes, False otherwise

    Example:
        >>> assert_true(5 > 3, "5 is greater than 3")
    """
    from CB9Lib.colors import color_text, GREEN, RED, BOLD

    _test_stats['total'] += 1

    if condition:
        _test_stats['passed'] += 1
        status = color_text("✓ PASS", fg=GREEN, style=BOLD)
        print(f"{status} - {msg if msg else 'Condition is True'}")
        return True
    else:
        _test_stats['failed'] += 1
        status = color_text("✗ FAIL", fg=RED, style=BOLD)
        print(f"{status} - {msg if msg else 'Condition is False'}")
        return False


def assert_false(condition: bool, msg: str = "") -> bool:
    """
    Assert that condition is False.

    Args:
        condition: Boolean condition to test
        msg: Optional message to display

    Returns:
        True if assertion passes, False otherwise

    Example:
        >>> assert_false(5 < 3, "5 is not less than 3")
    """
    return assert_true(not condition, msg)


@contextmanager
def test_suite(name: str):
    """
    Context manager for grouping tests.

    Args:
        name: Name of the test suite

    Example:
        >>> with test_suite("Math Tests"):
        >>>     assert_equals(2 + 2, 4)
        >>>     assert_equals(5 * 5, 25)
    """
    from CB9Lib.colors import color_text, CYAN, GREEN, RED, BOLD

    print(f"\n{color_text('═' * 60, fg=CYAN)}")
    print(color_text(f"Test Suite: {name}", fg=CYAN, style=BOLD))
    print(f"{color_text('═' * 60, fg=CYAN)}\n")

    # Reset stats for this suite
    _test_stats['passed'] = 0
    _test_stats['failed'] = 0
    _test_stats['total'] = 0

    try:
        yield
    finally:
        # Print summary
        print(f"\n{color_text('─' * 60, fg=CYAN)}")
        print(color_text("Test Results:", fg=CYAN, style=BOLD))
        print(f"  Total:  {_test_stats['total']}")
        print(f"  {color_text('Passed:', fg=GREEN)} {_test_stats['passed']}")
        print(f"  {color_text('Failed:', fg=RED)} {_test_stats['failed']}")

        if _test_stats['failed'] == 0 and _test_stats['total'] > 0:
            print(color_text("\n✓ All tests passed!", fg=GREEN, style=BOLD))
        elif _test_stats['failed'] > 0:
            print(color_text(f"\n✗ {_test_stats['failed']} test(s) failed", fg=RED, style=BOLD))

        print(f"{color_text('═' * 60, fg=CYAN)}\n")


@contextmanager
def mock_input(values: List[str]):
    """
    Context manager to mock user input for testing.

    Args:
        values: List of input values to return in sequence

    Example:
        >>> with mock_input(["John", "25"]):
        >>>     name = input("Name: ")
        >>>     age = input("Age: ")
        >>> assert_equals(name, "John")
    """
    original_input = __builtins__.input
    iterator = iter(values)

    def mock_input_func(prompt=""):
        try:
            return next(iterator)
        except StopIteration:
            raise EOFError("No more mocked inputs available")

    __builtins__.input = mock_input_func

    try:
        yield
    finally:
        __builtins__.input = original_input


@contextmanager
def capture_output():
    """
    Context manager to capture print statements.

    Returns:
        StringIO object containing captured output

    Example:
        >>> with capture_output() as output:
        >>>     print("Hello, World!")
        >>> assert_equals(output.getvalue(), "Hello, World!\\n")
    """
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    try:
        yield captured_output
    finally:
        sys.stdout = old_stdout


def get_test_stats() -> dict:
    """
    Get current test statistics.

    Returns:
        Dictionary with test statistics (passed, failed, total)
    """
    return _test_stats.copy()


def reset_test_stats() -> None:
    """Reset test statistics to zero."""
    _test_stats['passed'] = 0
    _test_stats['failed'] = 0
    _test_stats['total'] = 0
