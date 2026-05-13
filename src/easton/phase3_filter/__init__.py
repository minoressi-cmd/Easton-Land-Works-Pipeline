"""
Phase 3 — Parse received sheets + filter.

Input: files in data/inbox/<state>_<county>/<filename>, referenced by
outreach_log.attachment_path with status='list_received'.

Output:
- One row per parcel in leads_raw (preserving original data as JSON in raw_data).
- One row per parcel in leads_filtered with is_entity flag set.

Adapters per format (csv, xlsx, pdf) live in adapters/.
Filter rules live in filters.py and pull from config/filters.yaml.

NOTE on acreage: we DO NOT filter by acre range here. Many county lists don't
include acreage. That filter happens in Phase 4 after Zamplo enriches it.
The LLC/entity flag IS set here so we can skip entity rows before paying
Zamplo credits.
"""
