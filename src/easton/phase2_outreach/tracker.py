"""
Reply + bounce tracking for Phase 2.

Two ways to ingest replies:

1. Postmark Inbound Webhook (preferred, real-time)
   - Configure Postmark to POST to an HTTPS endpoint when records@ receives mail.
   - This module exposes the handler logic; the HTTPS endpoint lives wherever
     you host it (a tiny Flask/FastAPI app on the Mac Mini behind a tunnel, or
     a Lambda, or a Cloudflare Worker).

2. Polled IMAP fallback
   - If webhooks aren't viable, poll the records@ inbox via IMAP every N minutes.
   - Slower, more brittle, but no public endpoint required.

Both paths funnel into `handle_reply()` which:
   - finds the originating outreach_log row (Message-ID header → message_id column)
   - saves any attachments under data/inbox/<county>/<filename>
   - updates outreach_log.status, reply_received_at, reply_summary, attachment_path
   - sets next_action based on detected intent (list attached / fee required / denied / etc.)
"""

from __future__ import annotations


def handle_reply(message_id: str, body: str, attachments: list[dict]) -> None:
    """
    Process one inbound email. Idempotent on message_id.

    TODO:
        - SELECT outreach_log row WHERE message_id = ?
        - classify the reply: list_received | payment_required | denied | needs_clarification | bounced
        - persist attachments to data/inbox/<state>_<county>/<filename>
        - UPDATE outreach_log set status, reply_received_at, etc.
    """
    raise NotImplementedError("Implement when starting Phase 2.")
