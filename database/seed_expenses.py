"""Seed N realistic random expenses for a given user_id, spread across M past months.

Usage (from project root):
    Claude_Code/Scripts/python.exe database/seed_expenses.py <user_id> <count> <months>
"""
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# Make `database` importable when run from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import get_db  # noqa: E402

# (category, min_amount, max_amount, [descriptions...])
CATEGORY_RULES = {
    "Food": (
        50, 800,
        [
            "Lunch at Haldiram's", "Chai and samosa", "Dinner at Saravana Bhavan",
            "Zomato order", "Swiggy dinner", "Breakfast at Indian Coffee House",
            "Dominos pizza", "Subway sandwich", "Street food stall",
            "Thali at local restaurant", "Chole bhature", "Masala dosa",
            "Idli sambar", "Biryani at Paradise", "MTR meals",
            "Cafe Coffee Day", "Chai at tapri", "Veg momos",
        ],
    ),
    "Transport": (
        20, 500,
        [
            "Uber to office", "Ola auto rickshaw", "Delhi Metro token",
            "BMTC bus pass", "Mumbai local train", "Rapido bike ride",
            "Petrol refill", "Diesel for Activa", "Auto to station",
            "Cab to airport", "Chai tapri fuel", "Train ticket Bengaluru",
        ],
    ),
    "Bills": (
        200, 3000,
        [
            "Airtel postpaid bill", "Jio Fiber recharge", "Electricity bill BESCOM",
            "Tata Play DTH", "Gas cylinder refil", "Tata Power bill",
            "Broadband bill", "Water bill", "Maintenance charge",
            "Mobile recharge", "Insurance premium quarterly",
        ],
    ),
    "Health": (
        100, 2000,
        [
            "Apollo Pharmacy", "Pharmacy medicines", "Doctor consultation",
            "Pathology lab test", "Dentist cleaning", "Eye checkup at Lenskart",
            "Health supplement", "Gym monthly fee", "Yoga class",
            "Physiotherapy session", "Thyroid test",
        ],
    ),
    "Entertainment": (
        100, 1500,
        [
            "PVR movie tickets", "BookMyShow concert", "Netflix monthly plan",
            "Hotstar Premium", "Spotify annual", "Amazon Prime renewal",
            "Bowling with friends", "Game zone at Select Citywalk",
            "Standup comedy show", "Theme park entry",
        ],
    ),
    "Shopping": (
        200, 5000,
        [
            "Myntra kurta", "Ajio jeans", "Amazon headphones",
            "Flipkart mobile cover", "Lenskart spectacles",
            "Decathlon sports shoes", "Croma smartwatch",
            "Reliance Trends shirt", "Lifestyle store haul",
            "Nykaa cosmetics", "BigBazaar groceries", "DMart monthly stock",
        ],
    ),
    "Other": (
        50, 1000,
        [
            "Barber shop haircut", "Tailor alteration", "Photocopying",
            "Courier via DTDC", "Laundry pickup", "Gift wrap",
            "Donation at temple", "Parking fee", "ATM withdrawal fee",
            "Newspaper subscription", "Household repair",
        ],
    ),
}

# Proportional category distribution — Food most common, Health and Entertainment least
CATEGORY_WEIGHTS = [
    ("Food", 28),
    ("Transport", 18),
    ("Bills", 14),
    ("Shopping", 14),
    ("Other", 10),
    ("Entertainment", 8),
    ("Health", 8),
]

CATEGORIES = tuple(name for name, _ in CATEGORY_WEIGHTS)
WEIGHTS = tuple(w for _, w in CATEGORY_WEIGHTS)


def parse_args(argv: list[str]) -> tuple[int, int, int]:
    if len(argv) != 4:
        raise ValueError(
            "Usage: /seed-expenses <user_id> <count> <months>\n"
            "Example: /seed-expenses 1 50 6"
        )
    try:
        user_id = int(argv[1])
        count = int(argv[2])
        months = int(argv[3])
    except ValueError:
        raise ValueError(
            "Usage: /seed-expenses <user_id> <count> <months>\n"
            "Example: /seed-expenses 1 50 6"
        )
    if count <= 0 or months <= 0 or user_id <= 0:
        raise ValueError("user_id, count, and months must be positive integers")
    return user_id, count, months


def random_date_within_months(months: int, today: date) -> date:
    """Pick a random day in the last <months> calendar months, ending today."""
    start = today.replace(day=1)
    for _ in range(months - 1):
        start = (start - timedelta(days=1)).replace(day=1)
    end = today
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def build_expense(user_id: int, today: date, months: int) -> tuple:
    category = random.choices(CATEGORIES, weights=WEIGHTS, k=1)[0]
    lo, hi, descriptions = CATEGORY_RULES[category]
    amount = round(random.uniform(lo, hi), 2)
    description = random.choice(descriptions)
    expense_date = random_date_within_months(months, today).isoformat()
    return (user_id, amount, category, expense_date, description)


def main() -> None:
    user_id, count, months = parse_args(sys.argv)

    conn = get_db()
    try:
        # Verify user exists
        row = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            print(f"No user found with id {user_id}.")
            return

        # Ensure expenses table exists (matches init_db schema in db.py)
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        conn.commit()

        today = date.today()
        rows = [build_expense(user_id, today, months) for _ in range(count)]

        try:
            conn.execute("BEGIN")
            conn.executemany(
                """
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

        # Pull back for confirmation
        inserted = conn.execute(
            """
            SELECT id, user_id, amount, category, date, description
            FROM expenses
            WHERE user_id = ? AND date >= ?
            ORDER BY date ASC
            """,
            (user_id, (today.replace(day=1) if months <= 1
                       else (today - timedelta(days=months * 31)).isoformat())),
        ).fetchall()

        # Compute the actual span of the rows we just inserted
        dates = [r["date"] for r in inserted]
        # Filter to only the ones we just inserted (those within the last <months> months, by build)
        # Since multiple runs may overlap, restrict to the latest batch by id range
        if inserted:
            first_id = inserted[0]["id"]
            last_id = inserted[-1]["id"]
            # We inserted `count` rows in one go — find the most recent run by id desc
            latest = conn.execute(
                """
                SELECT id, user_id, amount, category, date, description
                FROM expenses
                WHERE user_id = ? AND id >= ?
                ORDER BY id ASC
                """,
                (user_id, last_id - count + 1),
            ).fetchall()
        else:
            latest = []

        # Re-pull: safest is "last N rows for this user"
        latest = conn.execute(
            """
            SELECT id, user_id, amount, category, date, description
            FROM expenses
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, count),
        ).fetchall()
        latest = list(reversed(latest))  # chronological

        if not latest:
            print("No expenses were inserted.")
            return

        dates = [r["date"] for r in latest]
        print(f"Inserted {len(latest)} expenses for user {user_id}.")
        print(f"Date range: {min(dates)} to {max(dates)}")
        print("Sample (first 5):")
        for r in latest[:5]:
            print(f"  id={r['id']:>3}  {r['date']}  Rs.{r['amount']:>8.2f}  "
                  f"{r['category']:<14}  {r['description']}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
