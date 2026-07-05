# Log View

**An interactive terminal log viewer — pick a log, tail it live, scroll history, and search.**

`logView.py` lists the log files you care about in a menu, then opens the one you choose in a full-screen viewer. Follow it live (tail), scroll back through history with the arrow keys, and search within it — all with ANSI colors preserved. CB9Lib is bundled.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Alias Setup — Run From Anywhere](#alias-setup--run-from-anywhere)
6. [Configuration](#configuration)
7. [Usage & Examples](#usage--examples)
8. [Troubleshooting](#troubleshooting)
9. [License / Copyright](#license--copyright)

---

## Overview

Instead of remembering long `tail -f` paths, keep your important logs in one config and open any of them from a menu. The viewer keeps ANSI colors intact and adds live-follow, scrolling, and in-file search.

---

## Features

- **Menu of log files** — defined once in config; select and open.
- **Live follow (tail)** — watch new lines as they arrive.
- **Scroll history** — arrow keys move through the file.
- **Search (`[S]`)** — find a term; `←/→` jump between matches. Current match is highlighted black-on-white, others black-on-yellow; a `SEARCH` badge shows an `N/M` counter.
- **ANSI color support** — colored logs render correctly.
- **Instant ESC** — exits search / viewer promptly.

---

## Requirements

| Requirement | Notes |
|-------------|-------|
| **macOS / Linux** | Uses `curses` / a Unix terminal — not native Windows. |
| **Python 3.10+** | CB9Lib is **bundled** — no separate install. |

---

## Installation

```bash
git clone <REPOSITORY_URL> LogView
cd LogView
python3 logView.py
```

---

## Alias Setup — Run From Anywhere

Launch from any directory by typing `logview`.

### macOS / Linux (zsh or bash)

Add to `~/.zshrc` or `~/.bashrc`:

```bash
alias logview='python3 ~/path/to/LogView/logView.py'
```

Reload and run:

```bash
source ~/.zshrc
logview
```

**Alternative — symlink onto your `PATH`:**

```bash
chmod +x ~/path/to/LogView/logView.py
ln -s ~/path/to/LogView/logView.py /usr/local/bin/logview
```

> **Windows:** the `curses` viewer isn't supported natively — use **WSL**.

---

## Configuration

Edit **`logViewConfig.json`** — a list of the logs to show in the menu:

```json
{
  "logFiles": [
    { "name": "Claude Commands", "path": "~/Documents/log/claudeCommands.log" },
    { "name": "Backup42",        "path": "~/Documents/log/backup42.log" },
    { "name": "Git Push All",    "path": "~/Documents/log/gitPushAll.log" }
  ]
}
```

| Key | Description |
|-----|-------------|
| `name` | Label shown in the menu. |
| `path` | Path to the log file (`~/` is expanded). |

---

## Usage & Examples

```bash
python3 logView.py
```

1. Choose a log from the menu.
2. In the viewer: follow live, scroll with the arrow keys, press `[S]` to search.
3. While searching: `←/→` move between matches, `ESC` exits search, `ESC` again leaves the viewer.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| A log is missing from the menu | Add it to `logFiles` in `logViewConfig.json`. |
| "File not found" on open | Check the `path` (and that the log has been created). |
| Colors look wrong | Ensure your terminal supports ANSI colors and isn't overriding them. |
| ESC feels laggy | Fixed in recent versions (ESC delay lowered) — use the current build. |

---

## License / Copyright

---
**Version:** 1.06
**Author:** Cloud Box 9 Inc.
**Maintainer / Owner:** Cloud Box 9 Inc.
**Last Updated:** Jul 5, 2026

Copyright © 2026 Cloud Box 9 Inc. All rights reserved.
