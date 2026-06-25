# Spec: Delete Expense

## Overview
Step 8 turns the `/expenses/<int:id>/delete` stub into a real delete flow. Up to now the profile page (Step 4), date filter (Step 6), and edit route (Step 7) let the user browse, filter, and edit expenses, but there is no way to remove an expense that was logged in error. This step adds a per-row Delete affordance on the profile page that submits a form to delete the row, then redirects back to `/profile` (respecting the active date range if one is in the URL). The view must verify that the expense belongs to the currently signed-in user — a delete attempt for another user's expense returns a 404 rather than leaking its existence. Step 8 also introduces a small `confirm_delete_expense.html` confirmation page so users do not accidentally lose data by clicking the wrong button, and replaces the existing GET-only stub with a proper `POST`-only view (deletes must never be reachable via a plain link, to protect against CSRF-style prefetching and to follow the Post/Redirect/Get convention).

## Depends on
- **Step 1 — Database setup**: requires the `expenses` table with columns `id`, `user_id`, and the `get_db()` helper.
- **Step 2 — Registration**: requires `session["user_id"]` to identify the current user and scope the delete.
- **Step 4 — Profile page**: requires the `/profile` route and `profile.html` template — Step 8 reuses the profile page as the destination after a successful delete.
- **Step 6 — Date filter on profile page**: requires the `start_date` / `end_date` query string on `/profile` so that the post-delete redirect can preserve an active filter when one is in the URL.
- **Step 7 — Edit expense**: requires the existing per-row layout on `profile.html` (`profile-expense-row`) so the Delete affordance can be added next to the Edit link without restructuring the row.

## Routes
- `GET /expenses/<int:id>/delete` — load the expense by id, verify it belongs to the current user, render `confirm_delete_expense.html` with the expense details; if the expense does not exist or belongs to another user, abort with 404; if not logged in, redirect to `/login` — logged-in only
- `POST /expenses/<int:id>/delete` — load the expense by id, verify ownership (404 otherwise), delete the row, and redirect to `/profile` (preserving `start_date` / `end_date` if present); if not logged in, redirect to `/login`; **never** delete on `GET` — logged-in only

## Database changes
No database changes. The `expenses` table from Step 1 already has `id` (the primary key the `DELETE` filters on) and `user_id` (used in the ownership check and `WHERE` clause); no new columns, tables, or indexes are introduced.

## Templates
- **Create:**
  - `templates/confirm_delete_expense.html` — extends `base.html`. Shows a centered card with a title ("Delete expense?"), a short summary of the row being deleted (date, category, amount, description — read-only, so the user can confirm they are deleting the right one), and two actions: a "Yes, delete" submit button (`.btn-submit`) wrapped in a `<form method="post">` that posts to `{{ url_for("delete_expense", id=expense.id) }}`, and a "Cancel" ghost link back to `/profile` (preserving the active date range via `{{ url_for("profile", start_date=start_date, end_date=end_date) }}`). No error banner is needed on this page — the only failure mode is 404, which is handled by `abort`. Inline a `<style>` block at the bottom for page-specific layout, using only CSS variables (no hardcoded hex).
- **Modify:**
  - `templates/profile.html` — extend each `profile-expense-row` with a Delete affordance that submits a small inline form (the form approach is intentional — it lets us use `POST`, which the delete view requires). Each row gets a `<form method="post" action="{{ url_for('delete_expense', id=expense.id) }}">` containing a single "Delete" submit button styled like the existing Edit link/button (or a small `.btn-ghost` variant) so the affordance is clearly clickable but not visually louder than Edit. The button submits via POST, the view handles the delete, and the user lands back on `/profile` with the date filter intact.

## Files to change
- `app.py` — replace the `delete_expense(id)` stub (currently a `GET` route returning `"Delete expense — coming in Step 9"`) with a real implementation handling both `GET` (confirmation page) and `POST` (actual delete):
  1. Read `session["user_id"]`; if missing, `return redirect(url_for("login"))`.
  2. Open a DB connection inside a `try` / `finally` and close it in `finally`.
  3. `SELECT id, user_id, date, category, amount, description FROM expenses WHERE id = ?` with `(id,)`. If no row is returned, OR the row's `user_id` does not match `session["user_id"]`, `return abort(404)` (do not leak the difference between "not found" and "not yours" — both look like 404 to the user).
  4. On `GET`, render `confirm_delete_expense.html` with the row's values plus `start_date` and `end_date` from `request.args` (so the Cancel link can round-trip back to the filtered profile view).
  5. On `POST`, run a parameterised `DELETE FROM expenses WHERE id = ? AND user_id = ?` with `(id, session["user_id"])`, commit, and `return redirect(url_for("profile", start_date=start_date, end_date=end_date))` — preserving `start_date` / `end_date` from `request.args` when present so the user lands back on the filtered profile view they came from.
- `templates/profile.html` — add the per-row Delete form on each `profile-expense-row`, sitting next to the existing Edit link from Step 7. Match the visual weight of the Edit affordance so the row still reads as a compact expense entry, not a wall of buttons.

## Files to create
- `templates/confirm_delete_expense.html` — the delete-confirmation page (see Templates section).

## New dependencies
No new dependencies. `sqlite3`, `flask.abort`, `request`, `redirect`, `url_for`, `session`, and `render_template` are all already importable in `app.py`.

## Rules for implementation
- No SQLAlchemy or any ORM — use `sqlite3` via `get_db()` only.
- Parameterised queries only — never interpolate values into SQL strings. Every `?` in the queries must correspond to a parameter in the `execute(...)` call.
- The view must scope every read and write to the current user. The `SELECT` filters by `id = ?`; if the row's `user_id` does not match `session["user_id"]`, abort 404. The `DELETE` must include `AND user_id = ?` in its `WHERE` clause as a belt-and-braces safeguard in case a future refactor reorders the ownership check.
- Do not distinguish "not found" from "not yours" in the response — both return 404. This avoids leaking the existence of other users' expense ids.
- Deletes must only happen on `POST`. A `GET` request must never mutate the database — it only renders the confirmation page. This protects against CSRF-style prefetching, accidental link-clicks, and follows the Post/Redirect/Get convention.
- The Delete affordance on the profile page must be a `<form method="post">`, not a plain `<a>` link — plain links issue `GET` and would either be ignored by the view or, worse, leave an open door if someone later "helpfully" wires the delete to GET.
- The successful redirect must preserve `start_date` and `end_date` from `request.args` when present (so a user deleting from a filtered profile view lands back on the same filter). If neither is in the query string, redirect with no query string.
- The Cancel link on the confirmation page must also preserve `start_date` / `end_date` — passing them as query string args into `url_for("profile", ...)` from inside the template.
- Use CSS variables — never hardcode hex values. Reuse the existing global classes from `static/css/style.css` (`.auth-section`, `.auth-container`, `.auth-card`, `.btn-submit`, `.btn-ghost`). If new page-specific styles are needed for the confirmation page or the per-row Delete button, inline them in a `<style>` block at the bottom of the relevant template and reference the existing CSS variables only.
- All templates extend `base.html` (use `{% extends "base.html" %}` and the `{% block content %}` / `{% block title %}` blocks). Use `url_for()` for all URL generation — including the confirm form `action` (`url_for("delete_expense", id=expense.id)`), the Cancel link (`url_for("profile", start_date=start_date, end_date=end_date)`), and the per-row Delete form `action` on the profile page.
- Do not introduce `flash()` / `get_flashed_messages()` in this step. There is no success toast or banner — the user simply sees the row disappear from the profile list, which is feedback enough.
- Do not change `app.secret_key`, the navbar, the `/profile` view, the add route, or the edit route.
- Do not change `database/db.py`.

## Definition of done
- Visiting `/expenses/<id>/delete` (GET) for an expense owned by the current user, while logged in, renders `confirm_delete_expense.html` with the row's `date`, `category`, `amount`, and `description` shown read-only so the user can verify what they are about to delete.
- Visiting `/expenses/<id>/delete` (GET) while **not** logged in redirects to `/login` (HTTP 302) and does not render the confirmation template.
- Visiting `/expenses/<id>/delete` (GET) for an expense that does not exist, or that exists but belongs to a different user, returns HTTP 404 — the response does not distinguish "missing" from "not yours", and the template is not rendered.
- Submitting `POST /expenses/<id>/delete` for an expense owned by the current user deletes the row from the `expenses` table, commits the change, and redirects to `/profile` (with `start_date` / `end_date` preserved if they were on the original request URL). The deleted row no longer appears in the profile expense list.
- Submitting `POST /expenses/<id>/delete` while **not** logged in redirects to `/login` (HTTP 302) and does not delete anything.
- Submitting `POST /expenses/<id>/delete` for an expense that does not exist, or that exists but belongs to a different user, returns HTTP 404 and does not delete anything.
- A plain `GET` to `/expenses/<id>/delete` (whether triggered by clicking a link, prefetching, or any browser navigation) does not delete the row — only `POST` does.
- The per-row Delete affordance on the profile page submits via `POST` to `{{ url_for("delete_expense", id=expense.id) }}` (not a hardcoded path), renders as a clearly clickable button on each `profile-expense-row` next to the Edit link from Step 7, and does not visually overpower the row.
- The Cancel link on the confirmation page returns to `/profile` and preserves `start_date` / `end_date` if they were on the request URL, so a user who cancels from a filtered view lands back on the same filter.
- The confirmation page extends `base.html` and uses `{% block title %}` (e.g. `"Delete expense — Spendly"`) and `{% block content %}`.
- The page uses the existing global CSS classes (`.auth-section`, `.auth-card`, `.btn-submit`, `.btn-ghost`, etc.) and any page-specific styles are inlined in a `<style>` block at the bottom of the template using CSS variables only — no hardcoded hex values.
- `app.py` runs without errors on port 5001. `git status` shows only the intended changes (`app.py`, `templates/confirm_delete_expense.html`, `templates/profile.html`).