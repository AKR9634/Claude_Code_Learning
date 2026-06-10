"""Seed a single realistic random Indian user into spendly.db."""
import random
import sys
from datetime import datetime
from pathlib import Path

from werkzeug.security import generate_password_hash

# Make `database` importable when run from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import get_db  # noqa: E402

# Realistic Indian first names across regions
INDIAN_FIRST_NAMES = [
    # North
    "Aarav", "Arjun", "Rahul", "Vivek", "Rohan", "Aditya", "Karan", "Saurabh",
    "Neha", "Pooja", "Priya", "Anjali", "Shreya", "Kavya", "Riya",
    # South
    "Arun", "Karthik", "Vijay", "Ravi", "Suresh", "Manoj",
    "Lakshmi", "Divya", "Anitha", "Meera", "Deepa",
    # West
    "Hitesh", "Nikhil", "Yash", "Ishaan", "Tushar",
    "Sneha", "Aishwarya", "Tanvi",
    # East
    "Suman", "Pradeep", "Bikram", "Subham",
    "Pallabi", "Rupali", "Ananya",
    # Central / mixed
    "Aman", "Rakesh", "Vikas", "Sandeep",
    "Nisha", "Sunita", "Rekha",
]

INDIAN_LAST_NAMES = [
    # North
    "Sharma", "Verma", "Gupta", "Agarwal", "Mishra", "Pandey", "Tiwari",
    "Saxena", "Sinha", "Yadav",
    # South
    "Iyer", "Krishnan", "Menon", "Nair", "Pillai", "Reddy", "Rao",
    "Naidu", "Murthy", "Bhat",
    # West
    "Patel", "Shah", "Desai", "Mehta", "Joshi", "Kulkarni", "Jain",
    "Modi", "Trivedi", "Thakkar",
    # East
    "Mukherjee", "Chatterjee", "Banerjee", "Das", "Sen", "Bose", "Dutta",
    "Ghosh", "Roy", "Sarkar",
    # Sikh / others
    "Singh", "Kaur", "Gill", "Sandhu", "Dhillon", "Bedi",
]


def make_email(first: str, last: str) -> str:
    """Build a realistic email: firstname.lastname<2-3 digit number>@gmail.com."""
    digits = random.randint(10, 999)  # 2 or 3 digits
    handle = f"{first.lower()}.{last.lower()}{digits}"
    return f"{handle}@gmail.com"


def pick_name() -> tuple[str, str]:
    return random.choice(INDIAN_FIRST_NAMES), random.choice(INDIAN_LAST_NAMES)


def main() -> None:
    conn = get_db()
    try:
        # Ensure schema exists
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()

        # Generate a unique email
        for _ in range(200):
            first, last = pick_name()
            name = f"{first} {last}"
            email = make_email(first, last)
            existing = conn.execute(
                "SELECT 1 FROM users WHERE email = ?", (email,)
            ).fetchone()
            if not existing:
                break
        else:
            raise RuntimeError("Could not generate a unique email after 200 tries")

        password_hash = generate_password_hash("password123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, datetime.now().isoformat(sep=" ", timespec="seconds")),
        )
        conn.commit()
        user_id = cursor.lastrowid

        print(f"id:        {user_id}")
        print(f"name:      {name}")
        print(f"email:     {email}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
