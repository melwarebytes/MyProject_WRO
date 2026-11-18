"""Maintenance tracker for telecom towers.

Logs towers and their faults, records servicing, lists overdue sites
and rates the risk of each tower.
"""

import os
import sqlite3

NOC_PASSWORD = os.environ.get("NOC_PASSWORD", "")
OVERDUE_YEARS = 2
HIGH_RISK_FAULTS = 3


class TowerTracker:
    """Stores towers in an SQLite database and tracks servicing."""

    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE towers (id INTEGER PRIMARY KEY, site TEXT, "
            "last_service INTEGER, faults INTEGER)"
        )
        self.service_count = 0

    def add_tower(self, site, last_service, faults=0):
        """Add a tower with its last service year and fault count."""
        self.conn.execute(
            "INSERT INTO towers (site, last_service, faults) "
            "VALUES (?, ?, ?)",
            (site, last_service, faults),
        )
        self.conn.commit()

    def service_tower(self, tower_id, year):
        """Record a service for a tower and clear its faults."""
        try:
            self.conn.execute(
                "UPDATE towers SET last_service = ?, faults = 0 "
                "WHERE id = ?",
                (year, tower_id),
            )
            self.conn.commit()
            self.service_count += 1
        except sqlite3.Error as err:
            print(f"service failed: {err}")

    def overdue(self, year):
        """Return the sites not serviced in the last OVERDUE_YEARS years."""
        rows = self.conn.execute(
            "SELECT site, last_service FROM towers"
        ).fetchall()
        return [site for site, last in rows if year - last >= OVERDUE_YEARS]

    def risk_level(self, tower_id):
        """Return 'high', 'normal' or 'unknown' for a tower."""
        row = self.conn.execute(
            "SELECT faults FROM towers WHERE id = ?", (tower_id,)
        ).fetchone()
        if row is None:
            return "unknown"
        if row[0] > HIGH_RISK_FAULTS:
            return "high"
        return "normal"

    def snapshot(self):
        """Return a copy of every tower row."""
        return list(self.conn.execute("SELECT * FROM towers").fetchall())


def main():
    """Run a short demonstration of the tracker."""
    tracker = TowerTracker()
    tracker.add_tower("Ridge-A", 2021, 5)
    tracker.add_tower("Coast-B", 2024)
    tracker.service_tower(2, 2025)
    total = len(tracker.snapshot())
    print(
        tracker.overdue(2025),
        tracker.risk_level(1),
        total,
        tracker.service_count,
    )


if __name__ == "__main__":
    main()
