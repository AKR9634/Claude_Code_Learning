# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

**Spendly** is a personal expense tracker built with Flask + SQLite. It is structured as a **step-by-step teaching project**: students fill in features incrementally (database setup, auth, expenses CRUD, reports) while the surrounding scaffolding (routes, templates, styles) is already in place.

## Project layout

- `app.py` — Flask routes. Implemented: `landing`, `register`, `login`, `terms`, `privacy`, plus stub routes for `logout`, `profile`, and expenses (`add`, `edit`, `delete`) that return placeholder strings. Entry point runs the dev server on **port 5001** in debug mode.
- `database/db.py` — **Stub. To be implemented.** Should expose `get_db()` (returns SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (CREATE TABLE IF NOT EXISTS), and `seed_db()`.
- `templates/` — Jinja2 templates extending `base.html`. Implemented: `base.html`, `landing.html`, `register.html`, `login.html`, `terms.html`, `privacy.html`.
- `static/css/style.css`, `static/js/main.js` — Shared assets. `main.js` is currently a placeholder; inline `<script>` blocks are used for page-specific behavior (e.g. the landing-page video modal).
- `requirements.txt` — flask, werkzeug, pytest, pytest-flask.

## Conventions

- **Templates extend `base.html`.** Use `{% block content %}`, `{% block title %}`, `{% block head %}`, `{% block scripts %}`. All template URLs go through `{{ url_for('endpoint') }}`, not hardcoded paths.
- **Styles:** Global classes live in `static/css/style.css` (`.btn-primary`, `.btn-ghost`, `.btn-submit`, `.form-input`, `.auth-section`, `.hero-*`, `.feature-card`, `.terms-container`, etc.). Page-specific styles are typically inlined in a `<style>` block at the bottom of the template — match that pattern rather than adding to the global stylesheet.
- **JS:** Vanilla only. No external libraries. Page-specific scripts go in an inline `<script>` block at the bottom of the template; shared behavior goes in `static/js/main.js`.
- **Stubbed routes** return plain strings like `"Add expense — coming in Step 7"` and reference the step in which they will be implemented.
- **Port:** Dev server runs on `5001`, not the Flask default `5000`.

## Commands

```bash
# Activate the existing virtualenv
Claude_Code\Scripts\Activate.ps1   # PowerShell
# source Claude_Code/bin/activate  # bash

# Install dependencies
pip install -r requirements.txt

# Run the dev server
python app.py
# → http://localhost:5001

# Run tests (pytest + pytest-flask are preinstalled)
pytest
```

## Notes for future sessions

- The repo is a tutorial codebase. When asked to add a feature, look for the matching stub route or `TODO` comment first — most "missing" pieces are intentional scaffolds.
- `database/db.py` is intentionally empty pending Step 1. Don't try to wire up persistence until that file is filled in.
- The `.gitignore` excludes `expense_tracker.db`, `venv/`, and `.claude/plans/`.
- `hero.png` at the repo root is a design reference, not an asset (assets live in `static/`).
