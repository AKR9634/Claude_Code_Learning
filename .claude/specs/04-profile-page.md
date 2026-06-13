# Spec: Profile Page

## Overview
Step 4 turns the `/profile` route from a placeholder string into the user's first authenticated landing surface. After registering (Step 2) or logging in (Step 3), users are redirected to `/profile`, so it must do three things in this step: (1) require a session — anonymous visitors are bounced to `/login`; (2) load the current user's `id`, `name`, `email`, and `created_at` from the `users` table and pass them to the template; (3) render a profile page that uses the existing light-mode fintech style and links forward to the expenses work coming in Step 7. This step does **not** introduce edit/delete, avatar upload, password change, or any expenses logic — those are separate steps. Profile is the read-only "you are signed in as …" view that every later authenticated feature will return to.

## Depends on
- **Step 1 — Database setup**: requires the `users` table (with columns `id`, `name`, `email`, `password_hash`, `created_at`) and the `get_db()` helper from `database/db.py`.
- **Step 2 — Registration**: requires the `session["user_id"]` and `session["user_name"]` session keys that the registration flow sets on success. The profile view trusts `session["user_id"]` to identify which user to load.
- **Step 3 — Login and Logout**: requires the same session keys to be set on login, the navbar's logged-in greeting + sign-out button, and the `POST /logout` endpoint. This step reuses the navbar from Step 3; do not re-implement it.

## Routes
- `GET /profile` — load the current user by `session["user_id"]`, render `profile.html`; if not logged in, redirect to `/login` — logged-in only

No new POST routes in this step. Edit profile / delete account / change password are out of scope and belong to future steps.

## Database changes
No database changes. The `users` table from Step 1 is sufficient — `id`, `name`, `email`, and `created_at` are already present and exposed via `get_db()`.

## Templates
- **Create:**
  - `templates/profile.html` — extends `base.html`. Shows a profile header with the user's name, a profile card with email, member-since date (formatted from the `created_at` string), and a "placeholder" panel that points forward to the upcoming expenses steps (e.g. an empty state with a disabled "Add your first expense" button and a "Coming in Step 7" hint). The page must use the existing global classes (`.auth-section`, `.auth-card`, `.feature-card`) and inline a small `<style>` block at the bottom for any page-specific layout, matching the convention in `landing.html`, `register.html`, and `login.html`.
- **Modify:** none. The navbar from Step 3 already shows the greeting + "Sign out" form for logged-in users, which is what `/profile` needs.

## Files to change
- `app.py` — replace the stub `profile()` view (currently returns the string `"Profile page — coming in Step 4"`) with a real implementation: read `session["user_id"]`; if it is not set, `return redirect(url_for("login"))`; otherwise look up `name`, `email`, `created_at` from `users` by id, render `profile.html` with those values, and close the connection in a `finally` block.

## Files to create
- `templates/profile.html` — the page itself (see Templates section).

## New dependencies
No new dependencies. The existing `sqlite3` connection, `session`, `redirect`, `url_for`, and `render_template` imports already cover everything this step needs.

## Rules for implementation
- No SQLAlchemy or any ORM — use `sqlite3` via `get_db()` only.
- Parameterised queries only — never interpolate values into SQL strings. The lookup query is `SELECT name, email, created_at FROM users WHERE id = ?`.
- The `/profile` view **must** check for `session["user_id"]` first. If it is missing, redirect to `/login` with a `return redirect(url_for("login"))` — do not render the page, do not raise, do not return a 401. This is the standard pattern for every future authenticated route.
- Open the DB connection inside a `try` / `finally` and call `conn.close()` in the `finally` block, matching the style already used by `/register` and `/login` in `app.py`.
- Only select the columns the template actually needs: `name`, `email`, `created_at`. Do **not** select `password_hash` and pass it to the template — it is never rendered and never should be.
- `created_at` is stored as a `datetime('now')` string in the `users` table. Format it in the template for display (e.g. `"Member since " + formatted date`). If a simple split on the space character is used to extract the date, that is acceptable for this step — full date parsing is not required.
- Use CSS variables — never hardcode hex values. Reuse the existing global classes from `static/css/style.css` (`.auth-section`, `.auth-container`, `.auth-card`, `.btn-primary`, `.btn-ghost`, `.feature-card`, `.feature-icon`, `.feature-title`, `.feature-body`) for layout. If new page-specific styles are needed (e.g. a profile header layout), inline them in a `<style>` block at the bottom of `profile.html` and reference the existing CSS variables only.
- All templates extend `base.html` (use `{% extends "base.html" %}` and the `{% block content %}` / `{% block title %}` blocks).
- Use `url_for()` for all URL generation — including any "Add expense" link (`url_for("add_expense")` is fine; the route exists as a stub).
- Do not introduce `flash()` / `get_flashed_messages()` in this step — the existing auth templates use a `{% if error %}` block instead, and that pattern is not needed for a read-only profile view.
- Do not change `app.secret_key` or anything in the navbar from Step 3.
- Do not add edit-profile, delete-account, change-password, or avatar-upload UI in this step — those are out of scope and should be left for a future step.

## Definition of done
- Visiting `/profile` while **not** logged in redirects to `/login` (HTTP 302) and does not render the profile template.
- Visiting `/profile` while logged in (after `/register` or `/login`) renders `profile.html` showing the user's name, email, and a "Member since" line derived from `created_at`.
- The `password_hash` column is never selected by the profile query and never appears in the rendered HTML.
- The page uses the existing global CSS classes (e.g. `.auth-section`, `.auth-card`) and any page-specific styles are inlined in a `<style>` block at the bottom of `profile.html` using CSS variables only — no hardcoded hex values.
- The navbar continues to show "Hi, {name}" and a "Sign out" form for logged-in users (carried over from Step 3), and the "Sign out" button still POSTs to `/logout` and redirects to `/`.
- The template extends `base.html` and uses `{% block title %}` (e.g. `"Your profile — Spendly"`) and `{% block content %}`.
- The page includes a forward-looking placeholder panel that points to Step 7 (expenses) and links (with `url_for("add_expense")`) to the stub route — clicking the link should land on the existing stub string `"Add expense — coming in Step 7"`, not a 404.
- `app.py` runs without errors on port 5001. `git status` shows only the intended changes (`app.py`, `templates/profile.html`).
