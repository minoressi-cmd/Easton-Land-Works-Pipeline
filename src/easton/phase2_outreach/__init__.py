"""
Phase 2 — Email outreach.

Goal: for every county with a verified email, send a records-request email
asking for their current tax-delinquent property list.

Key design notes:
- Sender domain must be DIFFERENT from the operator's main email. Use
  records@eastonlandworks.com or similar dedicated subdomain.
- Warm up the domain over 2 weeks. EMAIL_DAILY_CAP in .env caps the sender.
- Frame as a public records request, NOT a sales ask. Cite the relevant
  state statute pulled from `states.statute_citation`.
- Every send is logged in `outreach_log`. Replies and bounces feed back in
  via webhook or polled inbox.
"""
