# Spec: Registration

## Overview
Step 2 wires up user registration end-to-end. The current `/register` route is a stub that only renders a static template — it does not accept POST data, validate input, hash passwords, or persist users. This feature turns that stub into a working flow: the form accepts a name, email, and password; the server validates them, hashes the password with werkzeug, stores the new user in the `users` table (created in Step 1), and logs the user in immediately by setting a signed `user_id` session cookie. After registration the user is redirected to the profile page. This unblocks Step 3 (Login and Logout) and Step 4 (Profile), both of which require a `user_id` in the session to function.

## Depends on
- **Step 1 — Database setup**: requires the `users` table (with columns `id`, `name`, `email UNIQUE`, `password_hash`, `created_at`) and the `get_db()` helper from `database/db.py`.

## Routes
- `GET /register` — render the registration form — public
- `POST /register` — validate input, create user, log them in, redirect to `/profile` — public

## Database changes
No database changes. The `users` table from Step 1 is sufficient.

## Templates
- **Create:** none
- **Modify:**
  - `templates/register.html` — change the form `action` from the literal `"/register"` to `{{ url_for('register') }}`; keep the existing markup, classes, and inline page-specific styles untouched.

## Files to change
- `app.py` — convert the `register` view to accept `GET` and `POST`; add validation, password hashing, and session setup; import `generate_password_hash` and `check_password_hash` from `werkzeug.security`, plus `session`, `redirect`, `url_for`, `request`, and `flash` from `flask`.
- `templates/register.html` — replace the hardcoded form action with `{{ url_for('register') }}`.

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security` is already installed (required by Step 1).

## Rules for implementation
- No SQLAlchemy or any ORM — use `sqlite3` via `get_db()` only.
- Parameterised queries only — never interpolate values into SQL strings.
- Passwords must be hashed with `werkzeug.security.generate_password_hash` before being stored. Never store plaintext passwords.
- The Flask `app.secret_key` must be set in `app.py` so signed session cookies work (e.g. `app.secret_key = "dev-secret-change-me"`). Document this is for development.
- On success, store `session["user_id"] = new_user_id` and `session["user_name"] = new_user_name`, then `return redirect(url_for("profile"))`.
- Validation rules for the POST handler:
  - All three fields (`name`, `email`, `password`) are required — if any is missing, re-render the form with an error message and HTTP 400.
  - `email` must contain `@` and `.` and be unique — query `users` by email first and re-render with an error if it already exists.
  - `password` must be at least 8 characters — re-render with an error otherwise.
  - Trim whitespace from `name` and `email` before validation and storage.
- Use CSS variables — never hardcode hex values. Existing global classes in `static/css/style.css` (`.btn-submit`, `.form-input`, `.auth-section`, `.auth-error`, etc.) should be reused; do not add new page-specific styles for registration.
- All templates extend `base.html` (already the case — preserve it).
- Use `url_for()` for all URL generation, including the form `action` attribute.

## Definition of done
- Visiting `/register` shows the existing registration form.
- Submitting the form with all fields blank shows an error message and does not create a user.
- Submitting a valid new email and a password of 8+ characters creates a row in the `users` table with a non-empty `password_hash` and redirects to `/profile`.
- After registration, the response sets a session cookie; reloading `/profile` keeps the user logged in (Step 4 will replace the placeholder `/profile` route, but the session itself must persist).
- Submitting an email that already exists in `users` re-renders the form with an "email already registered" error and does not create a duplicate row (UNIQUE constraint is preserved).
- Submitting a password shorter than 8 characters re-renders the form with a "password must be at least 8 characters" error.
- Inspecting the `users` table after a successful registration shows the stored `password_hash` is a werkzeug hash (starts with `pbkdf2:` or `scrypt:`), not the plaintext password.
- `app.py` runs without errors on port 5001 and `git status` shows only the intended changes (`app.py` and `templates/register.html`).
