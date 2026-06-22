# Spec: Date Filter for Profile Page

## Overview
Step 6 adds a date range filter to the `/profile` page so users can narrow the expenses shown on their profile to a specific window. The profile page (Step 4) currently shows a forward-looking placeholder panel for expenses; this step keeps that placeholder structure but makes the dates dynamic by reading query parameters (`start_date`, `end_date`) from the URL, validating them as `YYYY-MM-DD` strings, and using the chosen range to scope the (still placeholder) list of expenses shown to the user. With no query parameters, the page defaults to the current month (1st of this month through today). Invalid or malformed date strings are ignored — the page falls back to the default range rather than raising. Because the actual expenses CRUD lives in Step 7 (and beyond), this step introduces the filter UI, URL handling, and validation, and renders an empty-state list of expenses filtered by the chosen window so that Step 7 can drop straight into populating real rows. The filter applies only to the profile's own expenses view — the navbar and the rest of the page are unchanged.

## Depends on
- **Step 1 — Database setup**: requires the `expenses` table (with columns `id`, `user_id`, `amount`, `category`, `date`, `description`, `created_at`) and the `get_db()` helper from `database/db.py`. The date filter is a no-op until expenses exist, but the schema must already have the `date TEXT` column in `YYYY-MM-DD` format so that range comparisons (`date BETWEEN ? AND ?`) work.
- **Step 2 — Registration**: requires the `session["user_id"]` and `session["user_name"]` session keys to identify which user to filter expenses for.
- **Step 4 — Profile page**: requires the existing `GET /profile` route (which loads the user's `name`, `email`, `created_at` from `users`), the `templates/profile.html` template, and the navbar greeting/Sign-out form. This step extends both the route and the template rather than replacing them.

## Routes
- `GET /profile?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — load the current user, parse optional `start_date` and `end_date` query parameters, validate them as `YYYY-MM-DD` strings, query the `expenses` table for the current user's rows whose `date` falls within the chosen window (inclusive), and render `profile.html` with the user, the chosen date range, and the filtered expense list. If a parameter is missing or invalid, fall back to the default range (1st of the current month through today). If not logged in, redirect to `/login` — logged-in only

No new POST routes. No changes to `/login`, `/register`, `/logout`, or any other existing route.

## Database changes
No database changes. The `expenses.date` column already exists from Step 1 as a `TEXT` field stored in `YYYY-MM-DD` format, which is the format this filter reads and writes. No new columns, tables, indexes, or constraints are introduced in this step.

## Templates
- **Create:** none
- **Modify:**
  - `templates/profile.html` — extend the existing forward-looking expenses panel from Step 4 to accept a date filter form:
    1. Add a date-range form (two `<input type="date">` fields labeled `start_date` and `end_date`, plus a "Apply" submit button) at the top of the expenses placeholder panel. The form must submit via `GET` to `{{ url_for("profile") }}` so the chosen range appears in the URL and is shareable/bookmarkable.
    2. Render the chosen range as a small label above the expenses list (e.g. `"Showing expenses from 2026-06-01 to 2026-06-22"`). When the default range is in effect, the label should still read clearly (e.g. `"Showing expenses from {start} to {end} (this month)"`).
    3. Render the filtered expenses list. For this step, the list contains placeholder rows (since Step 7 hasn't built CRUD yet) — but the **filtering logic must already work**: the template must loop over the `expenses` collection passed from the view and render each row's `date`, `category`, `amount`, and `description`. If the list is empty, show the existing empty-state message.
    4. Preserve the existing profile header (name, email, member-since line) and the link to `/expenses/add` from Step 4 — those parts of the page are not touched by this step.
  - **No change** to `base.html` — the navbar greeting/Sign-out form from Step 3 already works with the filtered profile URL.

## Files to change
- `app.py` — modify the `profile` view to:
  1. Continue reading `session["user_id"]` and redirecting to `/login` if missing.
  2. Read `start_date` and `end_date` from `request.args`.
  3. Validate each as `YYYY-MM-DD` using a small helper (e.g. parse with `datetime.strptime(s, "%Y-%m-%d")` inside a `try/except ValueError`; on failure, drop that parameter and fall back to the default). The helper should be a small inner function or a top-level helper in `app.py` — it does **not** belong in `database/db.py`.
  4. Compute the default range: `start_date` = first day of the current month (`today.replace(day=1).isoformat()`), `end_date` = today (`date.today().isoformat()`).
  5. After the existing `users` lookup, query `SELECT date, category, amount, description FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date DESC, id DESC` with `(session["user_id"], start_date, end_date)`.
  6. Open the DB connection inside a single `try` / `finally` and call `conn.close()` in `finally`, matching the style of every other route in `app.py`.
  7. Render `profile.html` with `user`, `start_date`, `end_date`, and `expenses` (the list of rows).
- `templates/profile.html` — add the date-range filter form, the range label, and the loop over `expenses` inside the existing placeholder panel (see Templates section).

## Files to create
None.

## New dependencies
No new dependencies. `datetime` is in the Python standard library (the `date` class is already imported by `database/db.py`); `request` and `url_for` are already imported in `app.py`.

## Rules for implementation
- No SQLAlchemy or any ORM — use `sqlite3` via `get_db()` only.
- Parameterised queries only — never interpolate values into SQL strings. The expense query is `SELECT date, category, amount, description FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date DESC, id DESC`.
- Passwords are not handled in this step, but the rule still applies: never compare or store plaintext passwords. (Carry-over from Steps 2–3.)
- The `/profile` view **must** check for `session["user_id"]` first. If it is missing, redirect to `/login` exactly as Step 4 did — this filter does not change auth behavior.
- Date validation: use `datetime.strptime(s, "%Y-%m-%d")` inside a `try/except ValueError`. On failure, the parameter is treated as missing and the default is used. Do **not** accept other formats (e.g. `MM/DD/YYYY`), do **not** accept free-text, and do **not** raise.
- If `start_date` is valid but `end_date` is missing/invalid, use the default `end_date`. If `end_date` is valid but `start_date` is missing/invalid, use the default `start_date`. If both are missing, use both defaults. If both are invalid, use both defaults.
- If the parsed `start_date` is **after** the parsed `end_date`, swap them (so `start <= end`) before querying. Do not reject the input — silently correct it.
- The query window is inclusive on both ends (`date BETWEEN ? AND ?`), matching SQL's default `BETWEEN` semantics.
- The expenses query must be scoped to the current user (`user_id = ?` with `session["user_id"]`) — never return another user's expenses.
- Only select the columns the template renders: `date`, `category`, `amount`, `description`. Do **not** select `password_hash` (it's not even in this table, but the rule generalizes) or any other internal column.
- Use CSS variables — never hardcode hex values. Reuse the existing global classes from `static/css/style.css` (`.auth-section`, `.auth-card`, `.feature-card`, `.btn-primary`, `.btn-ghost`, `.btn-submit`, `.form-input`). If new page-specific styles are needed for the date-range form, inline them in a `<style>` block at the bottom of `profile.html` and reference the existing CSS variables only.
- All templates extend `base.html` (already the case for `profile.html` — preserve it). Use `{% block content %}`, `{% block title %}`, `{% block head %}`, and `{% block scripts %}` as appropriate.
- Use `url_for()` for all URL generation — including the date-range form `action` (`url_for("profile")`).
- Do not introduce `flash()` / `get_flashed_messages()` in this step. The filter is purely GET-driven; any "invalid date" cases fall back silently to the default range.
- Do not change `app.secret_key`, the navbar, or anything outside the `profile` view and `profile.html`.

## Definition of done
- Visiting `/profile` while **not** logged in redirects to `/login` (HTTP 302) and does not render the profile template.
- Visiting `/profile` (no query string) while logged in renders `profile.html` showing the default range (`{first-of-this-month}` through `{today}`), the user's name/email/member-since line from Step 4, and an empty-state placeholder for the expenses list (because Step 7 hasn't built CRUD yet, the demo seed from Step 1 only includes the `demo@spendly.com` user, so logging in as that user should show the seeded expenses scoped to this month).
- Visiting `/profile?start_date=2026-06-01&end_date=2026-06-30` while logged in renders the same page but with the chosen range shown in the label and the expenses list filtered to that window.
- Visiting `/profile?start_date=2026-06-15&end_date=2026-06-10` (start after end) renders the page with the dates silently swapped, so the query is `BETWEEN '2026-06-10' AND '2026-06-15'`.
- Visiting `/profile?start_date=invalid&end_date=2026-06-30` renders the page with the default `start_date` and the chosen `end_date` — no error, no 500.
- Visiting `/profile?start_date=06/01/2026&end_date=06/30/2026` (wrong format) renders the page with both dates defaulted — no error, no 500.
- The date-range form on the page submits via `GET` to `/profile` (the action is `url_for("profile")`, not a hardcoded `/profile`), and the chosen dates appear in the resulting URL so the filtered view is bookmarkable/shareable.
- The expenses query never returns rows belonging to a different user — verified by logging in as the demo user and confirming only the seeded expenses for that user appear.
- The page uses existing global CSS classes (`.auth-section`, `.auth-card`, etc.) and any page-specific styles for the date-range form are inlined in a `<style>` block at the bottom of `profile.html` using CSS variables only — no hardcoded hex values.
- The template extends `base.html` and uses `{% block title %}` (e.g. `"Your profile — Spendly"`) and `{% block content %}`.
- The navbar greeting/Sign-out form from Step 3 continues to work on `/profile` (carried over from Steps 3 and 4).
- `app.py` runs without errors on port 5001. `git status` shows only the intended changes (`app.py`, `templates/profile.html`).
