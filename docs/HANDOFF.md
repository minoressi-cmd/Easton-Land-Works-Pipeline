# Handoff — Moving to the Mac Mini

This doc exists because the pipeline was scaffolded on a Mac Air under one Claude account,
and will be developed/operated long-term on a Mac Mini under the Easton Land Works Claude
account. **Claude conversation history does NOT move between accounts.** Anything the
new Claude needs to know lives in this repo, not in chat memory.

If you're a fresh Claude reading this on the Mac Mini: welcome. Read every doc in `/docs/`
and skim `src/easton/db.py` before touching anything. That'll get you up to speed.

---

## One-time setup on the Mac Mini

```bash
# Prereqs (one-time, install via Homebrew)
brew install python@3.11 tesseract poppler git

# Get the code
git clone <repo-url> ~/easton-pipeline
cd ~/easton-pipeline

# Python env
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Secrets — copy values from the Mac Air's .env, NOT from anywhere committed
cp .env.example .env
# Fill .env with the same keys you used on the Air

# Database — two options:
#   A) Fresh start (recommended for first migration)
python scripts/init_db.py
#   B) Copy the working DB from the Air via AirDrop or scp:
#      scp macair:~/easton-pipeline/data/pipeline.db data/pipeline.db
```

## What's NOT in this repo (and where it lives)

| Thing | Where | Why excluded |
|---|---|---|
| API keys | `.env` (gitignored) | Secrets never go in Git. |
| `data/pipeline.db` | Local file | Has owner PII; keep off Git. Back up separately. |
| Received county sheets | `data/inbox/` | Same as DB — PII. |
| Sending domain DNS records | Postmark dashboard + domain registrar | Live config, not code. |

## Sanity-check after migration

```bash
# DB schema present
python -c "from easton.db import get_conn; print([r[0] for r in get_conn().execute(\"SELECT name FROM sqlite_master WHERE type='table'\")])"

# Should print: ['states', 'counties', 'outreach_log', 'leads_raw', 'leads_filtered', 'leads_enriched']

# Config loads
python -c "from easton.db import load_states_config; print(list(load_states_config().keys()))"
```

## Where to leave breadcrumbs for the next Claude

When you finish a work session, before closing the chat:

1. Append a short entry to `docs/DECISIONS.md` for any non-obvious choice made.
2. If you stopped mid-task, write the next step into `docs/NEXT.md` (create the file).
3. Commit + push. The next Claude reads `git log --oneline -20` to catch up.

This is how continuity survives the account switch.
