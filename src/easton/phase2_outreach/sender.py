"""
Email sender for Phase 2.

Uses Postmark by default (see requirements.txt). Swap the provider by
replacing the `_send_via_provider` function — the rest of the module is
provider-agnostic.

Rate limit: respects EMAIL_DAILY_CAP from .env. Reads today's send count
from `outreach_log` before sending. Refuses to exceed the cap.
"""

from __future__ import annotations

import os
from pathlib import Path

from easton.db import get_conn, transaction


TEMPLATES_DIR = Path(__file__).parent / "templates"


def render_template(template_name: str, context: dict) -> tuple[str, str]:
    """
    Load templates/{template_name}.txt, substitute {var} placeholders.
    Returns (subject, body). First line of file is the subject.

    TODO: implement using str.format_map or jinja2 (already in deps via beautifulsoup
    transitive; consider adding jinja2 explicitly if templates get complex).
    """
    raise NotImplementedError("Implement when starting Phase 2.")


def send_records_request(county_id: int, dry_run: bool = True) -> str | None:
    """
    Send (or simulate) a records request to one county. Logs to outreach_log.

    Returns the provider's message_id on success, None on dry_run.

    TODO:
        - load county row + its state's statute_citation
        - check daily cap
        - render template
        - call _send_via_provider unless dry_run
        - insert into outreach_log with status='sent'
    """
    raise NotImplementedError("Implement when starting Phase 2.")


def _send_via_provider(to_email: str, subject: str, body: str) -> str:
    """Postmark-specific send. Returns message_id."""
    raise NotImplementedError
