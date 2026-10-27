# Lab 5: Reflection

**1. Which issues were the easiest to fix, and which were the hardest? Why?**

The Flake8 issues were the easiest. Long lines, extra blank lines and missing spaces around `=` are mechanical, and the fix doesn't change what the code does. The hardest was the `global service_count` warning from Pylint. There's no one-line fix for it: the counter and the database connection both lived at module level, so I had to move them into a `TowerTracker` class and turn the functions into methods. That touched every function, so I had to re-run the program afterwards to check the output hadn't changed. The SQL injection fix was simple to write, but it took a moment to see why `%` formatting was dangerous, since the demo only ever passes safe strings.

**2. Did the static analysis tools report any false positives? If so, describe one example.**

The Bandit pickle warnings (B403, B301) were close to a false positive in this program. The data being unpickled was created by `pickle.dumps` one line earlier, so no untrusted input could reach `pickle.loads`. Bandit can't tell where the data comes from, so it flags every use of pickle. I still removed it, because the round trip did nothing useful. B105 (hardcoded password) is another borderline one: Bandit flags it from the variable name, and it would also flag a harmless string. In this case it really was a credential, though.

**3. How would you integrate static analysis tools into your actual software development workflow?**

I'd run them in two places. Locally, a pre-commit hook would run Flake8 and Bandit on changed files, so style problems and obvious security issues are caught before a commit. In CI (for example, GitHub Actions), all three tools would run on every push and pull request. The build would fail on any Bandit Medium/High finding, any Flake8 error, or a Pylint score below a set threshold such as 9.5. I'd keep the tool settings in a config file (`setup.cfg` or `pyproject.toml`) so everyone on the team uses the same rules, and use `# nosec` or Pylint disables only with a comment explaining why.

**4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?**

- Security: the INSERT can no longer be broken by a crafted site name, pickle is gone, and the password is no longer in the source.
- Robustness: `risk_level` no longer crashes on an unknown tower id, service updates are committed, and only database errors are caught, so real bugs aren't silently swallowed.
- Readability: snake_case names, docstrings and named constants (`OVERDUE_YEARS`, `HIGH_RISK_FAULTS`) make the intent clear without reading the logic.
- Reusability: the file can be imported without running the demo, and the class makes it possible to create more than one tracker or point it at a real database file.

The Pylint score went from 5.14 to 10.00, and Flake8 and Bandit report nothing.
