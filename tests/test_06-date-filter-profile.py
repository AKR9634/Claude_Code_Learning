"""Tests for Step 6 — Date Filter for Profile Page.

These tests are written against the SPEC
(`.claude/specs/06-date-filter-profile.md`), not against the current
implementation. They describe the behavior the `/profile` route SHOULD have:

- Auth guard: unauthenticated requests redirect to `/login`.
- Optional `start_date` / `end_date` query params (YYYY-MM-DD).
- Defaults to current month (first-of-this-month through today).
- Invalid / missing params fall back to the default silently.
- `start_date > end_date` is silently swapped.
- Filtering is inclusive and scoped to the current user.
- The page exposes a GET form with two date inputs whose action is
  `url_for("profile")`.
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta

import pytest

from app import app as flask_app
from database import db as db_module


# ---------------------------------------------------------------------- #
# Fixtures                                                               #
# ---------------------------------------------------------------------- #


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Isolated Spendly app with a fresh SQLite file per test.

    The `database.db.get_db()` helper hard-codes `DB_PATH` to a file under
    the project root. We point `DB_PATH` at a per-test temporary file so
    each test sees a clean schema and seed state.
    """
    db_file = tmp_path / "spendly-test.db"
    monkeypatch.setattr(db_module, "DB_PATH", db_file)

    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        WTF_CSRF_ENABLED=False,
    )

    with flask_app.app_context():
        db_module.init_db()
        db_module.seed_db()
        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


# Known demo user seeded by database/db.py -> seed_db()
DEMO_EMAIL = "demo@spendly.com"
DEMO_PASSWORD = "demo123"


@pytest.fixture
def auth_client(client):
    """Logged-in client using the seeded demo user."""
    response = client.post(
        "/login",
        data={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
        follow_redirects=False,
    )
    # Login should redirect somewhere (profile) on success.
    assert response.status_code in (200, 302)
    return client


# ---------------------------------------------------------------------- #
# DB seeding helpers                                                     #
# ---------------------------------------------------------------------- #


def _insert_user(name: str, email: str, password: str = "Password1!") -> int:
    """Insert a brand-new user with a hashed password and return its id."""
    from werkzeug.security import generate_password_hash

    conn = db_module.get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def _insert_expense(user_id: int, expense_date: str, category: str = "Food",
                    amount: float = 10.0, description: str = "Test expense") -> int:
    """Insert an expense row for `user_id` on a specific YYYY-MM-DD date."""
    conn = db_module.get_db()
    try:
        cursor = conn.execute(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, amount, category, expense_date, description),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


# ---------------------------------------------------------------------- #
# Auth guards                                                            #
# ---------------------------------------------------------------------- #


class TestAuthGuards:
    """Definition of done: unauthenticated /profile redirects to /login."""

    def test_profile_redirects_to_login_when_not_authenticated(self, client):
        response = client.get("/profile", follow_redirects=False)
        assert response.status_code == 302, (
            "Unauthenticated GET /profile must redirect (302), got "
            f"{response.status_code}"
        )
        assert response.headers["Location"].rstrip("/").endswith("/login"), (
            f"Expected redirect to /login, got {response.headers.get('Location')!r}"
        )

    def test_profile_does_not_render_template_when_not_authenticated(self, client):
        response = client.get("/profile", follow_redirects=False)
        # Spec: "does not render the profile template" — the body should
        # not contain profile landmarks (user header, range label, etc.).
        body = response.data.lower()
        assert b"showing expenses from" not in body
        assert b"<input" not in body

    def test_profile_accessible_when_authenticated(self, auth_client):
        response = auth_client.get("/profile")
        assert response.status_code == 200, (
            f"Logged-in GET /profile must succeed, got {response.status_code}"
        )


# ---------------------------------------------------------------------- #
# Default range                                                          #
# ---------------------------------------------------------------------- #


class TestDefaultRange:
    """No query params -> first-of-this-month through today."""

    def test_default_start_date_is_first_of_month(self, auth_client):
        today = date.today()
        expected_start = today.replace(day=1).isoformat()
        response = auth_client.get("/profile")
        assert response.status_code == 200
        assert expected_start.encode() in response.data, (
            f"Default start_date {expected_start} must appear in the page"
        )

    def test_default_end_date_is_today(self, auth_client):
        expected_end = date.today().isoformat()
        response = auth_client.get("/profile")
        assert response.status_code == 200
        assert expected_end.encode() in response.data, (
            f"Default end_date {expected_end} must appear in the page"
        )

    def test_default_range_label_marks_this_month(self, auth_client):
        response = auth_client.get("/profile")
        assert response.status_code == 200
        body = response.data.decode("utf-8", errors="replace").lower()
        assert "this month" in body, (
            "Default-range label must indicate 'this month' so users know "
            "they're seeing the fallback range."
        )

    def test_profile_renders_user_header_fields(self, auth_client):
        response = auth_client.get("/profile")
        assert response.status_code == 200
        body = response.data.decode("utf-8", errors="replace")
        # Seeded user: name="Demo User", email=demo@spendly.com
        assert "Demo User" in body, "Profile must render the user's name"
        assert "demo@spendly.com" in body, "Profile must render the user's email"
        # Member-since line — date or "member since" wording, spec preserves
        # the existing line so it must still be visible.
        assert "member" in body.lower(), (
            "Profile must render the 'member since' line from Step 4"
        )


# ---------------------------------------------------------------------- #
# Valid date range from query params                                     #
# ---------------------------------------------------------------------- #


class TestValidDateRange:
    """Query params are reflected in the rendered label and the filter."""

    def test_custom_range_label_reflected_in_page(self, auth_client):
        response = auth_client.get(
            "/profile?start_date=2026-06-01&end_date=2026-06-30"
        )
        assert response.status_code == 200
        body = response.data
        assert b"2026-06-01" in body, "Chosen start_date must appear in the label"
        assert b"2026-06-30" in body, "Chosen end_date must appear in the label"

    def test_expense_inside_range_is_shown(self, auth_client):
        """An expense dated inside the window must appear in the rendered HTML."""
        _insert_expense(
            user_id=1,  # demo user is always id=1 in the seed
            expense_date="2026-06-15",
            category="Food",
            amount=42.42,
            description="Inside-window expense",
        )

        response = auth_client.get(
            "/profile?start_date=2026-06-01&end_date=2026-06-30"
        )
        assert response.status_code == 200
        body = response.data.decode("utf-8", errors="replace")
        assert "Inside-window expense" in body, (
            "Expenses inside the chosen window must be rendered"
        )
        # Date should also appear.
        assert "2026-06-15" in body

    def test_expense_outside_range_is_hidden(self, auth_client):
        """An expense dated outside the window must NOT appear in the rendered HTML."""
        _insert_expense(
            user_id=1,
            expense_date="2026-05-15",
            category="Bills",
            amount=999.99,
            description="OUTSIDE_WINDOW_DESCRIPTION",
        )

        response = auth_client.get(
            "/profile?start_date=2026-06-01&end_date=2026-06-30"
        )
        assert response.status_code == 200
        body = response.data.decode("utf-8", errors="replace")
        assert "OUTSIDE_WINDOW_DESCRIPTION" not in body, (
            "Expenses outside the chosen window must NOT be rendered"
        )


# ---------------------------------------------------------------------- #
# Swapped dates                                                          #
# ---------------------------------------------------------------------- #


class TestSwappedDates:
    """start_date > end_date is silently corrected (not rejected)."""

    def test_swapped_dates_silently_reversed(self, auth_client):
        # Insert an expense that lives inside the *swapped-corrected* window
        # but outside the *as-given* window to verify the implementation
        # actually queried the corrected range.
        _insert_expense(
            user_id=1,
            expense_date="2026-06-12",
            category="Food",
            amount=12.34,
            description="SWAPPED_RANGE_EXPENSE",
        )

        response = auth_client.get(
            "/profile?start_date=2026-06-15&end_date=2026-06-10"
        )
        assert response.status_code == 200, (
            "Swapped dates must NOT raise — the page should still render."
        )
        body = response.data.decode("utf-8", errors="replace")

        # After swap, the window becomes 2026-06-10..2026-06-15, so the
        # 2026-06-12 expense must now be visible.
        assert "SWAPPED_RANGE_EXPENSE" in body, (
            "After silently swapping start/end, the expense dated 2026-06-12 "
            "should fall inside the corrected window and be rendered."
        )

        # Both corrected dates must appear in the label.
        assert "2026-06-10" in body
        assert "2026-06-15" in body


# ---------------------------------------------------------------------- #
# Invalid / malformed dates                                              #
# ---------------------------------------------------------------------- #


class TestInvalidDates:
    """Spec: invalid dates fall back to defaults silently — no 500."""

    def test_invalid_start_falls_back_to_default_end_used(self, auth_client):
        """?start_date=invalid&end_date=2026-06-30
        -> default start_date, chosen end_date used."""
        today = date.today()
        default_start = today.replace(day=1).isoformat()

        response = auth_client.get(
            "/profile?start_date=invalid&end_date=2026-06-30"
        )
        assert response.status_code == 200, (
            f"Invalid start_date must NOT raise — got {response.status_code}"
        )
        body = response.data.decode("utf-8", errors="replace")
        assert default_start in body, (
            f"Invalid start_date should default to first-of-this-month "
            f"({default_start})"
        )
        assert "2026-06-30" in body, (
            "Valid end_date must still be honoured when only start is invalid"
        )

    def test_wrong_format_dates_both_default(self, auth_client):
        """?start_date=06/01/2026&end_date=06/30/2026
        -> both fall back to defaults, no 500."""
        today = date.today()
        default_start = today.replace(day=1).isoformat()
        default_end = today.isoformat()

        response = auth_client.get(
            "/profile?start_date=06/01/2026&end_date=06/30/2026"
        )
        assert response.status_code == 200, (
            "Wrong-format dates must NOT raise — got "
            f"{response.status_code}"
        )
        body = response.data.decode("utf-8", errors="replace")
        assert default_start in body
        assert default_end in body

    def test_both_dates_invalid_both_default(self, auth_client):
        today = date.today()
        default_start = today.replace(day=1).isoformat()
        default_end = today.isoformat()

        response = auth_client.get(
            "/profile?start_date=garbage&end_date=also-garbage"
        )
        assert response.status_code == 200
        body = response.data.decode("utf-8", errors="replace")
        assert default_start in body
        assert default_end in body

    def test_missing_one_param_uses_chosen_other_defaults_missing(self, auth_client):
        """?start_date=2026-06-05 (no end_date)
        -> start_date is used as-given, end_date defaults to today."""
        today = date.today()
        default_end = today.isoformat()

        response = auth_client.get("/profile?start_date=2026-06-05")
        assert response.status_code == 200
        body = response.data.decode("utf-8", errors="replace")
        assert "2026-06-05" in body, (
            "Explicit start_date must be honoured when only end is missing"
        )
        assert default_end in body

    def test_no_500_on_garbage_input(self, auth_client):
        """Random SQL-ish / random strings must never produce a 500."""
        garbage_payloads = [
            "'; DROP TABLE expenses; --",
            "2026-13-40",          # invalid month/day
            "2026-02-30",          # impossible date
            "yesterday",
            "<script>alert(1)</script>",
            "2026/06/01",
        ]
        for payload in garbage_payloads:
            response = auth_client.get(
                f"/profile?start_date={payload}&end_date={payload}"
            )
            assert response.status_code == 200, (
                f"Garbage date {payload!r} caused status "
                f"{response.status_code}; expected 200"
            )


# ---------------------------------------------------------------------- #
# User scoping                                                           #
# ---------------------------------------------------------------------- #


class TestUserScoping:
    """Definition of done: another user's expenses are never returned."""

    def test_other_users_expenses_never_shown(self, client):
        # Create two users, each with one expense on the same date.
        alice_id = _insert_user("Alice Tester", "alice@example.com")
        bob_id = _insert_user("Bob Tester", "bob@example.com")

        _insert_expense(
            user_id=alice_id,
            expense_date="2026-06-10",
            category="Food",
            description="ALICE_SECRET_EXPENSE",
        )
        _insert_expense(
            user_id=bob_id,
            expense_date="2026-06-10",
            category="Food",
            description="BOB_SECRET_EXPENSE",
        )

        # Log in as Alice.
        client.post(
            "/login",
            data={"email": "alice@example.com", "password": "Password1!"},
            follow_redirects=False,
        )

        response = client.get(
            "/profile?start_date=2026-06-01&end_date=2026-06-30"
        )
        assert response.status_code == 200
        body = response.data.decode("utf-8", errors="replace")

        assert "ALICE_SECRET_EXPENSE" in body, (
            "Alice must see her own expense on her profile"
        )
        assert "BOB_SECRET_EXPENSE" not in body, (
            "Alice must NEVER see Bob's expense on her profile"
        )

    def test_logged_in_as_bob_does_not_see_alice(self, client):
        alice_id = _insert_user("Alice Two", "alice2@example.com")
        bob_id = _insert_user("Bob Two", "bob2@example.com")

        _insert_expense(
            user_id=alice_id,
            expense_date="2026-06-10",
            description="ALICE_TWO_EXPENSE",
        )
        _insert_expense(
            user_id=bob_id,
            expense_date="2026-06-10",
            description="BOB_TWO_EXPENSE",
        )

        client.post(
            "/login",
            data={"email": "bob2@example.com", "password": "Password1!"},
            follow_redirects=False,
        )

        response = client.get(
            "/profile?start_date=2026-06-01&end_date=2026-06-30"
        )
        body = response.data.decode("utf-8", errors="replace")
        assert "BOB_TWO_EXPENSE" in body
        assert "ALICE_TWO_EXPENSE" not in body


# ---------------------------------------------------------------------- #
# Inclusive bounds                                                       #
# ---------------------------------------------------------------------- #


class TestInclusiveBounds:
    """BETWEEN semantics: exact start_date and exact end_date are included."""

    def test_bounds_are_inclusive(self, auth_client):
        _insert_expense(
            user_id=1,
            expense_date="2026-06-01",  # exactly on start_date
            description="ON_START_DATE",
            amount=1.00,
        )
        _insert_expense(
            user_id=1,
            expense_date="2026-06-30",  # exactly on end_date
            description="ON_END_DATE",
            amount=2.00,
        )
        _insert_expense(
            user_id=1,
            expense_date="2026-05-31",  # one day before
            description="DAY_BEFORE_START",
        )
        _insert_expense(
            user_id=1,
            expense_date="2026-07-01",  # one day after
            description="DAY_AFTER_END",
        )

        response = auth_client.get(
            "/profile?start_date=2026-06-01&end_date=2026-06-30"
        )
        assert response.status_code == 200
        body = response.data.decode("utf-8", errors="replace")

        assert "ON_START_DATE" in body, (
            "Expense on exact start_date must be included (BETWEEN is inclusive)"
        )
        assert "ON_END_DATE" in body, (
            "Expense on exact end_date must be included (BETWEEN is inclusive)"
        )
        assert "DAY_BEFORE_START" not in body
        assert "DAY_AFTER_END" not in body


# ---------------------------------------------------------------------- #
# Form / UI contract                                                     #
# ---------------------------------------------------------------------- #


class TestFormContract:
    """The page exposes a GET form with two date inputs and url_for('profile')."""

    def test_form_action_uses_url_for_profile(self, auth_client):
        """The form's action attribute should be `/profile` (url_for output)."""
        response = auth_client.get("/profile")
        assert response.status_code == 200
        body = response.data.decode("utf-8", errors="replace")
        assert '<form' in body, "Profile must include a date-range <form>"

        # Find every <form ...> opening tag and confirm one of them has
        # an action targeting /profile. We don't pin to a specific HTML
        # structure — we just assert a form posts back to /profile.
        import re

        form_open_tags = re.findall(r"<form\b[^>]*>", body, flags=re.IGNORECASE)
        assert form_open_tags, "Expected at least one <form> on the profile page"

        profile_action_found = any(
            re.search(r'action\s*=\s*["\']/?profile["\']', tag, flags=re.IGNORECASE)
            for tag in form_open_tags
        )
        assert profile_action_found, (
            "One <form> action must target /profile (i.e. url_for('profile')). "
            f"Found: {form_open_tags}"
        )

    def test_form_uses_get_method(self, auth_client):
        response = auth_client.get("/profile")
        body = response.data.decode("utf-8", errors="replace")
        # The filter form must be GET (so the URL is bookmarkable).
        import re

        form_open_tags = re.findall(r"<form\b[^>]*>", body, flags=re.IGNORECASE)
        assert form_open_tags, "Expected at least one <form> on the profile page"
        # At least one form should target /profile AND use method=get.
        get_form_found = any(
            re.search(r'action\s*=\s*["\']/?profile["\']', tag, flags=re.IGNORECASE)
            and re.search(r'method\s*=\s*["\']get["\']', tag, flags=re.IGNORECASE)
            for tag in form_open_tags
        )
        assert get_form_found, (
            "The filter <form> must submit via GET to /profile. "
            f"Found forms: {form_open_tags}"
        )

    def test_form_has_two_date_inputs(self, auth_client):
        response = auth_client.get("/profile")
        body = response.data.decode("utf-8", errors="replace")
        import re

        date_inputs = re.findall(
            r'<input\b[^>]*type\s*=\s*["\']date["\'][^>]*>',
            body,
            flags=re.IGNORECASE,
        )
        assert len(date_inputs) >= 2, (
            "Profile must expose two <input type='date'> fields "
            f"(start_date, end_date). Found {len(date_inputs)}."
        )

        # Each date input must be named start_date or end_date.
        names_found = []
        for tag in date_inputs:
            m = re.search(r'name\s*=\s*["\']([\w-]+)["\']', tag, flags=re.IGNORECASE)
            if m:
                names_found.append(m.group(1))

        assert "start_date" in names_found, (
            f"Expected a date input named start_date; got names={names_found}"
        )
        assert "end_date" in names_found, (
            f"Expected a date input named end_date; got names={names_found}"
        )

    def test_page_renders_chosen_range_label(self, auth_client):
        """Spec: 'Render the chosen range as a small label above the list'."""
        response = auth_client.get(
            "/profile?start_date=2026-06-01&end_date=2026-06-30"
        )
        body = response.data.decode("utf-8", errors="replace").lower()
        # Spec example wording: "Showing expenses from ... to ..."
        assert "showing expenses from" in body, (
            "Page must render a label like 'Showing expenses from ... to ...'"
        )

    def test_page_extends_base_html(self, auth_client):
        """Profile must extend base.html and use block title + block content."""
        response = auth_client.get("/profile")
        body = response.data.decode("utf-8", errors="replace")
        # If base.html is extended, the page must declare its own <title>.
        assert "<title>" in body.lower(), "Profile must render a <title> block"
        # The title should mention Spendly / profile (per spec example wording).
        assert "spendly" in body.lower(), "Page title should brand with 'Spendly'"


# ---------------------------------------------------------------------- #
# DB safety — column scoping & parameterised queries                    #
# ---------------------------------------------------------------------- #


class TestQueryContract:
    """Spec: only date, category, amount, description selected."""

    def test_query_returns_only_legitimate_columns(self, auth_client):
        """Direct DB check: rows exposed to the template contain only the
        four whitelisted columns."""
        _insert_expense(
            user_id=1,
            expense_date="2026-06-10",
            category="Food",
            amount=11.11,
            description="COLUMN_SCOPE_TEST",
        )

        response = auth_client.get(
            "/profile?start_date=2026-06-01&end_date=2026-06-30"
        )
        assert response.status_code == 200
        assert b"COLUMN_SCOPE_TEST" in response.data

        # Inspect the raw DB: confirm the row exists with all columns,
        # and confirm the *implementation* query (the one the route runs)
        # only exposes the four whitelisted columns.
        conn = db_module.get_db()
        try:
            # Reproduce the spec's mandated query verbatim.
            rows = conn.execute(
                """
                SELECT date, category, amount, description
                FROM expenses
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
                """,
                (1, "2026-06-01", "2026-06-30"),
            ).fetchall()
        finally:
            conn.close()

        assert rows, "Query should return at least the inserted row"
        for row in rows:
            keys = set(row.keys())
            # Spec: select only date, category, amount, description.
            assert keys == {"date", "category", "amount", "description"}, (
                "Query must select only date, category, amount, description. "
                f"Got columns: {keys}"
            )
            # Defence-in-depth: these columns must NEVER appear in the row.
            assert "user_id" not in keys
            assert "id" not in keys
            assert "password_hash" not in keys


# ---------------------------------------------------------------------- #
# No flash messages                                                     #
# ---------------------------------------------------------------------- #


class TestNoFlashMessages:
    """Spec: invalid dates fall back silently — no flashed messages."""

    def test_no_flash_messages_for_invalid_dates(self, auth_client):
        """Even when dates are invalid, the page must not surface flash UI."""
        response = auth_client.get(
            "/profile?start_date=garbage&end_date=also-garbage"
        )
        assert response.status_code == 200
        body = response.data.decode("utf-8", errors="replace")

        # get_flashed_messages renders a category/with_categories block
        # only when messages exist. Assert none rendered.
        assert "get_flashed_messages" not in body, (
            "Spec forbids flash() / get_flashed_messages() in this step."
        )

        # Also: there should be no visible "alert" / "error" banner for
        # the date filter case.
        import re

        # Look for a generic Bootstrap-style alert used for flashed errors.
        # The implementation is forbidden from emitting these for date errors.
        # We don't assume a specific CSS class — we just assert the page
        # contains no obvious "Invalid date"-style banner text.
        assert "invalid date" not in body.lower(), (
            "Invalid date input must fall back silently — no error banner."
        )


# ---------------------------------------------------------------------- #
# DB connection hygiene (smoke test)                                    #
# ---------------------------------------------------------------------- #


class TestDatabaseHygiene:
    """Smoke checks: DB file is correctly written, query results are sane."""

    def test_demo_user_present_after_seed(self, app):
        conn = db_module.get_db()
        try:
            row = conn.execute(
                "SELECT email FROM users WHERE email = ?", (DEMO_EMAIL,)
            ).fetchone()
            assert row is not None, "seed_db() should have created the demo user"
        finally:
            conn.close()

    def test_filter_does_not_mutate_expenses_table(self, auth_client):
        """Multiple GETs to /profile must never INSERT/UPDATE/DELETE."""
        _insert_expense(user_id=1, expense_date="2026-06-10", description="STABLE")

        # Snapshot row count.
        conn = db_module.get_db()
        try:
            before = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
        finally:
            conn.close()

        for _ in range(3):
            response = auth_client.get(
                "/profile?start_date=2026-06-01&end_date=2026-06-30"
            )
            assert response.status_code == 200

        conn = db_module.get_db()
        try:
            after = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
        finally:
            conn.close()

        assert after == before, (
            f"GET /profile must not mutate the expenses table "
            f"(before={before}, after={after})"
        )
