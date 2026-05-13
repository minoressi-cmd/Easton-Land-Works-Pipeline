"""
Phase 4 — Zamplo enrichment.

For each row in leads_filtered where:
    needs_zamplo_enrichment = 1 AND is_entity = 0 (or trust override)

...call the Zamplo API to pull parcel data + owner enrichment + GIS + estimated value.

Persist results into leads_enriched. Apply the final acre-range filter
(config/filters.yaml: 5-20 acres) and flag ready_for_mailer.

API specifics: see client.py. You'll need to fill in exact endpoint paths after
talking to Zamplo support to confirm their API contract.
"""
