#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
#
# Filename: func.py
# Project: Shared Library
# Version: 1.7
# Description: Common functions for Cloud Box 9 projects (UI + JSON + Console).
# Maintainer: Cloud Box 9 Inc.
# Last Modified Date: 2026-04-19
# -----------------------------------------------------------------------------
# Function List:
# -----------------------------------------------------------------------------
# clear_screen()
#     Clear the terminal screen
#
# pause(msg: str = "Press Enter to continue...")
#     Pause for user input with custom message
#     msg: Message to display to user
#
# sleep(seconds: float = 1.0)
#     Wait for N seconds with visual indicator
#     seconds: Number of seconds to wait
#
# load_json_config(jsonFileName: str) -> dict
#     Load and parse JSON config file, returns empty dict on error
#     jsonFileName: Path to JSON file (absolute or relative)
#                   Example: "config.json" or "/Users/user/config.json"
#
# save_json_config(jsonFileName: str, data: dict)
#     Save dictionary to JSON file with indentation
#     jsonFileName: Path to JSON file (absolute or relative)
#                   Example: "config.json" or "/Users/user/config.json"
#     data: Dictionary to save as JSON
#
# header(title: str = "Untitled Script", version: str = "v1.2", subtitle: str = "", width: int = 0)
#     Display full header banner with title, version, and optional subtitle
#     title: Title of the script/application
#     version: Version string (e.g., "v1.2")
#     subtitle: Optional subtitle text
#     width: Terminal width (0 = auto-detect)
#
# footerMenu(legend: str = "", width: int = 0) -> str
#     Display footer menu with legend and prompt, returns user input
#     legend: Menu legend/instructions to display
#     width: Terminal width (0 = auto-detect)
#
# file_exists(path: str) -> bool
#     Check if a file exists
#     path: Path to file (absolute or relative)
#           Example: "data.txt" or "/Users/user/data.txt"
#
# folder_exists(path: str) -> bool
#     Check if a directory exists
#     path: Path to directory (absolute or relative)
#           Example: "logs" or "/Users/user/Documents/log"
#
# ensure_folder(path: str)
#     Create directory if not existing
#     path: Path to directory (absolute or relative)
#           Example: "output" or "/Users/user/Documents/output"
#
# list_files(path: str, ext: str = None) -> list
#     List files in directory, optionally filter by extension
#     path: Directory path (absolute or relative)
#           Example: "data" or "/Users/user/Documents/data"
#     ext: Optional file extension filter (e.g., ".py", ".json")
#
# remove_files(path: str, filelist: Optional[List[str]] = None, dry_run: bool = False, log_deletions: bool = True) -> bool
#     Delete files matching patterns from path recursively (secure, no shell injection)
#     path: Root directory to search (absolute or relative)
#           Example: "/Volumes/Data" or "~/Documents/cleanup"
#     filelist: List of filename patterns to delete (e.g., ['.DS_Store', '*.tmp', '*.log'])
#     dry_run: If True, shows what would be deleted without actually deleting
#     log_deletions: If True, logs all deletions to LOG_DIR with timestamps
#
# write_log(message: str, filename: str = None)
#     Write log message to file and print to console
#     message: Log message to write
#     filename: Optional log file path (absolute or relative, auto-generated if None)
#               Example: "/Users/user/Documents/log/app.log"
#
# log_header(job_name: str, version: str = "v1.2", filename: str = None) -> str
#     Write log header at start of job, returns filename
#     job_name: Name of the job/script
#     version: Version string
#     filename: Optional log file path (absolute or relative, auto-generated if None)
#               Example: "/Users/user/Documents/log/backup.log"
#
# log_footer(job_name: str, version: str = "v1.2", filename: str = None)
#     Write log footer at end of job
#     job_name: Name of the job/script
#     version: Version string
#     filename: Log file path (absolute or relative)
#               Example: "/Users/user/Documents/log/backup.log"
#
# logRotate(script_name: str, version: str = "v1.2", old_filename: str = None) -> str
#     Rotate log file, create new timestamped file with header, returns new filename
#     script_name: Name of the script/job
#     version: Version string
#     old_filename: Optional previous log file to close (absolute or relative)
#                   Example: "/Users/user/Documents/log/backup_2025-10-23.log"
#
# test_ui()
#     Demonstrate header, footer, and color usage
#
# -----------------------------------------------------------------------------
# Revision History:
# -----------------------------------------------------------------------------
# v1.7 (2026-04-19)
#   • MASTER_EXEC_LOG: hardened against rogue literal-`~` folders.
#     When expanduser("~/...") returns unchanged (HOME unset + no valid
#     passwd home, e.g. sudo/cron/www-data on BPA5), fall back to
#     $HOME or /home/ubuntu. scriptStart/scriptEnd also refuse to run
#     if the resolved path still begins with `~`.
#
# v1.6 (2026-03-19)
#   • play_sound() now accepts http/https URLs: downloads to a temp file,
#     plays via afplay, then deletes the temp file (non-blocking)
#   • get_project_sound() no longer rejects URL values with os.path.isfile();
#     URLs pass through directly as valid overrides
#   • Added urllib.request and tempfile imports
#
# v1.3 (2025-10-24)
#   • Major security update to remove_files() function
#   • Replaced shell command execution with native pathlib operations (eliminates shell injection risk)
#   • Added proper type hints (Optional[List[str]]) and fixed boolean return values
#   • Added dry_run mode for safe testing before deletion
#   • Added automatic logging of deletions with timestamps
#   • Improved error handling with separate permission error detection
#   • Added wildcard pattern support (e.g., '*.tmp', '.DS_Store')
#   • Added typing module imports (List, Optional) for better type safety
#
# v1.2 (2025-10-23)
#   • Added logRotate() function for log file rotation with timestamps
#   • Enhanced Function List with complete parameter descriptions
#   • Added return type annotations to function signatures
#   • Added detailed argument descriptions for each parameter
#   • Added path type specifications and example inputs for file/folder arguments
#
# v1.1 (2025-10-22)
#   • Added full Function List header and Revision History section.
#   • Integrated write_log() logging function below File Utilities.
#   • Confirmed Cloud Box 9 formatting, UI header/footer consistency.
#   • Version officially marked as baseline v1.1.
# -----------------------------------------------------------------------------

import os, json, shutil, time, logging, subprocess, tempfile, urllib.request
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from CB9Lib.colors import *
from CB9Lib.globals import *

# -----------------------------------------------------------------------------
# Global Vars
# -----------------------------------------------------------------------------
width = shutil.get_terminal_size().columns

# -----------------------------------------------------------------------------
# Core Utilities
# -----------------------------------------------------------------------------
def get_width() -> int:
    """
    Get the current terminal width.
    Call this after clear_screen() to get the updated width if window was resized.

    Returns:
        int: Current terminal width in columns
    """
    return shutil.get_terminal_size().columns


def clear_screen():
    """Clear the terminal screen."""
    os.system("clear" if os.name == "posix" else "cls")


def pause(msg: str = "Press Enter to continue..."):
    """Pause for user input."""
    input(f"{DIM}{msg}{RESET}")


def sleep(seconds: float = 1.0):
    """Wait for N seconds (with small visual indicator)."""
    print(f"{DIM}Please wait{RESET}", end="", flush=True)
    for _ in range(int(seconds * 2)):
        time.sleep(0.5)
        print(f"{DIM}.{RESET}", end="", flush=True)
    print()

# -----------------------------------------------------------------------------
# JSON Helpers
# -----------------------------------------------------------------------------
def load_json_config(jsonFileName: str) -> dict:
    """
    Load and parse JSON config file.
    Returns empty dict if file missing or invalid.
    """
    try:
        with open(jsonFileName, "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(color_text(f"[ERROR] Config file not found: {jsonFileName}", RED, style=BOLD))
    except json.JSONDecodeError as e:
        print(color_text(f"[ERROR] Invalid JSON format: {e}", RED, style=BOLD))
    return {}


def save_json_config(jsonFileName: str, data: dict):
    """
    Save dictionary to JSON file with indentation.
    """
    try:
        with open(jsonFileName, "w") as f:
            json.dump(data, f, indent=4)
        print(color_text(f"[OK] Saved: {jsonFileName}", GREEN))
    except Exception as e:
        print(color_text(f"[ERROR] Could not save JSON: {e}", RED))

# -----------------------------------------------------------------------------
# UI Elements
# -----------------------------------------------------------------------------
def header(title: str = "Untitled Script", version: str = "v1.2", subtitle: str = "", width: int = 0):
    """
    Display a full header banner with title and version.
    """
    if width == 0:
        width = shutil.get_terminal_size().columns
    if subtitle != "":
        subtitle = "["+subtitle+"]"
    clear_screen()
    print("=" * width)
    print(f" {BOLD}{CYAN}{title}{MAGENTA} {version} {BRIGHT_GREEN}{subtitle}{RESET}")
    print("=" * width)


def footerMenu(legend: str = "", width: int = 0) -> str:
    """
    Display footer menu with legend and prompt for user input.
    Returns the choice entered by the user.
    """
    if width == 0:
        width = shutil.get_terminal_size().columns
    print("-" * width)
    if legend:
        print(color_text(legend, fg=BRIGHT_YELLOW))
    print("-" * width)
    choice = input(f"{BOLD}{WHITE}> {RESET}").strip().lower()
    return choice


def exit_screen(script_name: str, version: str, copyright_year: str = "2026", width: int = 0):
    """
    Display the standard CB9 exit screen and terminate.

    Shows:
      - Header (= bar / title / = bar)
      - "<script_name> exiting..."
      - Copyright notice
      - A closing = separator line

    This is the canonical exit display for ALL CB9 scripts.
    Always call this instead of rolling your own exit block.
    """
    if width == 0:
        width = shutil.get_terminal_size().columns
    clear_screen()
    print("=" * width)
    print(f" {BOLD}{CYAN}{script_name}{MAGENTA} {version}{RESET}")
    print("=" * width)
    print()
    print(color_text(f"{script_name} exiting...", fg=CYAN))
    print()
    print(f"Copyright \u00a9 {copyright_year} Cloud Box 9 Inc. All rights reserved.")
    print()
    print("=" * width)

# -----------------------------------------------------------------------------
# Sound Utilities
# -----------------------------------------------------------------------------

def get_project_sound(project_name: str, sound_type: str, default_path: str) -> str:
    """
    Return the audio file path for a script, preferring a project-specific
    override from ~/userProfile.json over the supplied default.

    Lookup logic:
      1. Load ~/userProfile.json
      2. Find the entry in projectPreferences where projectName == project_name
      3. If the entry has a key matching sound_type ('successAudio' or 'failureAudio')
         and the resolved file exists on disk, return that path.
      4. Otherwise return default_path.

    Args:
        project_name:  Matches projectPreferences[].projectName  (e.g. "Git Push All")
        sound_type:    Key to look up — 'successAudio' or 'failureAudio'
        default_path:  Fallback path (local audio/ file inside the script folder)

    Returns:
        Resolved path string (expanded ~ if needed).
    """
    try:
        profile_path = os.path.expanduser("~/userProfile.json")
        if not os.path.isfile(profile_path):
            return default_path

        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)

        prefs = profile.get("projectPreferences", [])
        for entry in prefs:
            if entry.get("projectName", "") == project_name:
                raw = entry.get(sound_type, "")
                if raw:
                    if raw.startswith("http://") or raw.startswith("https://"):
                        return raw  # URL — pass through as-is
                    resolved = os.path.expanduser(raw)
                    if os.path.isfile(resolved):
                        return resolved
                break  # found the project, no override or file missing
    except Exception:
        pass  # never crash a script over a missing sound

    return default_path


def play_sound(filepath: str):
    """
    Play an audio file non-blocking via afplay (macOS).
    Accepts a local file path or an http/https URL.
    For URLs, downloads to a temp file, plays it, then deletes it.
    Silently does nothing if the file does not exist or download fails.
    """
    if not filepath:
        return

    if filepath.startswith("http://") or filepath.startswith("https://"):
        try:
            suffix = os.path.splitext(filepath.split("?")[0])[1] or ".mp3"
            tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            tmp.close()
            urllib.request.urlretrieve(filepath, tmp.name)
            def _play_and_delete(path):
                subprocess.run(
                    ["afplay", path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                try:
                    os.unlink(path)
                except Exception:
                    pass
            import threading
            threading.Thread(target=_play_and_delete, args=(tmp.name,), daemon=True).start()
        except Exception:
            pass  # never crash a script over a missing sound
    elif os.path.isfile(filepath):
        subprocess.Popen(
            ["afplay", filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

# -----------------------------------------------------------------------------
# File Utilities
# -----------------------------------------------------------------------------
def file_exists(path: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(path)


def folder_exists(path: str) -> bool:
    """Check if a directory exists."""
    return os.path.isdir(path)


def ensure_folder(path: str):
    """Create directory if not existing."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(color_text(f"[Created] {path}", GREEN))
    else:
        print(color_text(f"[Exists]  {path}", CYAN))


def list_files(path: str, ext: str = None) -> list:
    """List files in a directory (optionally filter by extension)."""
    try:
        files = [f for f in os.listdir(path) if not ext or f.endswith(ext)]
        return sorted(files)
    except Exception as e:
        print(color_text(f"[ERROR] {e}", RED))
        return []

def remove_files(
    path: str,
    filelist: Optional[List[str]] = None,
    dry_run: bool = False,
    log_deletions: bool = True
) -> bool:
    """
    Deletes files matching patterns in filelist from path recursively.

    Args:
        path: Root directory to search (absolute or relative)
        filelist: List of filename patterns to delete (e.g., ['.DS_Store', '*.tmp'])
        dry_run: If True, only shows what would be deleted without deleting
        log_deletions: If True, logs deleted files to LOG_DIR

    Returns:
        True if successful with no errors, False if errors occurred
    """
    if filelist is None:
        filelist = []

    ensure_folder(LOG_DIR)

    # Setup logging if needed
    if log_deletions:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = Path(LOG_DIR) / f"deletions_{timestamp}.log"
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            force=True
        )

    try:
        root_path = Path(path)
        if not root_path.exists():
            print(color_text(f"[ERROR] Path does not exist: {path}", RED, style=BOLD))
            return False

        deleted_count = 0
        error_count = 0

        for pattern in filelist:
            # Use rglob for recursive globbing (handles wildcards)
            for file_path in root_path.rglob(pattern):
                if file_path.is_file():
                    try:
                        if dry_run:
                            print(color_text(f"[DRY RUN] Would delete: {file_path}", YELLOW))
                        else:
                            file_path.unlink()
                            deleted_count += 1
                            if log_deletions:
                                logging.info(f"Deleted: {file_path}")
                            print(color_text(f"[Deleted] {file_path}", GREEN))
                    except PermissionError:
                        error_count += 1
                        print(color_text(f"[ERROR] Permission denied: {file_path}", RED, style=BOLD))
                        if log_deletions:
                            logging.error(f"Permission denied: {file_path}")
                    except Exception as e:
                        error_count += 1
                        print(color_text(f"[ERROR] Failed to delete {file_path}: {e}", RED, style=BOLD))
                        if log_deletions:
                            logging.error(f"Failed to delete {file_path}: {e}")

        # Summary
        if dry_run:
            print(color_text(f"\n[DRY RUN] Complete. Found {deleted_count} file(s) that would be deleted.", CYAN, style=BOLD))
        else:
            print(color_text(f"\n[SUCCESS] Deleted {deleted_count} file(s)", GREEN, style=BOLD))

        if error_count > 0:
            print(color_text(f"[WARNING] {error_count} error(s) occurred", YELLOW, style=BOLD))

        return error_count == 0

    except Exception as e:
        print(color_text(f"[ERROR] {e}", RED, style=BOLD))
        if log_deletions:
            logging.error(f"Fatal error: {e}")
        return False

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
def write_log(message: str, filename: str = None):
    """Write a log message to file and print it to console."""
    ensure_folder(LOG_DIR)
    if not filename:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(LOG_DIR, f"script_{timestamp}.log")

    try:
        with open(filename, "a") as log_file:
            log_file.write(f"[{datetime.now()}] {message}\n")
        print(f"{BOLD}{YELLOW}{message}{RESET}")
    except Exception as e:
        print(color_text(f"[ERROR] Could not write log: {e}", RED, style=BOLD))


def log_header(job_name: str, version: str = "v1.2", filename: str = None):
    """
    Write a log header at the start of a job.
    Logs the job name, version, and start timestamp with a separator line.
    """
    ensure_folder(LOG_DIR)
    if not filename:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(LOG_DIR, f"{job_name.replace(' ', '_')}_{timestamp}.log")

    separator = "-" * 80
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(filename, "a") as log_file:
            log_file.write(f"{separator}\n")
            log_file.write(f"JOB: {job_name} {version}\n")
            log_file.write(f"START: {start_time}\n")
            log_file.write(f"{separator}\n")
        print(color_text(f"[LOG] Started: {job_name} {version}", BRIGHT_GREEN, style=BOLD))
        return filename
    except Exception as e:
        print(color_text(f"[ERROR] Could not write log header: {e}", RED, style=BOLD))
        return None


def log_footer(job_name: str, version: str = "v1.2", filename: str = None):
    """
    Write a log footer at the end of a job.
    Logs the job name, version, and end timestamp.
    """
    if not filename:
        print(color_text("[WARNING] No log filename provided for footer", YELLOW))
        return

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = "-" * 80

    try:
        with open(filename, "a") as log_file:
            log_file.write(f"END: {end_time}\n")
            log_file.write(f"JOB: {job_name} {version}\n")
            log_file.write(f"{separator}\n\n")
        # print(color_text(f"[LOG] Completed: {job_name} {version}", YELLOW, style=BOLD))
    except Exception as e:
        print(color_text(f"[ERROR] Could not write log footer: {e}", RED, style=BOLD))


def logRotate(script_name: str, version: str = "v1.2", old_filename: str = None) -> str:
    """
    Rotate the log file and create a new one with a header.

    Creates a new timestamped log file with a header containing:
    - Created Date
    - Script Name
    - Version

    Args:
        script_name: Name of the script/job
        version: Version string (default "v1.2")
        old_filename: Optional previous log file (for reference only)

    Returns:
        str: Path to the new log file
    """
    ensure_folder(LOG_DIR)

    # Close old log with footer if provided
    if old_filename:
        try:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            separator = "-" * 80
            with open(old_filename, "a") as log_file:
                log_file.write(f"END: {end_time}\n")
                log_file.write(f"LOG ROTATED\n")
                log_file.write(f"{separator}\n\n")
        except Exception as e:
            print(color_text(f"[WARNING] Could not close old log: {e}", YELLOW))

    # Create new log file with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_filename = os.path.join(LOG_DIR, f"{script_name.replace(' ', '_')}_{timestamp}.log")

    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = "-" * 80

    try:
        with open(new_filename, "w") as log_file:
            log_file.write(f"{separator}\n")
            log_file.write(f"LOG FILE CREATED: {created_date}\n")
            log_file.write(f"SCRIPT: {script_name}\n")
            log_file.write(f"VERSION: {version}\n")
            log_file.write(f"{separator}\n")
        print(color_text(f"[LOG] Rotated: {new_filename}", BRIGHT_CYAN, style=BOLD))
        return new_filename
    except Exception as e:
        print(color_text(f"[ERROR] Could not create rotated log: {e}", RED, style=BOLD))
        return None

# -----------------------------------------------------------------------------
# Interactive UI (v1.3)
# -----------------------------------------------------------------------------
def menu(title: str, options: list, allow_back: bool = True, allow_quit: bool = True) -> str:
    """
    Display an interactive menu with numbered options.

    Args:
        title: Menu title to display
        options: List of menu options (strings or tuples of (key, description))
        allow_back: Include a 'Back' option (default: True)
        allow_quit: Include a 'Quit' option (default: True)

    Returns:
        Selected option key/text, or 'back', 'quit'
    """
    print(f"\n{color_text(title, fg=CYAN, style=BOLD)}")
    print("─" * len(title))

    for i, option in enumerate(options, 1):
        if isinstance(option, tuple):
            key, desc = option
            print(f"  {color_text(str(i), fg=YELLOW)}. {desc}")
        else:
            print(f"  {color_text(str(i), fg=YELLOW)}. {option}")

    if allow_back:
        print(f"  {color_text('B', fg=YELLOW)}. Back")
    if allow_quit:
        print(f"  {color_text('Q', fg=YELLOW)}. Quit")

    while True:
        choice = input(f"\n{color_text('Select option:', fg=CYAN)} ").strip().lower()

        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return choice
        elif allow_back and choice == 'b':
            return 'back'
        elif allow_quit and choice == 'q':
            return 'quit'
        else:
            print(color_text("Invalid choice. Please try again.", fg=RED))


def select_list(title: str, items: list, multi: bool = False, selected: list = None) -> list:
    """
    Interactive item selection with number input.

    Args:
        title: Selection prompt
        items: List of items to choose from
        multi: Allow multiple selections (default: False)
        selected: Pre-selected items (default: None)

    Returns:
        List of selected items
    """
    if selected is None:
        selected = []

    print(f"\n{color_text(title, fg=CYAN, style=BOLD)}")

    if multi:
        print(color_text("(Enter numbers separated by commas, or 'all')", fg=YELLOW))

    for i, item in enumerate(items, 1):
        marker = "✓" if item in selected else " "
        print(f"  [{marker}] {i}. {item}")

    if multi:
        choices = input(f"\n{color_text('Select (1,2,3 or all):', fg=CYAN)} ").strip().lower()

        if choices == 'all':
            return items.copy()

        result = []
        for choice in choices.split(','):
            choice = choice.strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    result.append(items[idx])
        return result
    else:
        choice = input(f"\n{color_text('Select one:', fg=CYAN)} ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return [items[idx]]
        return []


def progress_bar(current: int, total: int, width: int = 50, label: str = "", show_percent: bool = True) -> None:
    """
    Display a progress bar in the terminal.

    Args:
        current: Current progress value
        total: Total/maximum value
        width: Width of the progress bar in characters (default: 50)
        label: Optional label to show before the bar
        show_percent: Show percentage (default: True)
    """
    import sys

    percent = (current / total) * 100 if total > 0 else 0
    filled = int(width * current / total) if total > 0 else 0

    bar = "█" * filled + "░" * (width - filled)
    bar_colored = color_text(bar, fg=GREEN, style=BOLD)

    output = f"\r{label} " if label else "\r"
    output += f"[{bar_colored}]"

    if show_percent:
        output += f" {percent:.1f}%"

    output += f" ({current}/{total})"

    sys.stdout.write(output)
    sys.stdout.flush()

    if current >= total:
        sys.stdout.write("\n")


def confirm(prompt: str, default: bool = True) -> bool:
    """
    Ask for yes/no confirmation.

    Args:
        prompt: Question to ask
        default: Default answer if user just presses Enter

    Returns:
        True for yes, False for no
    """
    suffix = " [Y/n]: " if default else " [y/N]: "

    while True:
        response = input(color_text(prompt + suffix, fg=YELLOW)).strip().lower()

        if response == '':
            return default
        elif response in ('y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False
        else:
            pass


# -----------------------------------------------------------------------------
# Table Formatting (v1.3)
# -----------------------------------------------------------------------------
def print_table(headers: list, rows: list, align: list = None, border: bool = True) -> None:
    """
    Print a formatted table to the console.

    Args:
        headers: List of column headers
        rows: List of lists (each inner list is a row)
        align: List of alignment ('left', 'right', 'center') per column
        border: Show border lines (default: True)
    """
    if align is None:
        align = ['left'] * len(headers)

    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Print header
    header_parts = []
    for i, header_text in enumerate(headers):
        width = col_widths[i]
        if align[i] == 'right':
            header_parts.append(str(header_text).rjust(width))
        elif align[i] == 'center':
            header_parts.append(str(header_text).center(width))
        else:
            header_parts.append(str(header_text).ljust(width))

    separator = "─" * (sum(col_widths) + len(headers) * 3 - 1)

    if border:
        print("┌" + separator + "┐")

    print("│ " + color_text(" │ ".join(header_parts), fg=CYAN, style=BOLD) + " │")

    if border:
        print("├" + separator + "┤")
    else:
        print("  " + "─" * (sum(col_widths) + len(headers) * 3 - 3))

    # Print rows
    for row in rows:
        row_parts = []
        for i, cell in enumerate(row):
            if i < len(col_widths):
                width = col_widths[i]
                if align[i] == 'right':
                    row_parts.append(str(cell).rjust(width))
                elif align[i] == 'center':
                    row_parts.append(str(cell).center(width))
                else:
                    row_parts.append(str(cell).ljust(width))

        print("│ " + " │ ".join(row_parts) + " │")

    if border:
        print("└" + separator + "┘")


def table_format(headers: list, rows: list, align: list = None) -> str:
    """
    Return a formatted table as a string (for logging or saving).

    Returns:
        Formatted table string
    """
    if align is None:
        align = ['left'] * len(headers)

    lines = []

    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Build header
    header_parts = []
    for i, header_text in enumerate(headers):
        width = col_widths[i]
        if align[i] == 'right':
            header_parts.append(str(header_text).rjust(width))
        elif align[i] == 'center':
            header_parts.append(str(header_text).center(width))
        else:
            header_parts.append(str(header_text).ljust(width))

    lines.append(" | ".join(header_parts))
    lines.append("-" * (sum(col_widths) + len(headers) * 3 - 1))

    # Build rows
    for row in rows:
        row_parts = []
        for i, cell in enumerate(row):
            if i < len(col_widths):
                width = col_widths[i]
                if align[i] == 'right':
                    row_parts.append(str(cell).rjust(width))
                elif align[i] == 'center':
                    row_parts.append(str(cell).center(width))
                else:
                    row_parts.append(str(cell).ljust(width))
        lines.append(" | ".join(row_parts))

    return "\n".join(lines)


def print_dict_table(dict_list: list, keys: list = None) -> None:
    """
    Print a table from a list of dictionaries.

    Args:
        dict_list: List of dictionaries with same keys
        keys: Specific keys to display (None = all keys)
    """
    if not dict_list:
        return

    if keys is None:
        keys = list(dict_list[0].keys())

    headers = [k.upper() for k in keys]
    rows = [[str(d.get(k, "")) for k in keys] for d in dict_list]

    print_table(headers, rows)


# -----------------------------------------------------------------------------
# Advanced Logging System (v1.3)
# -----------------------------------------------------------------------------
# Log level constants
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50

_LOG_LEVELS = {
    DEBUG: "DEBUG",
    INFO: "INFO",
    WARNING: "WARNING",
    ERROR: "ERROR",
    CRITICAL: "CRITICAL"
}


class Logger:
    """
    Advanced logger with level filtering.
    """

    def __init__(self, name: str, level: int = INFO, filename: str = None,
                 console: bool = True, colored: bool = True):
        """
        Initialize logger.

        Args:
            name: Logger name (usually script/module name)
            level: Minimum log level to display (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            filename: Optional log file path
            console: Print to console (default: True)
            colored: Use colors in console output (default: True)
        """
        self.name = name
        self.level = level
        self.filename = filename
        self.console = console
        self.colored = colored

    def _log(self, level: int, message: str) -> None:
        """Internal logging method."""
        if level < self.level:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_name = _LOG_LEVELS.get(level, "UNKNOWN")
        log_line = f"[{timestamp}] [{level_name:8s}] [{self.name}] {message}"

        # Console output with colors
        if self.console:
            if self.colored:
                colors_map = {
                    DEBUG: CYAN,
                    INFO: RESET,
                    WARNING: YELLOW,
                    ERROR: RED,
                    CRITICAL: BRIGHT_RED
                }
                colored_line = (f"[{timestamp}] "
                               f"[{color_text(level_name, fg=colors_map.get(level, RESET))}] "
                               f"[{self.name}] {message}")
                print(colored_line)
            else:
                print(log_line)

        # File output
        if self.filename:
            Path(self.filename).parent.mkdir(parents=True, exist_ok=True)
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(log_line + "\n")

    def debug(self, message: str) -> None:
        """Log debug message."""
        self._log(DEBUG, message)

    def info(self, message: str) -> None:
        """Log info message."""
        self._log(INFO, message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self._log(WARNING, message)

    def error(self, message: str) -> None:
        """Log error message."""
        self._log(ERROR, message)

    def critical(self, message: str) -> None:
        """Log critical message."""
        self._log(CRITICAL, message)

    def set_level(self, level: int) -> None:
        """Change the log level."""
        self.level = level


def get_logger(name: str, level: int = INFO, filename: str = None) -> Logger:
    """
    Create and return a Logger instance.

    Args:
        name: Logger name
        level: Minimum log level
        filename: Optional log file

    Returns:
        Logger instance
    """
    return Logger(name, level, filename)


# -----------------------------------------------------------------------------
# Advanced File Utilities (v1.3)
# -----------------------------------------------------------------------------
def copy_file(src: str, dst: str, overwrite: bool = False) -> bool:
    """
    Copy a file from source to destination.

    Args:
        src: Source file path
        dst: Destination file path
        overwrite: Allow overwriting existing file (default: False)

    Returns:
        True if successful, False otherwise
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)

        if not src_path.exists():
            print(color_text(f"[ERROR] Source file not found: {src}", RED, style=BOLD))
            return False

        if dst_path.exists() and not overwrite:
            print(color_text(f"[ERROR] Destination exists (use overwrite=True): {dst}", RED, style=BOLD))
            return False

        shutil.copy2(src, dst)
        print(color_text(f"[Copied] {src} → {dst}", GREEN))
        return True
    except Exception as e:
        print(color_text(f"[ERROR] Failed to copy: {e}", RED, style=BOLD))
        return False


def move_file(src: str, dst: str) -> bool:
    """
    Move a file from source to destination.

    Args:
        src: Source file path
        dst: Destination file path

    Returns:
        True if successful, False otherwise
    """
    try:
        src_path = Path(src)

        if not src_path.exists():
            print(color_text(f"[ERROR] Source file not found: {src}", RED, style=BOLD))
            return False

        shutil.move(src, dst)
        print(color_text(f"[Moved] {src} → {dst}", GREEN))
        return True
    except Exception as e:
        print(color_text(f"[ERROR] Failed to move: {e}", RED, style=BOLD))
        return False


def search_files(path: str, pattern: str, recursive: bool = True) -> list:
    """
    Search for files matching a pattern.

    Args:
        path: Directory to search
        pattern: Glob pattern (e.g., "*.py", "backup_*")
        recursive: Search subdirectories (default: True)

    Returns:
        List of matching file paths
    """
    try:
        search_path = Path(path)
        if not search_path.exists():
            print(color_text(f"[ERROR] Path not found: {path}", RED, style=BOLD))
            return []

        if recursive:
            matches = list(search_path.rglob(pattern))
        else:
            matches = list(search_path.glob(pattern))

        # Return only files, not directories
        return [str(m) for m in matches if m.is_file()]
    except Exception as e:
        print(color_text(f"[ERROR] Search failed: {e}", RED, style=BOLD))
        return []


def get_file_info(path: str) -> dict:
    """
    Get detailed information about a file.

    Args:
        path: File path

    Returns:
        Dictionary with file info (size, modified, created, etc.)
    """
    try:
        file_path = Path(path)

        if not file_path.exists():
            print(color_text(f"[ERROR] File not found: {path}", RED, style=BOLD))
            return {}

        stat = file_path.stat()

        return {
            'path': str(file_path.absolute()),
            'name': file_path.name,
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            'created': datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            'is_file': file_path.is_file(),
            'is_dir': file_path.is_dir(),
            'extension': file_path.suffix
        }
    except Exception as e:
        print(color_text(f"[ERROR] Failed to get file info: {e}", RED, style=BOLD))
        return {}


# -----------------------------------------------------------------------------
# Master Execution Logging
# -----------------------------------------------------------------------------
def _resolveMasterLog() -> str:
    # expanduser silently returns "~/..." unchanged when HOME is unset AND
    # the running user has no valid passwd home (sudo/cron/www-data on BPA5).
    # Falling through to os.makedirs(~) then creates a literal `~` folder.
    p = os.path.expanduser("~/Documents/log/masterExec.log")
    if p.startswith("~"):
        home = os.environ.get("HOME") or "/home/ubuntu"
        p = os.path.join(home, "Documents/log/masterExec.log")
    return p


MASTER_EXEC_LOG = _resolveMasterLog()


def scriptStart(script_name: str) -> None:
    """
    Log script start to master execution log.

    Args:
        script_name: Name of the script being executed
    """
    try:
        if MASTER_EXEC_LOG.startswith("~"):
            return
        log_dir = os.path.dirname(MASTER_EXEC_LOG)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {script_name} - START\n"

        with open(MASTER_EXEC_LOG, "a") as f:
            f.write(log_entry)
    except Exception:
        # Silently fail - don't interrupt script execution
        pass


def scriptEnd(script_name: str) -> None:
    """
    Log script end to master execution log.

    Args:
        script_name: Name of the script being executed
    """
    try:
        if MASTER_EXEC_LOG.startswith("~"):
            return
        log_dir = os.path.dirname(MASTER_EXEC_LOG)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {script_name} - END\n"

        with open(MASTER_EXEC_LOG, "a") as f:
            f.write(log_entry)
    except Exception:
        # Silently fail - don't interrupt script execution
        pass


# -----------------------------------------------------------------------------
# Debug/Test
# -----------------------------------------------------------------------------
def test_ui():
    """Demonstrate header, footer, and color usage."""
    header("Demo Script", "v3.9")
    print(color_text("This is a demo of the Cloud Box 9 shared library.", BRIGHT_CYAN))
    choice = footerMenu("Use arrow keys or shortcuts to navigate.")
    print(color_text(f"You selected: {choice}", YELLOW))