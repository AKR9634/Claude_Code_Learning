# Spec: Edit Expense

## Overview
Step 7 turns the `/expenses/<int:id>/edit` stub into a real edit flow. Up to now the profile page (Step 4) and the date filter (Step 6) render the user's existing expenses as read-only rows; this step adds the ability to update one of those rows in place. The user lands on a form pre-populated with the expense's current `date`, `category`, `amount`, and `description`, can change any field, and submits the form to persist the change and return to `/profile` (respecting the active date range if one is in the URL). The view must verify that the expense belongs to the currently signed-in user — an edit attempt for another user's expense returns a 404 rather than leaking its existence. Step 7 also removes the "Coming in Step 7" hint on the profile page, since the add/edit/delete flow is now in flight, and adds an "Edit" affordance on each expense row on the profile page so the edit route is reachable in one click.

## Depends on
- **Step 1 — Database setup**: requires the `expenses` table with columns `id`, `user_id`, `amount`, `category`, `date`, `description`, `created_at`, and the `get_db()` helper.
- **Step 2 — Registration**: requires `session["user_id"]` to identify the current user and scope the edit.
- **Step 4 — Profile page**: requires the `/profile` route and `profile.html` template — Step 7 reuses the profile page as the destination after a successful edit.
- **Step 6 — Date filter on profile page**: requires the `start_date` / `end_date` query string on `/profile` so that the post-edit redirect can preserve an active filter when one is in the URL.

## Routes
- `GET /expenses/<int:id>/edit` — load the expense by id, verify it belongs to the current user, render `edit_expense.html` with the current values; if the expense does not exist or belongs to another user, abort with 404; if not logged in, redirect to `/login` — logged-in only
- `POST /expenses/<int:id>/edit` — load the expense by id, verify ownership (404 otherwise), validate the submitted `date`, `category`, `amount`, and `description`, update the row, and redirect to `/profile` (preserving `start_date` / `end_date` if present); on validation failure, re-render `edit_expense.html` with the submitted values and an error message — logged-in only

No new routes for add or delete — those are separate steps. The existing `/expenses/add` and `/expenses/<int:id>/delete` stubs are unchanged.

## Database changes
No database changes. The `expenses` table from Step 1 already exposes every column this step writes to (`amount`, `category`, `date`, `description`); no new columns, tables, or indexes are introduced.

## Templates
- **Create:**
  - `templates/edit_expense.html` — extends `base.html`. Shows a centered card with a title ("Edit expense"), a back link to `/profile`, an error banner block (matching the pattern in `register.html` / `login.html`), and a form with fields for `date` (`<input type="date">`), `category` (`<select>` with the seven categories from `CATEGORIES` in `database/db.py`), `amount` (`<input type="number" step="0.01" min="0">`), and `description` (`<input type="text">` — optional). The form must submit via `POST` to `{{ url_for('edit_expense', id=expense.id) }}`. A "Save changes" submit button (`.btn-submit`) and a "Cancel" ghost link back to `/profile` round out the page. Inline a `<style>` block at the bottom for page-specific layout, using only CSS variables (no hardcoded hex).
- **Modify:**
  - `templates/profile.html` — extend the existing expense list (introduced in Step 6) with a per-row Edit affordance: add an Edit link on each `profile-expense-row` pointing to `{{ url_for('edit_expense', id=expense.id) }}` and styled to fit the row. Also remove the "Coming in Step 7" hint and the dashed border on `.profile-next` (since the placeholder is no longer forward-looking), and switch the "Add your first expense" CTA from a disabled-looking stub to a working link to `/expenses/add` (the route is still a stub returning a string, but the link itself is real and reflects that add is the next step, not this one). The date-range filter, range label, and expense rows from Step 6 are otherwise unchanged.

## Files to change
- `app.py` — replace the `edit_expense(id)` stub (currently returns `"Edit expense — coming in Step 8"`) with a real implementation handling both `GET` and `POST`:
  1. Read `session["user_id"]`; if missing, `return redirect(url_for("login"))`.
  2. Open a DB connection inside a `try` / `finally` and close it in `finally`.
  3. `SELECT id, user_id, amount, category, date, description FROM expenses WHERE id = ?` with `(id,)`. If no row is returned, OR the row's `user_id` does not match `session["user_id"]`, `return abort(404)` (do not leak the difference between "not found" and "not yours" — both look like 404 to the user).
  4. On `GET`, render `edit_expense.html` with the row's values.
  5. On `POST`, read `date`, `category`, `amount`, `description` from `request.form`. Validate: `date` is a `YYYY-MM-DD` string (use the existing `_parse_iso_date` helper or `datetime.strptime` in a `try/except ValueError`); `category` is one of the seven `CATEGORIES` from `database.db`; `amount` is a positive number (parse with `float(...)` in a `try/except ValueError`; reject `<= 0` and `NaN`/`inf`); `description` is optional and may be the empty string (trim whitespace, cap at a reasonable length such as 200 characters to keep the DB tidy).
  6. If validation fails, re-render `edit_expense.html` with the submitted values (so the user does not lose what they typed) and a short error message (`"Please fix the highlighted fields."` or per-field specifics).
  7. On success, `UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? WHERE id = ? AND user_id = ?` with the validated values plus `(id, session["user_id"])`, commit, and `return redirect(url_for("profile", start_date=start_date, end_date=end_date))` — preserving `start_date` / `end_date` from `request.args` when present so the user lands back on the filtered profile view they came from.
- `templates/profile.html` — add the per-row Edit link, drop the "Coming in Step 7" hint, and update the panel styling to reflect that this is no longer a forward-looking placeholder.

## Files to create
- `templates/edit_expense.html` — the edit form (see Templates section).

## New dependencies
No new dependencies. `sqlite3`, `datetime`, `flask.abort`, `request`, `redirect`, `url_for`, `session`, and `render_template` are all already importable in `app.py` (add `from flask import abort` if not already imported). The `CATEGORIES` tuple from `database.db` is reused.

## Rules for implementation
- No SQLAlchemy or any ORM — use `sqlite3` via `get_db()` only.
- Parameterised queries only — never interpolate values into SQL strings. Every `?` in the queries must correspond to a parameter in the `execute(...)` call.
- The view must scope every read and write to the current user. The `SELECT` filters by `id = ?`; if the row's `user_id` does not match `session["user_id"]`, abort 404. The `UPDATE` must include `AND user_id = ?` in its `WHERE` clause as a belt-and-braces safeguard in case a future refactor reorders the ownership check.
- Do not distinguish "not found" from "not yours" in the response — both return 404. This avoids leaking the existence of other users' expense ids.
- Category validation: the value must be one of the seven `CATEGORIES` defined in `database/db.py`. Import `CATEGORIES` from `database.db` and check membership — do not hardcode the list a second time in `app.py`.
- Amount validation: parse with `float(value)` inside `try/except ValueError`. Reject `0`, negatives, `NaN`, and `inf` (e.g. `math.isfinite(...)` and `amount > 0`). The form's `step="0.01"` and `min="0"` are hints only — the server is the source of truth.
- Date validation: reuse `_parse_iso_date` from `app.py` (it already exists from Step 6 and returns a `(date, used_default_bool)` tuple). If `used_default_bool` is `True`, treat the input as invalid and surface an error.
- Description: trim leading/trailing whitespace; treat empty after trim as "no description". Optionally cap at 200 characters — anything longer is truncated or rejected (pick one and apply it consistently).
- The successful redirect must preserve `start_date` and `end_date` from `request.args` when present (so a user editing from a filtered profile view lands back on the same filter). If neither is in the query string, redirect with no query string.
- Use CSS variables — never hardcode hex values. Reuse the existing global classes from `static/css/style.css` (`.auth-section`, `.auth-container`, `.auth-card`, `.form-group`, `.form-input`, `.btn-submit`, `.btn-ghost`). If new page-specific styles are needed for the edit form, inline them in a `<style>` block at the bottom of `edit_expense.html` and reference the existing CSS variables only.
- All templates extend `base.html` (use `{% extends "base.html" %}` and the `{% block content %}` / `{% block title %}` blocks). Use `url_for()` for all URL generation — including the form `action` (`url_for("edit_expense", id=expense.id)`) and the Cancel/back link (`url_for("profile")`).
- Do not introduce `flash()` / `get_flashed_messages()` in this step. Follow the existing error-banner pattern from `register.html` / `login.html`: pass an `error` variable into the template and render it in a `{% if error %}` block.
- Do not change `app.secret_key`, the navbar, the `/profile` view, or anything in the add/delete routes.

## Definition of done
- Visiting `/expenses/<id>/edit` for an expense owned by the current user, while logged in, renders `edit_expense.html` with the row's current `date`, `category`, `amount`, and `description` pre-filled.
- Visiting `/expenses/<id>/edit` while **not** logged in redirects to `/login` (HTTP 302) and does not render the edit template.
- Visiting `/expenses/<id>/edit` for an expense that does not exist, or that exists but belongs to a different user, returns HTTP 404 — the response does not distinguish "missing" from "not yours", and the template is not rendered.
- Submitting the form with a valid `date`, `category`, `amount`, and `description` updates the row in the `expenses` table, commits the change, and redirects to `/profile` (with `start_date` / `end_date` preserved if they were on the original request URL).
- Submitting the form with an invalid `amount` (non-numeric, `<= 0`, `NaN`, or `inf`) re-renders `edit_expense.html` with the user's submitted values intact and an error message; the row in the DB is unchanged.
- Submitting the form with an `amount` larger than the DB's `REAL` column can faithfully represent (e.g. > 1e308) re-renders with an error rather than crashing.
- Submitting the form with a `category` that is not one of the seven `CATEGORIES` re-renders with an error; the row in the DB is unchanged.
- Submitting the form with a malformed `date` (anything that does not match `YYYY-MM-DD` exactly) re-renders with an error; the row in the DB is unchanged.
- The per-row Edit link on the profile page points to `/expenses/<id>/edit` (via `url_for("edit_expense", id=expense.id)`, not a hardcoded path) and renders as a clear, clickable affordance on each `profile-expense-row`.
- The "Coming in Step 7" hint on the profile page is removed, and the dashed border on `.profile-next` is replaced with the same solid treatment used elsewhere so the panel no longer reads as a forward-looking placeholder.
- The edit form posts via `POST` to `url_for("edit_expense", id=expense.id)` (not a hardcoded path) and includes a Cancel link back to `/profile`.
- The page uses the existing global CSS classes (`.auth-section`, `.auth-card`, `.form-input`, `.btn-submit`, etc.) and any page-specific styles for the edit form are inlined in a `<style>` block at the bottom of `edit_expense.html` using CSS variables only — no hardcoded hex values.
- The template extends `base.html` and uses `{% block title %}` (e.g. `"Edit expense — Spendly"`) and `{% block content %}`.
- `app.py` runs without errors on port 5001. `git status` shows only the intended changes (`app.py`, `templates/edit_expense.html`, `templates/profile.html`).
