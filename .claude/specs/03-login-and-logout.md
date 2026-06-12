# Spec: Login and Logout

## Overview
Step 3 wires up user login and logout end-to-end. The current `/login` route is a stub that only renders a static template — it does not accept POST data, look up the user, or verify the password. The `/logout` route is also a stub that returns a plain placeholder string. This feature turns both into working flows: the login form accepts an email and password, the server looks up the user in the `users` table, verifies the password with werkzeug's `check_password_hash`, and on success sets `session["user_id"]` and `session["user_name"]` exactly the way `/register` does, then redirects to `/profile`. On failure, the form re-renders with a generic error. `/logout` becomes a POST endpoint that clears the session and redirects to the landing page. Together, these flows let users re-enter the app after closing their browser and let them sign out cleanly, both prerequisites for every later authenticated feature (profile, expenses, reports).

## Depends on
- **Step 1 — Database setup**: requires the `users` table (with columns `id`, `name`, `email UNIQUE`, `password_hash`, `created_at`) and the `get_db()` helper from `database/db.py`.
- **Step 2 — Registration**: requires the registration flow to already create users and set `session["user_id"]` + `session["user_name"]` on success, since login must mirror that session shape. Also establishes the `auth-section` / `auth-card` / `form-input` / `btn-submit` / `auth-error` template and CSS conventions this spec reuses.

## Routes
- `GET /login` — render the login form — public
- `POST /login` — validate credentials, set session, redirect to `/profile` on success; re-render with error on failure — public
- `POST /logout` — clear the session, redirect to landing page `/` — logged-in

## Database changes
No database changes. The `users` table from Step 1 is sufficient.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — change the form `action` from the literal `"/login"` to `{{ url_for('login') }}`; add a small "Don't have an account?" link is already present, keep it. No new page-specific styles needed; the existing global classes are sufficient.
  - `templates/base.html` — the navbar currently shows "Sign in" and "Get started" links. Add a conditional block so that when `session.user_id` is set, the right-hand links switch to a greeting ("Hi, {name}") plus a `Sign out` button (a small `<form method="POST" action="{{ url_for('logout') }}">` with a submit button styled to match the existing nav links). When not logged in, keep the current "Sign in" / "Get started" links unchanged.

## Files to change
- `app.py` — convert the `login` view to accept `GET` and `POST`; add credential lookup, password verification with `check_password_hash`, and session setup matching the registration flow. Convert the `logout` view to accept `POST` only, clear `session`, and redirect to `landing`. The `app.secret_key` is already set in Step 2; no change there.
- `templates/login.html` — replace the hardcoded form `action` with `{{ url_for('login') }}`.
- `templates/base.html` — add a conditional navbar block that swaps "Sign in / Get started" for a greeting + "Sign out" POST form when `session.user_id` is present.

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` is already installed (required by Step 1 and used implicitly by Step 2's import line in `app.py`).

## Rules for implementation
- No SQLAlchemy or any ORM — use `sqlite3` via `get_db()` only.
- Parameterised queries only — never interpolate values into SQL strings. The lookup query is `SELECT id, name, password_hash FROM users WHERE email = ?`.
- Passwords must be verified with `werkzeug.security.check_password_hash(stored_hash, submitted_password)`. Never compare passwords as plain strings.
- The Flask `app.secret_key` is already set in `app.py` from Step 2 — leave it as is. Signed session cookies already work.
- On successful login, store the same two session keys that `/register` does: `session["user_id"]` (int) and `session["user_name"]` (str), then `return redirect(url_for("profile"))`.
- On failed login (unknown email **or** wrong password), re-render `login.html` with a single generic error message — `"Invalid email or password."` — and HTTP 401. Do not reveal which of the two was wrong.
- Validation rules for the POST handler:
  - Both `email` and `password` are required — if either is missing, re-render with an error and HTTP 400.
  - Trim whitespace from `email` before lookup. Do not trim the password.
  - Do not impose the 8-character minimum on login (a user who registered before that rule existed must still be able to sign in). Length validation belongs to registration, not login.
- `/logout` must be `POST` only — never allow `GET /logout` to clear a session, because that would let any `<img src="/logout">` or link preview log a user out. Refuse `GET` with a 405 (or simply don't register a GET handler — Flask will return 405 by default).
- On logout, use `session.clear()` to remove both `user_id` and `user_name`, then `return redirect(url_for("landing"))`.
- Use CSS variables — never hardcode hex values. Reuse existing global classes in `static/css/style.css` (`.btn-submit`, `.form-input`, `.auth-section`, `.auth-error`, `.nav-links`, etc.). If the navbar sign-out form needs any styling, inline a small `<style>` block in `base.html` using the existing CSS variables.
- All templates extend `base.html` (already the case — preserve it).
- Use `url_for()` for all URL generation, including form `action` attributes and the navbar links.
- Do not use `flash()` / `get_flashed_messages()` in this step — the existing auth templates use a `{% if error %}` block instead, and that pattern should be kept consistent with `/register`.

## Definition of done
- Visiting `/login` shows the existing login form, and submitting it goes to the `login` view function (not a hardcoded path).
- Submitting a known email with the **wrong** password re-renders `/login` with the generic error "Invalid email or password." and HTTP 401. The session is **not** set.
- Submitting an **unknown** email re-renders `/login` with the **same** generic error message (no leak about whether the email exists) and HTTP 401.
- Submitting a known email with the **correct** password (e.g. `demo@spendly.com` / `demo123` from the Step 1 seed, or any user created via `/register`) sets `session["user_id"]` and `session["user_name"]`, then redirects to `/profile`. The session persists across reloads.
- When logged in, the navbar shows a greeting ("Hi, {name}") and a "Sign out" button instead of "Sign in" and "Get started". When not logged in, the original links are shown.
- Clicking "Sign out" issues a `POST` to `/logout`, clears the session, and redirects to `/`. The navbar reverts to "Sign in" / "Get started" on the next render.
- A direct `GET /logout` request returns HTTP 405 (Method Not Allowed) and does not clear the session.
- Inspecting the session cookie before login shows it is not set; after login it is set; after logout it is cleared.
- `app.py` runs without errors on port 5001 and `git status` shows only the intended changes (`app.py`, `templates/login.html`, `templates/base.html`).
