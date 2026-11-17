# Contributing

Thanks for helping. Small, focused pull requests are easiest to review.

## Before you start

- Open an issue for anything larger than a bug fix or a new scraper, so we can agree on
  the approach first.
- Security problems: do **not** open an issue. Follow [SECURITY.md](SECURITY.md).

## Setup

See the "Getting started" section of the [README](README.md). Use your own Supabase
project and your own keys. Never commit `.env`, `.env.local` or any key.

## Workflow

1. Fork the repo and branch from `main` (`feature/<topic>` or `fix/<topic>`).
2. Make your change and add or update tests.
3. Run the checks:
   ```bash
   uv run --extra dev pytest
   uv run --extra dev ruff check .
   cd frontend && npm run lint && npm run build
   ```
4. Open a pull request describing what changed and why. Link the issue.

## Guidelines

- **Python:** formatted and linted with `ruff`; type hints on new code; manage
  dependencies with `uv` (commit `uv.lock`, no `requirements.txt`).
- **Frontend:** TypeScript, keep the app a static export (no server-only features).
- **Database:** add a new numbered file in `supabase/migrations/`; never edit an applied
  migration. Every new table needs row-level security. Openings are shared; anything
  about a user must be private to that user.
- **Edge Functions:** validate input, rate-limit, and never log secrets, CVs or AI keys
  (use `agents/redact.py` in agents).
- **Scrapers:** add one in `agents/search/scrapers/`, register it in `registry.py`.
  Respect each site's terms and `robots.txt`, keep request rates low, and do not add
  scrapers that need logins or violate a site's terms.
- **Workflows:** pin third-party actions to a commit SHA and keep permissions minimal.
- **Commits:** short imperative subject, e.g. `Add Euraxess deadline parsing`.

## Reporting bugs

Include what you expected, what happened, steps to reproduce, and logs with any personal
data or keys removed.

By contributing you agree your work is released under the [MIT License](LICENSE).
