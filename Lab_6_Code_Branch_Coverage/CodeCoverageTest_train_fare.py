"""Lab 6 - Code (line) coverage tests for train_fare.py

Goal: execute every line of train_fare.py at least once (>= 90% line coverage).
Run:
    coverage run -m pytest CodeCoverageTest_train_fare.py
    coverage report -m
"""
import pytest
from train_fare import base_fare, concession, tatkal_charge


# ---------- base_fare ----------
def test_sleeper_fare():
    assert base_fare("SL", 500) == 500


def test_unknown_class_raises():
    with pytest.raises(ValueError, match="unknown class"):
        base_fare("3E", 100)


def test_invalid_distance_raises():
    with pytest.raises(ValueError, match="invalid distance"):
        base_fare("SL", 0)


def test_minimum_fare_applied():
    # 1 * 10 = 10, which is below the Rs 50 floor
    assert base_fare("SL", 10) == 50


# ---------- concession ----------
def test_adult_no_concession():
    assert concession(30, "M", False) == 0


def test_tatkal_gets_no_concession():
    assert concession(3, "M", True) == 0


def test_infant_full_concession():
    assert concession(3, "M", False) == 100


def test_child_half_concession():
    assert concession(10, "F", False) == 50


def test_senior_female_concession():
    assert concession(65, "F", False) == 50


def test_senior_male_concession():
    assert concession(65, "M", False) == 40


# ---------- tatkal_charge ----------
def test_tatkal_sleeper_minimum_charge():
    # 500 // 10 = 50 -> raised to minimum of 100
    assert tatkal_charge("SL", 500) == 100


def test_tatkal_ac_capped_charge():
    # 2000 * 3 // 10 = 600 -> capped at 400
    assert tatkal_charge("2A", 2000) == 400
