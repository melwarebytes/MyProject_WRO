# Lab 5: Issues Found and Fixed

File: `tower_maintenance.py`. Line numbers refer to the original file (see `reports/before/`).

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| SQL injection (Bandit B608, Medium) | Security | 11 | `add_tower` built the INSERT with `%` string formatting, so a site name like `x'); DROP TABLE towers;--` goes straight into the SQL | Used a parameterized query with `?` placeholders and passed the values as a tuple |
| Unsafe deserialization (Bandit B301, Medium; B403, Low) | Security | 1, 43 | `snapshot()` round-tripped the rows through `pickle.dumps`/`pickle.loads`. pickle can run arbitrary code on untrusted data and wasn't needed here | Removed the pickle import and returned `list(...)` of the fetched rows, which is already a copy |
| Hardcoded password (Bandit B105, Low) | Security | 6 | `NOC_PASSWORD = "tower-noc-77"` puts a credential in source control | Read it from the `NOC_PASSWORD` environment variable with `os.environ.get` |
| Broad exception (Pylint W0718) | Bug | 20 | `except Exception` hides every error, including typos and programming bugs, and printed no detail | Catch only `sqlite3.Error` and print the error message |
| Global variable (Pylint W0603, C0103) | Design | 7, 16 | `service_count` was a module-level global changed with `global`, and the DB connection was also global | Moved the connection and counter into a `TowerTracker` class as instance attributes |
| Crash on missing tower | Bug | 35-36 | `riskLevel` did `row[0]` without checking for `None`, so an unknown id raised `TypeError` | Return `"unknown"` when no row is found; also removed the `else` after `return` (R1705) |
| Missing commit after update | Bug | 18 | `serviceTower` updated the row but never committed | Added `self.conn.commit()` after the update |
| Code runs on import | Bug | 54 | `main()` was called at module level, so importing the file ran the demo | Wrapped it in `if __name__ == "__main__":` |
| Naming style (Pylint C0103) | Style | 10, 15, 34 | `addTower`, `serviceTower`, `riskLevel` are camelCase | Renamed to `add_tower`, `service_tower`, `risk_level` |
| Missing docstrings (Pylint C0114, C0116) | Style | 1 and all functions | No module or function docstrings | Added a module docstring and one for the class and each method |
| Old-style formatting (Pylint C0209) | Style | 11 | `%` string formatting | Removed with the parameterized query; f-string used for the error message |
| Long lines (Flake8 E501, Pylint C0301) | Style | 5, 11, 18, 35, 43 | Lines over 79 characters | Split the SQL strings and calls over several lines |
| Blank lines (Flake8 E303) | Style | 25 | 3 blank lines before `overdue` | Reduced to 2 |
| Operator spacing (Flake8 E225) | Style | 50 | `total=len(...)` | Changed to `total = len(...)` |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.14/10 | 10.00/10 |
| Flake8 | 7 issues | 0 issues (empty report) |
| Bandit | 4 issues (2 Medium, 2 Low) | No issues identified |

The program prints the same output before and after: `['Ridge-A'] high 2 1`.
