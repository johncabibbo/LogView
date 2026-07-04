#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
#
# Filename:          logView.py
# Project:           Log Viewer
# Version:           1.06
# Description:       Interactive terminal log file viewer. Select a log file
#                    from the menu, then tail it in real time or scroll through
#                    history with arrow keys. Supports ANSI color codes.
# Maintainer:        Cloud Box 9 Inc.
# Last Modified Date: 2026-03-25
#
# -----------------------------------------------------------------------------
# Revision History:
# -----------------------------------------------------------------------------
# v1.06 (2026-03-25)
#   - Added [S] Search in viewer: bottom bar prompts for search term
#   - Left/Right arrows navigate prev/next match while in search mode
#   - Current match highlighted black-on-white; other visible matches black-on-yellow
#   - ESC exits search mode (returns to normal viewing)
#   - Footer swaps to search navigation hints while search is active
#   - Header shows SEARCH badge + "N/M" counter when search is active
#
# v1.05 (2026-03-25)
#   - Header/footer use default terminal background (no colored bar)
#   - Header title text: bold white; footer key labels: bold yellow
#
# v1.04 (2026-03-25)
#   - Header and footer bars changed from white-on-cyan to bright white-on-green
#     for improved readability (CP_HEADER, CP_FOOTER_KEY)
#   - Follow mode badge shifted to black-on-cyan (CP_FOLLOW) to remain
#     distinguishable against the new green header background
#
# v1.03 (2026-03-22)
#   - ESC now exits the viewer instantly: ESCDELAY set to 25ms before curses init
#   - ESC now exits the menu instantly: replaced footerMenu()+input() with
#     collect_input() in raw mode (same pattern as backup.py v3.7)
#   - Double-entry bug fixed: tty input buffer flushed after curses returns so
#     the first menu keypress after returning is never swallowed by a stale curses character
#   - exit screen now uses CB9Lib exit_screen() with proper closing = separator
#
# v1.02 (2026-03-17)
#   - Header text color changed from black to white (white on cyan)
#
# v1.01 (2026-03-11)
#   - Footer bar now uses the same cyan background as the header bar
#   - Footer key labels use bold white-on-cyan (CP_FOOTER_KEY) for contrast
#   - Updated legend: "Top/Bottom" → "Jump", "Back" → "Quit"
#   - Log lines starting with --Project: / -- Project: now get a blank line
#     inserted above them in the display (rawLines/displayLines separation)
#
# v1.0 (2026-03-11)
#   - Initial release
#   - CB9Lib menu for log file selection
#   - Curses viewer: ↑/↓ scroll, PgUp/PgDn page, Home/End, [F] follow mode
#   - ANSI color support: dim (timestamps), cyan (commands), green (summaries),
#     bold yellow (day headers)
#   - Auto-tail: detects new file content every 500ms while in follow mode
#   - Config-driven log file list (logViewConfig.json)
# -----------------------------------------------------------------------------

import os
import re
import sys
import select
import termios
import tty
import curses
from pathlib import Path
from datetime import datetime

# CB9Lib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # bundled CB9Lib (self-contained)
from CB9Lib import (
    header, color_text, load_json_config, exit_screen,
    clear_screen, pause, get_width,
    YELLOW, GREEN, RED, CYAN, WHITE, DIM, BOLD, RESET, BRIGHT_YELLOW
)

SCRIPT_DIR  = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / 'logViewConfig.json'
VERSION     = "1.06"

# Reduce curses ESC delay from 1000ms to 25ms so ESC exits the viewer instantly
os.environ.setdefault('ESCDELAY', '25')


def do_exit():
    """Show CB9 exit screen and quit."""
    exit_screen('Log Viewer', VERSION)
    sys.exit(0)


def collect_input(prompt: str = '> ') -> str:
    """Collect a line of input in raw mode.

    ESC exits the script immediately (no Enter needed).
    Enter (empty) or Q returns '' / 'q' for the caller to handle.
    Holds raw mode for the full session so a quickly-typed Enter
    is never lost between mode switches (fixes double-entry bug).
    """
    print(f"{BOLD}{WHITE}{prompt}{RESET}", end='', flush=True)
    input_str = ''
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch in ('\r', '\n'):
                print()
                return input_str
            elif ch == '\x1b':          # ESC — exit immediately
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                do_exit()
            elif ch in ('\x7f', '\b'):  # Backspace
                if input_str:
                    input_str = input_str[:-1]
                    print('\b \b', end='', flush=True)
            elif ch.isprintable():
                input_str += ch
                print(ch, end='', flush=True)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return input_str

# Curses color pair IDs
CP_DEFAULT      = 1   # white
CP_DIM          = 2   # dim white  (timestamps)
CP_CYAN         = 3   # cyan       (user commands)
CP_GREEN        = 4   # green      (summaries)
CP_YELLOW       = 5   # bold yellow (day headers)
CP_HEADER       = 6   # white on default (header/footer bar)
CP_FOLLOW       = 7   # black on cyan (follow badge)
CP_SCROLL       = 8   # black on yellow (scroll badge)
CP_FOOTER_KEY   = 9   # bold yellow (footer key labels)
CP_SEARCH_MATCH = 10  # black on yellow (non-current match highlight)
CP_SEARCH_CUR   = 11  # black on white  (current match highlight)
CP_SEARCH_BADGE = 12  # black on magenta (SEARCH header badge)


# =============================================================================
# LINE PREPROCESSING
# =============================================================================

_ANSI_RE      = re.compile(r'\x1b\[[0-9;]*m')
_PROJECT_RE   = re.compile(r'^\[[\d\- :]+\]\s+--\s*Project:', re.IGNORECASE)


def _stripAnsi(text: str) -> str:
    return _ANSI_RE.sub('', text)


def preprocessLines(lines: list[str]) -> list[str]:
    """Return display list with a blank line inserted before --Project: entries."""
    result = []
    for i, line in enumerate(lines):
        if i > 0 and _PROJECT_RE.match(_stripAnsi(line)):
            result.append('')
        result.append(line)
    return result


# =============================================================================
# FILE READING & TAIL
# =============================================================================

def readFile(filePath: str) -> tuple[list[str], int]:
    """Read entire file. Returns (lines, bytePosition)."""
    try:
        with open(filePath, 'rb') as f:
            data = f.read()
        lines = data.decode('utf-8', errors='replace').splitlines()
        return lines, len(data)
    except Exception as e:
        return [f'[ERROR] Could not read file: {e}'], 0


def checkTail(filePath: str, lastPos: int, lines: list[str]) -> tuple[list[str], int]:
    """
    Check for new content since lastPos.
    Returns (updatedLines, newBytePosition).
    """
    try:
        currentSize = os.path.getsize(filePath)
        if currentSize <= lastPos:
            return lines, lastPos

        with open(filePath, 'rb') as f:
            f.seek(lastPos)
            newData = f.read()

        if not newData:
            return lines, lastPos

        newText  = newData.decode('utf-8', errors='replace')
        newLines = newText.splitlines()

        # If the byte before lastPos was not a newline, the first new chunk
        # is a continuation of the last existing line — merge it.
        if lastPos > 0 and lines:
            with open(filePath, 'rb') as f:
                f.seek(lastPos - 1)
                prevByte = f.read(1)
            if prevByte != b'\n' and newLines:
                lines = lines[:-1] + [lines[-1] + newLines[0]] + newLines[1:]
            else:
                lines = lines + newLines
        else:
            lines = lines + newLines

        return lines, currentSize

    except Exception:
        return lines, lastPos


# =============================================================================
# ANSI → CURSES ATTRIBUTES
# =============================================================================

def getAnsiAttr(code: str) -> int:
    """Convert an ANSI escape code string to a curses attribute integer."""
    if code == '0':
        return curses.A_NORMAL
    if code == '2':
        return curses.color_pair(CP_DIM) | curses.A_DIM
    if code == '32':
        return curses.color_pair(CP_GREEN)
    if code == '36':
        return curses.color_pair(CP_CYAN)
    if code in ('33', '1;33'):
        return curses.color_pair(CP_YELLOW) | curses.A_BOLD
    if code == '1':
        return curses.color_pair(CP_DEFAULT) | curses.A_BOLD
    return curses.A_NORMAL


def parseAnsiLine(line: str) -> list[tuple[str, int]]:
    """
    Split a line with ANSI escape sequences into (text, curses_attr) segments.
    """
    segments    = []
    currentAttr = curses.A_NORMAL
    parts       = re.split(r'\x1b\[([0-9;]+)m', line)

    for i, part in enumerate(parts):
        if i % 2 == 0:          # text segment
            if part:
                segments.append((part, currentAttr))
        else:                    # ANSI code
            if part == '0':
                currentAttr = curses.A_NORMAL
            else:
                currentAttr = getAnsiAttr(part)

    return segments


# =============================================================================
# SEARCH HELPERS
# =============================================================================

def buildSearchMatches(lines: list[str], term: str) -> list[int]:
    """Return sorted list of line indices that contain term (case-insensitive)."""
    tl = term.lower()
    return [i for i, line in enumerate(lines) if tl in _stripAnsi(line).lower()]


def getMatchCol(line: str, term: str) -> tuple[int, int]:
    """
    Return (visual_col, match_len) of the first occurrence of term in line.
    Visual column is computed on the ANSI-stripped text (ANSI codes are zero-width).
    Returns (-1, 0) if not found.
    """
    stripped = _stripAnsi(line)
    idx = stripped.lower().find(term.lower())
    if idx < 0:
        return -1, 0
    return idx, len(term)


def scrollToMatch(matchLineIdx: int, contentH: int, maxScroll: int) -> int:
    """Return a scroll position that centers matchLineIdx in the viewport."""
    return max(0, min(maxScroll, matchLineIdx - contentH // 2))


# =============================================================================
# CURSES VIEWER — DRAWING
# =============================================================================

def initColors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(CP_DEFAULT,      curses.COLOR_WHITE,   -1)
    curses.init_pair(CP_DIM,          curses.COLOR_WHITE,   -1)
    curses.init_pair(CP_CYAN,         curses.COLOR_CYAN,    -1)
    curses.init_pair(CP_GREEN,        curses.COLOR_GREEN,   -1)
    curses.init_pair(CP_YELLOW,       curses.COLOR_YELLOW,  -1)
    curses.init_pair(CP_HEADER,       curses.COLOR_WHITE,   -1)
    curses.init_pair(CP_FOLLOW,       curses.COLOR_BLACK,   curses.COLOR_CYAN)
    curses.init_pair(CP_SCROLL,       curses.COLOR_BLACK,   curses.COLOR_YELLOW)
    curses.init_pair(CP_FOOTER_KEY,   curses.COLOR_YELLOW,  -1)
    curses.init_pair(CP_SEARCH_MATCH, curses.COLOR_BLACK,   curses.COLOR_YELLOW)
    curses.init_pair(CP_SEARCH_CUR,   curses.COLOR_BLACK,   curses.COLOR_WHITE)
    curses.init_pair(CP_SEARCH_BADGE, curses.COLOR_BLACK,   curses.COLOR_MAGENTA)


def drawHeader(stdscr, fileName: str, followMode: bool,
               scrollPos: int, totalLines: int,
               maxY: int, maxX: int, contentH: int,
               searchState: str = 'none', searchTerm: str = '',
               searchIdx: int = 0, matchCount: int = 0):
    """Draw the top header bar (row 0) and separator (row 1)."""
    hdrAttr = curses.color_pair(CP_HEADER)

    # Mode badge
    if searchState == 'active':
        modeAttr = curses.color_pair(CP_SEARCH_BADGE)
        modeText = ' SEARCH '
    elif followMode:
        modeAttr = curses.color_pair(CP_FOLLOW)
        modeText = ' FOLLOW '
    else:
        modeAttr = curses.color_pair(CP_SCROLL)
        modeText = ' SCROLL '

    endLine = min(scrollPos + contentH, totalLines)
    posText = f' {scrollPos + 1}–{endLine} / {totalLines} '

    # Match counter (appended to posText when search is active)
    if searchState == 'active' and matchCount > 0:
        posText = f' {searchIdx + 1}/{matchCount}  {posText}'

    # Fill header row
    try:
        stdscr.addstr(0, 0, ' ' * (maxX - 1), hdrAttr)
    except curses.error:
        pass

    # Left: title
    title = f'  Log Viewer  {fileName}'
    try:
        stdscr.addstr(0, 0, title[:maxX - len(modeText) - len(posText) - 2], hdrAttr | curses.A_BOLD)
    except curses.error:
        pass

    # Right: mode badge + position
    rightX = maxX - len(modeText) - len(posText) - 1
    try:
        stdscr.addstr(0, max(0, rightX),                          modeText, modeAttr | curses.A_BOLD)
        stdscr.addstr(0, max(0, rightX + len(modeText)),          posText,  hdrAttr)
    except curses.error:
        pass

    # Separator
    try:
        stdscr.addstr(1, 0, '─' * (maxX - 1), curses.color_pair(CP_DIM) | curses.A_DIM)
    except curses.error:
        pass


def drawFooter(stdscr, maxY: int, maxX: int):
    """Draw the separator and key-hint footer bar at the bottom (normal mode)."""
    sepAttr = curses.color_pair(CP_DIM) | curses.A_DIM
    try:
        stdscr.addstr(maxY - 2, 0, '─' * (maxX - 1), sepAttr)
    except curses.error:
        pass

    hints = [
        ('↑/↓',      'Scroll'),
        ('PgUp/PgDn', 'Page'),
        ('Home/End',  'Jump'),
        ('F',         'Follow'),
        ('S',         'Search'),
        ('Q/ESC',     'Quit'),
    ]

    barAttr = curses.color_pair(CP_HEADER)
    keyAttr = curses.color_pair(CP_FOOTER_KEY) | curses.A_BOLD
    col     = 2

    try:
        stdscr.addstr(maxY - 1, 0, ' ' * (maxX - 1), barAttr)
    except curses.error:
        pass

    for key, desc in hints:
        bracket_key = f'[{key}]'
        entry       = f'{bracket_key} {desc}  '
        if col + len(entry) >= maxX - 1:
            break
        try:
            stdscr.addstr(maxY - 1, col,                    bracket_key,  keyAttr)
            stdscr.addstr(maxY - 1, col + len(bracket_key), f' {desc}  ', barAttr)
        except curses.error:
            pass
        col += len(entry)


def drawSearchEntryBar(stdscr, maxY: int, maxX: int, searchInput: str):
    """Draw the search input bar at the bottom while the user is typing."""
    sepAttr = curses.color_pair(CP_DIM) | curses.A_DIM
    try:
        stdscr.addstr(maxY - 2, 0, '─' * (maxX - 1), sepAttr)
    except curses.error:
        pass

    barAttr = curses.color_pair(CP_HEADER)
    keyAttr = curses.color_pair(CP_FOOTER_KEY) | curses.A_BOLD
    try:
        stdscr.addstr(maxY - 1, 0, ' ' * (maxX - 1), barAttr)
        stdscr.addstr(maxY - 1, 1, '[S]',             keyAttr)
        prompt = ' Search: '
        stdscr.addstr(maxY - 1, 4, prompt + searchInput, barAttr | curses.A_BOLD)
    except curses.error:
        pass

    # Place cursor at end of typed input
    cursorX = 4 + len(' Search: ') + len(searchInput)
    try:
        stdscr.move(maxY - 1, min(cursorX, maxX - 2))
    except curses.error:
        pass


def drawSearchActiveBar(stdscr, maxY: int, maxX: int,
                        searchTerm: str, searchIdx: int, matchCount: int):
    """Draw the search navigation bar at the bottom while navigating matches."""
    sepAttr = curses.color_pair(CP_DIM) | curses.A_DIM
    try:
        stdscr.addstr(maxY - 2, 0, '─' * (maxX - 1), sepAttr)
    except curses.error:
        pass

    barAttr = curses.color_pair(CP_HEADER)
    keyAttr = curses.color_pair(CP_FOOTER_KEY) | curses.A_BOLD
    try:
        stdscr.addstr(maxY - 1, 0, ' ' * (maxX - 1), barAttr)
    except curses.error:
        pass

    col = 1

    if matchCount == 0:
        noMatch = f' No matches for "{searchTerm}"'
        try:
            stdscr.addstr(maxY - 1, col,       '[ESC]',   keyAttr)
            stdscr.addstr(maxY - 1, col + 5,   ' Exit Search', barAttr)
            stdscr.addstr(maxY - 1, col + 17,  noMatch,   barAttr | curses.A_BOLD)
        except curses.error:
            pass
        return

    hints = [
        ('[←]',   'Prev'),
        ('[→]',   'Next'),
        ('[ESC]', 'Exit Search'),
    ]
    for key, desc in hints:
        entry = f'{key} {desc}  '
        if col + len(entry) >= maxX - 1:
            break
        try:
            stdscr.addstr(maxY - 1, col,              key,          keyAttr)
            stdscr.addstr(maxY - 1, col + len(key),   f' {desc}  ', barAttr)
        except curses.error:
            pass
        col += len(entry)

    # Right-align: search term + match counter
    counter = f'  "{searchTerm}"  {searchIdx + 1}/{matchCount}  '
    counterX = maxX - len(counter) - 1
    if counterX > col:
        try:
            stdscr.addstr(maxY - 1, counterX, counter, barAttr | curses.A_BOLD)
        except curses.error:
            pass


def drawContent(stdscr, lines: list[str], scrollPos: int,
                contentH: int, maxX: int,
                searchTerm: str = '',
                searchMatchSet: set | None = None,
                currentMatchLine: int = -1):
    """Render the visible log lines with ANSI color support and search highlighting."""
    for row in range(contentH):
        lineIdx = scrollPos + row
        screenY = row + 2          # rows 0,1 are header

        if lineIdx >= len(lines):
            break

        line     = lines[lineIdx]
        segments = parseAnsiLine(line)
        col      = 0

        for text, attr in segments:
            if col >= maxX - 1:
                break
            displayText = text[:maxX - 1 - col]
            try:
                stdscr.addstr(screenY, col, displayText, attr)
            except curses.error:
                pass
            col += len(displayText)

        # Overlay search match highlight using chgat (changes attrs without changing chars)
        if searchTerm and searchMatchSet is not None and lineIdx in searchMatchSet:
            matchCol, matchLen = getMatchCol(line, searchTerm)
            if matchCol >= 0 and matchCol < maxX - 1:
                highlightLen = min(matchLen, maxX - 1 - matchCol)
                if lineIdx == currentMatchLine:
                    hlAttr = curses.color_pair(CP_SEARCH_CUR) | curses.A_BOLD
                else:
                    hlAttr = curses.color_pair(CP_SEARCH_MATCH)
                try:
                    stdscr.chgat(screenY, matchCol, highlightLen, hlAttr)
                except curses.error:
                    pass


# =============================================================================
# CURSES VIEWER — MAIN LOOP
# =============================================================================

def viewerLoop(stdscr, filePath: str, config: dict):
    """Curses viewer: scroll, tail, ANSI colors, search."""
    initColors()
    curses.curs_set(0)
    stdscr.timeout(500)          # Non-blocking getch; -1 returned on timeout

    rawLines, lastPos = readFile(filePath)
    lines             = preprocessLines(rawLines)
    fileName          = Path(filePath).name
    followMode        = config.get('viewer', {}).get('followOnOpen', True)

    maxY, maxX     = stdscr.getmaxyx()
    contentH       = max(1, maxY - 4)
    scrollPos      = max(0, len(lines) - contentH) if followMode else 0

    # Search state
    searchState   = 'none'   # 'none' | 'entry' | 'active'
    searchInput   = ''       # text being typed in entry mode
    searchTerm    = ''       # confirmed search term
    searchMatches = []       # ordered list of matching line indices
    searchMatchSet: set = set()
    searchIdx     = 0        # index into searchMatches (current match)

    while True:
        maxY, maxX = stdscr.getmaxyx()
        contentH   = max(1, maxY - 4)
        maxScroll  = max(0, len(lines) - contentH)
        scrollPos  = min(scrollPos, maxScroll)

        currentMatchLine = searchMatches[searchIdx] if (searchState == 'active' and searchMatches) else -1

        stdscr.erase()
        drawHeader(stdscr, fileName, followMode, scrollPos, len(lines),
                   maxY, maxX, contentH,
                   searchState, searchTerm, searchIdx, len(searchMatches))
        drawContent(stdscr, lines, scrollPos, contentH, maxX,
                    searchTerm if searchState != 'none' else '',
                    searchMatchSet if searchState != 'none' else None,
                    currentMatchLine)

        if searchState == 'entry':
            drawSearchEntryBar(stdscr, maxY, maxX, searchInput)
            curses.curs_set(1)
        elif searchState == 'active':
            drawSearchActiveBar(stdscr, maxY, maxX, searchTerm, searchIdx, len(searchMatches))
            curses.curs_set(0)
        else:
            drawFooter(stdscr, maxY, maxX)
            curses.curs_set(0)

        stdscr.refresh()
        key = stdscr.getch()

        # ── Search entry mode ─────────────────────────────────────────────
        if searchState == 'entry':
            if key == 27:                                   # ESC — cancel
                searchState = 'none'
                searchInput = ''
                curses.curs_set(0)

            elif key in (curses.KEY_ENTER, 10, 13):         # Enter — confirm
                term = searchInput.strip()
                searchInput = ''
                curses.curs_set(0)
                if term:
                    searchTerm    = term
                    searchMatches = buildSearchMatches(lines, searchTerm)
                    searchMatchSet = set(searchMatches)
                    if searchMatches:
                        # Start at first match at or after current scroll pos
                        searchIdx = 0
                        for i, li in enumerate(searchMatches):
                            if li >= scrollPos:
                                searchIdx = i
                                break
                        scrollPos  = scrollToMatch(searchMatches[searchIdx], contentH, maxScroll)
                        followMode = False
                    searchState = 'active'
                else:
                    searchState = 'none'

            elif key in (curses.KEY_BACKSPACE, 127, 8):     # Backspace
                searchInput = searchInput[:-1]

            elif 32 <= key <= 126:                           # Printable char
                searchInput += chr(key)

        # ── Search active mode ────────────────────────────────────────────
        elif searchState == 'active':
            if key == 27:                                   # ESC — exit search
                searchState    = 'none'
                searchTerm     = ''
                searchMatches  = []
                searchMatchSet = set()

            elif key == curses.KEY_RIGHT:                   # Next match
                if searchMatches:
                    searchIdx  = (searchIdx + 1) % len(searchMatches)
                    scrollPos  = scrollToMatch(searchMatches[searchIdx], contentH, maxScroll)
                    followMode = False

            elif key == curses.KEY_LEFT:                    # Prev match
                if searchMatches:
                    searchIdx  = (searchIdx - 1) % len(searchMatches)
                    scrollPos  = scrollToMatch(searchMatches[searchIdx], contentH, maxScroll)
                    followMode = False

            elif key in (ord('s'), ord('S')):               # New search
                searchState = 'entry'
                searchInput = ''

            elif key in (ord('q'), ord('Q')):               # Quit viewer
                break

            # Scroll keys still work in search mode
            elif key == curses.KEY_UP:
                scrollPos  = max(0, scrollPos - 1)
                followMode = False
            elif key == curses.KEY_DOWN:
                scrollPos = min(maxScroll, scrollPos + 1)
                if scrollPos >= maxScroll:
                    followMode = True
            elif key == curses.KEY_PPAGE:
                scrollPos  = max(0, scrollPos - contentH)
                followMode = False
            elif key == curses.KEY_NPAGE:
                scrollPos = min(maxScroll, scrollPos + contentH)
                if scrollPos >= maxScroll:
                    followMode = True
            elif key == curses.KEY_HOME:
                scrollPos  = 0
                followMode = False
            elif key == curses.KEY_END:
                scrollPos  = maxScroll
                followMode = True
            elif key in (ord('f'), ord('F')):
                followMode = not followMode
                if followMode:
                    scrollPos = maxScroll
            elif key == curses.KEY_RESIZE:
                maxY, maxX = stdscr.getmaxyx()
                contentH   = max(1, maxY - 4)
                maxScroll  = max(0, len(lines) - contentH)
                if followMode:
                    scrollPos = maxScroll
            elif key == -1:                                  # Timeout → tail
                rawLines, lastPos = checkTail(filePath, lastPos, rawLines)
                lines             = preprocessLines(rawLines)
                # Rebuild matches so new lines are included
                if searchTerm:
                    searchMatches  = buildSearchMatches(lines, searchTerm)
                    searchMatchSet = set(searchMatches)
                    searchIdx      = min(searchIdx, max(0, len(searchMatches) - 1))
                maxScroll = max(0, len(lines) - contentH)
                if followMode:
                    scrollPos = maxScroll

        # ── Normal mode ───────────────────────────────────────────────────
        else:
            if key in (27, ord('q'), ord('Q')):              # ESC or Q — quit
                break

            elif key in (ord('s'), ord('S')):                # Enter search
                searchState = 'entry'
                searchInput = ''

            elif key == curses.KEY_UP:
                scrollPos  = max(0, scrollPos - 1)
                followMode = False

            elif key == curses.KEY_DOWN:
                scrollPos = min(maxScroll, scrollPos + 1)
                if scrollPos >= maxScroll:
                    followMode = True

            elif key == curses.KEY_PPAGE:                    # Page Up
                scrollPos  = max(0, scrollPos - contentH)
                followMode = False

            elif key == curses.KEY_NPAGE:                    # Page Down
                scrollPos = min(maxScroll, scrollPos + contentH)
                if scrollPos >= maxScroll:
                    followMode = True

            elif key == curses.KEY_HOME:
                scrollPos  = 0
                followMode = False

            elif key == curses.KEY_END:
                scrollPos  = maxScroll
                followMode = True

            elif key in (ord('f'), ord('F')):                # Toggle follow
                followMode = not followMode
                if followMode:
                    scrollPos = maxScroll

            elif key == curses.KEY_RESIZE:
                maxY, maxX = stdscr.getmaxyx()
                contentH   = max(1, maxY - 4)
                maxScroll  = max(0, len(lines) - contentH)
                if followMode:
                    scrollPos = maxScroll

            elif key == -1:                                  # Timeout → tail
                rawLines, lastPos = checkTail(filePath, lastPos, rawLines)
                lines             = preprocessLines(rawLines)
                maxScroll         = max(0, len(lines) - contentH)
                if followMode:
                    scrollPos = maxScroll


def openViewer(filePath: str, config: dict):
    """Launch the curses viewer for the given file path."""
    if not os.path.exists(filePath):
        print(color_text(f'\n  File not found: {filePath}', fg=RED))
        pause('  Press Enter to continue...')
        return
    curses.wrapper(viewerLoop, filePath, config)
    # Flush any stale keypresses left in the tty buffer by curses so the
    # first menu keypress after returning is never swallowed (double-entry fix)
    try:
        termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
    except Exception:
        pass


# =============================================================================
# LOG FILE SELECTOR MENU (CB9Lib)
# =============================================================================

def showHeader(subtitle: str = ''):
    clear_screen()
    header('Log Viewer', VERSION, subtitle)


def buildMenuOptions(logFiles: list[dict]) -> list[str]:
    """Build display strings for the log file selector."""
    options = []
    for entry in logFiles:
        name = entry.get('name', 'Unknown')
        path = os.path.expanduser(entry.get('path', ''))
        size = ''
        if os.path.exists(path):
            bytes_ = os.path.getsize(path)
            size   = f'{bytes_ / 1024:.1f} KB' if bytes_ < 1_048_576 else f'{bytes_ / 1_048_576:.1f} MB'
            exists = color_text('●', fg=GREEN)
        else:
            exists = color_text('○', fg=RED)
            size   = 'not found'
        options.append(f'{exists}  {color_text(name, fg=WHITE)}  {color_text(size, style=DIM)}')
    return options


def mainMenu(config: dict):
    """Display the log file selector and open chosen file in viewer."""
    logFiles = config.get('logFiles', [])

    if not logFiles:
        showHeader()
        print(color_text('\n  No log files configured in logViewConfig.json.', fg=YELLOW))
        pause('  Press Enter to exit...')
        return

    while True:
        showHeader('Select Log File')

        width   = get_width()
        options = buildMenuOptions(logFiles)

        print()
        for i, opt in enumerate(options, 1):
            print(f'  {color_text(str(i), fg=YELLOW, style=BOLD)}.  {opt}')

        print()
        print('-' * width)
        print(color_text(f'[1–{len(logFiles)}] Open  [Q/Enter] Quit  [ESC] Exit', fg=BRIGHT_YELLOW))
        print('-' * width)
        choice = collect_input().strip().lower()

        if choice in ('q', ''):
            break

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(logFiles):
                path = os.path.expanduser(logFiles[idx]['path'])
                openViewer(path, config)


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    config = load_json_config(str(CONFIG_FILE))
    if config is None:
        print(color_text(f'Error: Could not load {CONFIG_FILE}', fg=RED))
        sys.exit(1)

    try:
        mainMenu(config)
    except KeyboardInterrupt:
        pass

    do_exit()


if __name__ == '__main__':
    main()
