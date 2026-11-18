# Lab 6: Code and Branch Coverage

Assigned repo: `L6_L7_25_train_fare` (Train Fare). Merull Shah, PES1UG24CS270, 5E.

`train_fare.py` works out base fares by class and distance, age concessions and Tatkal charges.

## Files

| File | What it is |
|---|---|
| `train_fare.py` | Module under test (unchanged) |
| `test_train_fare.py` | Starter tests from the assigned repo |
| `CodeCoverageTest_train_fare.py` | Tests written for line coverage |
| `BranchCoverageTest_train_fare.py` | Tests written for branch coverage, including boundary values |
| `screenshots/` | Terminal output of the coverage runs |
| `Lab_6_Handout.pdf` | Lab handout |

## Results (coverage on `train_fare.py`)

| Test file | Line coverage | Branch coverage |
|---|---|---|
| `test_train_fare.py` (starter) | 45% | 40% |
| `CodeCoverageTest_train_fare.py` | 100% | 98% (misses `36->38`: a Tatkal charge that needs no clamping) |
| `BranchCoverageTest_train_fare.py` | 100% | 100% |

## Run

```
pip install coverage pytest
coverage run -m pytest CodeCoverageTest_train_fare.py
coverage report -m
coverage run --branch -m pytest BranchCoverageTest_train_fare.py
coverage report -m
```
