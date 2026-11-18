# Lab 7: Fuzzing for Input Validation Bugs

Assigned repo: `L6_L7_25_train_fare` (Train Fare). Merull Shah, PES1UG24CS270, 5E.

## Files

| File | What it is |
|---|---|
| `train_fare.py` | Fixed application |
| `train_fare_original.py` | Buggy version as handed out, kept for comparison |
| `test_train_fare.py` | Completed Hypothesis fuzz tests (9 properties) |
| `Lab7_FuzzTesting_PES1UG24CS270.pdf` | Report with the screenshots for steps 2, 4, 5 and 6 |
| `fuzz_failures_full_log.txt` | Full pytest output of the failing run against the buggy code |
| `screenshots/` | The same screenshots as PNGs |

## Summary

Against the buggy code 6 of 9 properties fail. Hypothesis found crashes on `None`, empty strings,
`'1,,3'`, `'-'` and `'S3--1'`, plus wrong answers: a 2-digit PNR accepted, a negative journey
distance for `'1,0'`, and seat 0 accepted. The fixed functions check the type and format of every
input and return `None` for anything invalid; `main()` prints a message instead of crashing.
After the fix all 9 properties pass.

## Run

```
pip install hypothesis pytest
python train_fare.py
python -m pytest test_train_fare.py
```
