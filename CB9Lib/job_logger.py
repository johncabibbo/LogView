#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
#
# Filename:          job_logger.py
# Project:           CB9Lib
# Version:           1.0
# Description:       JobLogger — modular server job logging and alerting.
#                    Posts events to the DocInfo Manager serverJobLogAdd.php API,
#                    which writes to serverJobLog and triggers userNotifications
#                    for alerted users based on their serverJobAlertTypeId.
# Maintainer:        Cloud Box 9 Inc.
# Last Modified Date: 2026-03-21
#
# -----------------------------------------------------------------------------
# Revision History:
# -----------------------------------------------------------------------------
# v1.0 (2026-03-21)
#   • Initial release
#   • JobLogger class: log_start, log_end, log_error, log_warning, log_info
#   • Tracks warning/error counts for summary reports on job end
#   • Gracefully handles API failures (logs locally, does not raise)
# -----------------------------------------------------------------------------

import json
import datetime

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

from .func import write_log


class JobLogger:
    """
    Modular job logger for CB9 scripts.

    Posts log events to the DocInfo Manager API (serverJobLogAdd.php).
    Based on eventType, the API creates userNotifications for alerted users:

        serverJobAlertTypeId=1  All Alerts       → start, end, error, warning
        serverJobAlertTypeId=2  Start/End Alerts → start, end
        serverJobAlertTypeId=3  Errors/Warnings  → error, warning
        serverJobAlertTypeId=4  Summary Reports  → end (with summary text)

    Usage:
        jl = JobLogger(
            server_job_id = config['serverJobId'],
            api_base_url  = config['apiBaseUrl'],
            shared_secret = config['sharedSecret'],
            script_name   = SCRIPT_NAME,
            version       = VERSION,
            log_path      = log_path,   # local .log file path (str or Path), optional
        )
        jl.log_start()
        ...
        jl.log_warning("Low disk space on /var")
        jl.log_error("Connection to DB failed", details="<traceback>")
        jl.log_end(summary="Processed 42 records. 1 warning.")
    """

    _LOG_ENDPOINT = '/xhr/serverJobLogAdd.php'

    def __init__(self, server_job_id, api_base_url, shared_secret,
                 script_name, version, log_path=None):
        self.server_job_id = int(server_job_id)
        self.shared_secret = shared_secret
        self.script_name   = script_name
        self.version       = version
        self.log_path      = str(log_path) if log_path else None
        self._url          = api_base_url.rstrip('/') + self._LOG_ENDPOINT
        self._warning_count = 0
        self._error_count   = 0

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def log_start(self):
        """Log a job-start event. Notifies users with alert types 1 or 2."""
        text = f"{self.script_name} {self.version} started"
        return self._post('start', text, text)

    def log_end(self, summary=''):
        """
        Log a job-end event. Notifies users with alert types 1, 2, or 4.
        Users with type 4 receive the summary text and warning/error counts.

        Args:
            summary: Human-readable summary string (included in type-4 notifications).
        """
        text      = f"{self.script_name} {self.version} completed"
        text_full = f"{text}\n\nWarnings: {self._warning_count} | Errors: {self._error_count}"
        if summary:
            text_full += f"\n\n{summary}"

        summary_data = json.dumps({
            'summary':  summary,
            'warnings': self._warning_count,
            'errors':   self._error_count,
        })
        return self._post('end', text, text_full, summary_data=summary_data)

    def log_error(self, msg, details=''):
        """
        Log an error event. Notifies users with alert types 1 or 3.

        Args:
            msg:     Short error description (≤2000 chars).
            details: Full error detail — stack trace, raw output, etc. (optional).
        """
        self._error_count += 1
        text      = f"Error: {msg}"
        text_full = details if details else text
        if self.log_path:
            write_log(f"[ERROR] {msg}", self.log_path)
        return self._post('error', text, text_full)

    def log_warning(self, msg, details=''):
        """
        Log a warning event. Notifies users with alert types 1 or 3.

        Args:
            msg:     Short warning description (≤2000 chars).
            details: Full warning detail (optional).
        """
        self._warning_count += 1
        text      = f"Warning: {msg}"
        text_full = details if details else text
        if self.log_path:
            write_log(f"[WARN] {msg}", self.log_path)
        return self._post('warning', text, text_full)

    def log_info(self, msg, details=''):
        """
        Log an informational event. No notifications are sent.

        Args:
            msg:     Short message (≤2000 chars).
            details: Full detail (optional).
        """
        text      = msg
        text_full = details if details else text
        if self.log_path:
            write_log(f"[INFO] {msg}", self.log_path)
        return self._post('info', text, text_full)

    # -------------------------------------------------------------------------
    # Counters (read-only properties)
    # -------------------------------------------------------------------------

    @property
    def warning_count(self):
        return self._warning_count

    @property
    def error_count(self):
        return self._error_count

    # -------------------------------------------------------------------------
    # Internal
    # -------------------------------------------------------------------------

    def _post(self, event_type, text, text_full='', summary_data=None):
        """POST a log entry to the API. Returns the parsed JSON response dict."""
        if not _HAS_REQUESTS:
            msg = "'requests' library not installed — job log entry not sent."
            if self.log_path:
                write_log(f"[WARN] {msg}", self.log_path)
            return {'success': '0', 'msg': msg}

        payload = {
            'serverJobId':       self.server_job_id,
            'serverJobText':     text,
            'serverJobTextFull': text_full or text,
            'eventType':         event_type,
            'sharedSecret':      self.shared_secret,
        }
        if summary_data:
            payload['summaryData'] = summary_data

        try:
            resp   = _requests.post(self._url, data=payload, timeout=15)
            resp.raise_for_status()
            result = resp.json()
            if self.log_path and result.get('success') != '1':
                write_log(f"[WARN] Job log API warning ({event_type}): {result.get('msg','')}", self.log_path)
            return result
        except Exception as exc:
            err = f"Job log API call failed ({event_type}): {exc}"
            if self.log_path:
                write_log(f"[WARN] {err}", self.log_path)
            return {'success': '0', 'msg': str(exc)}
