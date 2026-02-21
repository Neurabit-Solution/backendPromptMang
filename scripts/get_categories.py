#!/usr/bin/env python3
"""
Query the database directly for all categories and print all rows and columns.
Uses config from config.properties (same as the app).
Usage (from project root):
  python scripts/get_categories.py
"""

import os
import sys

# Project root on path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User  # ensure User is registered before Style/Creation
from app.models.style import Category


# All Category columns in display order
COLUMNS = ["id", "name", "slug", "icon", "description", "preview_url", "display_order", "is_active"]


def main():
    db = SessionLocal()
    try:
        rows = db.query(Category).order_by(Category.id).all()
    finally:
        db.close()

    if not rows:
        print("No rows in categories table.")
        return

    # Build string width per column (header + values)
    widths = {}
    for col in COLUMNS:
        values = [str(getattr(r, col, "")) if getattr(r, col) is not None else "" for r in rows]
        widths[col] = max(len(col), max(len(v) for v in values), 1)

    def line(cells, sep=" "):
        return sep.join(cells[i].ljust(widths[col]) for i, col in enumerate(COLUMNS))

    header = line(COLUMNS)
    rule = "-" * len(header)
    print(header)
    print(rule)
    for r in rows:
        cells = [str(getattr(r, col, "")) if getattr(r, col) is not None else "" for col in COLUMNS]
        print(line(cells))
    print()
    print(f"Total: {len(rows)} row(s)")


if __name__ == "__main__":
    main()
