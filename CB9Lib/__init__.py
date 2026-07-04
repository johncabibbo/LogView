#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
#
# Filename: __init__.py
# Project: CB9Lib Library
# Version: 1.3
# Maintainer: Cloud Box 9 Inc
# Last Modified Date: 2025-10-25
# -----------------------------------------------------------------------------
# Description:
#   Initializes the CB9Lib package namespace and imports core modules.
# -----------------------------------------------------------------------------
# Changelog v1.3:
#   • Added interactive UI functions (menu, select_list, progress_bar, confirm)
#   • Added table formatting (print_table, table_format, print_dict_table)
#   • Added advanced logging (Logger class, get_logger, log levels)
#   • Added command-line parsing module (args)
#   • Added input validation module (validators)
#   • Added testing framework module (testing)
#   • Added color themes (THEME_*, apply_theme, get_theme_color)
#   • Added advanced file utilities (copy_file, move_file, search_files, get_file_info)
# -----------------------------------------------------------------------------

# Import modules
from . import globals
from . import colors
from . import func
from . import imgvid
from . import args
from . import validators
from . import testing
from . import job_logger

# Import commonly used items for convenience
from .colors import (
    # Color functions
    color_text, banner, enable_colors, test_colors,
    # Colors
    RED, GREEN, YELLOW, BLUE, CYAN, MAGENTA, WHITE, BLACK,
    BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_BLUE,
    BRIGHT_CYAN, BRIGHT_MAGENTA, BRIGHT_WHITE, BRIGHT_BLACK,
    BOLD, DIM, ITALIC, UNDERLINE, RESET,
    # Themes (v1.3)
    THEME_DEFAULT, THEME_OCEAN, THEME_FOREST, THEME_SUNSET, THEME_MONO,
    apply_theme, get_theme_color, get_current_theme, list_themes
)

from .func import (
    # Core utilities
    get_width, clear_screen, pause, sleep,
    # JSON helpers
    load_json_config, save_json_config,
    # UI elements
    header, footerMenu, exit_screen,
    # Sound utilities
    get_project_sound, play_sound,
    # File utilities
    file_exists, folder_exists, ensure_folder, list_files, remove_files,
    # Logging (original)
    write_log, log_header, log_footer, logRotate,
    # Testing
    test_ui,
    # Interactive UI (v1.3)
    menu, select_list, progress_bar, confirm,
    # Table formatting (v1.3)
    print_table, table_format, print_dict_table,
    # Advanced logging (v1.3)
    Logger, get_logger, DEBUG, INFO, WARNING, ERROR, CRITICAL,
    # Advanced file utilities (v1.3)
    copy_file, move_file, search_files, get_file_info,
    # Master execution logging (v1.4)
    scriptStart, scriptEnd, MASTER_EXEC_LOG
)

from .globals import (
    ROOT_DIR, LOG_DIR, TEMP_DIR,
    get_timestamp, print_banner, SETTINGS
)

from .imgvid import (
    create_thumb_resize, list_thumbnails
)

from .args import (
    parse_simple_args, CB9ArgParser, get_script_name, get_all_args
)

from .validators import (
    is_valid_email, is_valid_number, is_valid_integer, is_valid_path,
    is_valid_ip, is_valid_hostname, is_valid_port,
    validate_input, validate_choice
)

from .testing import (
    assert_equals, assert_true, assert_false,
    test_suite, mock_input, capture_output,
    get_test_stats, reset_test_stats
)

from .job_logger import JobLogger

__version__ = "1.4.0"

__all__ = [
    # Modules
    "globals", "colors", "func", "imgvid", "args", "validators", "testing",

    # Color functions
    "color_text", "banner", "enable_colors", "test_colors",

    # Colors
    "RED", "GREEN", "YELLOW", "BLUE", "CYAN", "MAGENTA", "WHITE", "BLACK",
    "BRIGHT_RED", "BRIGHT_GREEN", "BRIGHT_YELLOW", "BRIGHT_BLUE",
    "BRIGHT_CYAN", "BRIGHT_MAGENTA", "BRIGHT_WHITE", "BRIGHT_BLACK",
    "BOLD", "DIM", "ITALIC", "UNDERLINE", "RESET",

    # Color themes (v1.3)
    "THEME_DEFAULT", "THEME_OCEAN", "THEME_FOREST", "THEME_SUNSET", "THEME_MONO",
    "apply_theme", "get_theme_color", "get_current_theme", "list_themes",

    # Core utility functions
    "get_width", "clear_screen", "pause", "sleep",
    "load_json_config", "save_json_config",
    "header", "footerMenu", "exit_screen",
    "get_project_sound", "play_sound",

    # File utilities
    "file_exists", "folder_exists", "ensure_folder", "list_files", "remove_files",

    # Logging (original)
    "write_log", "log_header", "log_footer", "logRotate",

    # Testing
    "test_ui",

    # Interactive UI (v1.3)
    "menu", "select_list", "progress_bar", "confirm",

    # Table formatting (v1.3)
    "print_table", "table_format", "print_dict_table",

    # Advanced logging (v1.3)
    "Logger", "get_logger", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL",

    # Advanced file utilities (v1.3)
    "copy_file", "move_file", "search_files", "get_file_info",

    # Master execution logging (v1.4)
    "scriptStart", "scriptEnd", "MASTER_EXEC_LOG",

    # Global settings
    "ROOT_DIR", "LOG_DIR", "TEMP_DIR",
    "get_timestamp", "print_banner", "SETTINGS",

    # Image/video utilities
    "create_thumb_resize", "list_thumbnails",

    # Command-line parsing (v1.3)
    "parse_simple_args", "CB9ArgParser", "get_script_name", "get_all_args",

    # Input validation (v1.3)
    "is_valid_email", "is_valid_number", "is_valid_integer", "is_valid_path",
    "is_valid_ip", "is_valid_hostname", "is_valid_port",
    "validate_input", "validate_choice",

    # Testing framework (v1.3)
    "assert_equals", "assert_true", "assert_false",
    "test_suite", "mock_input", "capture_output",
    "get_test_stats", "reset_test_stats",

    # Job logging + alerting (v1.4)
    "job_logger", "JobLogger",
]
