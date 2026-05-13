# Decision Log

Append-only log of non-obvious decisions, in reverse chronological order.
New entries go at the TOP. Each entry: date, decision, why, tradeoff accepted.

---

## 2026-05-11 — Scaffolding initialized

**Decision:** Python + SQLite + file-based config, no web UI yet.
**Why:** Portable across Macs, no infra to manage, easy to hand off between Claude accounts.
**Tradeoff:** No remote access — pipeline only runs on the machine that has the DB.

**Decision:** Pipeline split into 4 phases with separate scripts.
**Why:** Different failure modes per phase; want to re-run any phase independently.
**Tradeoff:** More files; orchestration is manual until a wrapper script exists.

**Decision:** Target acre range 5–20 hardcoded in `config/filters.yaml`.
**Why:** Easton Land Works standard buy box.
**Tradeoff:** If the box changes, edit one file. Not a CLI flag for now.

**Decision:** Acre filtering deferred to Phase 4 (post-Zamplo).
**Why:** Most county lists don't ship acreage. Zamplo adds it.
**Tradeoff:** We pay Zamplo credits to enrich rows that may fail the acre filter.
We could pre-filter via free GIS APIs (e.g. county parcel viewers) but that's a Phase 5 optimization.

**Decision:** Postmark over Mailgun/SES for Phase 2.
**Why:** Better deliverability on transactional / records-request style email; less abuse-reporting noise on a fresh domain.
**Tradeoff:** Slightly higher cost than SES. Worth it given the audience is county officials whose spam filters are aggressive.

**Decision:** Wyoming as the first state.
**Why:** 23 counties is small enough to validate the end-to-end flow in one week.
**Tradeoff:** WY isn't necessarily Easton's highest-priority state for actual buying. It's a build target, not a business target.

---

## Template for future entries

```
## YYYY-MM-DD — short title

**Decision:**
**Why:**
**Tradeoff:**
```
