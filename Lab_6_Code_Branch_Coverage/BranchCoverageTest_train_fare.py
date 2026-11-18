"""Lab 6 - Branch coverage tests for train_fare.py

Goal: make every decision (if / elif / else) evaluate both True and False
(>= 90% branch coverage), including boundary values.
Run:
    coverage run --branch -m pytest BranchCoverageTest_train_fare.py
    coverage report -m
"""
import pytest
from train_fare import base_fare, concession, tatkal_charge, RATE_PER_KM


# ================= base_fare =================
# Branch 1: travel_class not in RATE_PER_KM -> True / False
def test_unknown_class_raises():
    with pytest.raises(ValueError, match="unknown class"):
        base_fare("3E", 100)


def test_class_is_case_sensitive():
    with pytest.raises(ValueError, match="unknown class"):
        base_fare("sl", 100)


# Branch 2: distance_km <= 0 -> True (zero and negative) / False
@pytest.mark.parametrize("distance", [0, -1, -250])
def test_invalid_distance_raises(distance):
    with pytest.raises(ValueError, match="invalid distance"):
        base_fare("SL", distance)


# Branch 3: fare < 50 -> True / False, plus the boundary at exactly 50
def test_fare_below_minimum_is_raised_to_50():
    assert base_fare("SL", 10) == 50


def test_fare_exactly_50_is_unchanged():
    assert base_fare("SL", 50) == 50


def test_fare_just_above_minimum():
    assert base_fare("SL", 51) == 51


@pytest.mark.parametrize("cls, rate", list(RATE_PER_KM.items()))
def test_every_class_rate(cls, rate):
    assert base_fare(cls, 500) == rate * 500


def test_short_first_class_trip_hits_minimum():
    # 5 * 9 = 45 -> raised to 50
    assert base_fare("1A", 9) == 50


# ================= concession =================
# Branch: is_tatkal True / False
@pytest.mark.parametrize("age, gender", [(3, "M"), (10, "F"), (70, "F"), (30, "M")])
def test_tatkal_never_gets_concession(age, gender):
    assert concession(age, gender, True) == 0


# Branch: age < 5 True / False (boundary 4 vs 5)
def test_infant_full_concession():
    assert concession(0, "M", False) == 100
    assert concession(4, "F", False) == 100


# Branch: age <= 12 True / False (boundary 5 and 12 vs 13)
def test_child_half_concession_boundaries():
    assert concession(5, "M", False) == 50
    assert concession(12, "F", False) == 50


def test_teenager_gets_no_concession():
    assert concession(13, "M", False) == 0


# Branch: age >= 60 True / False (boundary 59 vs 60)
def test_adult_just_below_senior_age():
    assert concession(59, "F", False) == 0


def test_adult_no_concession():
    assert concession(30, "M", False) == 0


# Branch: gender == "F" True / False inside the senior block
def test_senior_female_concession():
    assert concession(60, "F", False) == 50


def test_senior_male_concession():
    assert concession(60, "M", False) == 40


def test_senior_other_gender_gets_male_rate():
    assert concession(75, "O", False) == 40


# ================= tatkal_charge =================
# Branch: travel_class == "SL" True / False
# Then: charge > 400 / charge < 100 / neither (within range)
def test_sleeper_charge_within_range():
    # 2000 // 10 = 200
    assert tatkal_charge("SL", 2000) == 200


def test_sleeper_charge_raised_to_minimum():
    # 500 // 10 = 50 -> 100
    assert tatkal_charge("SL", 500) == 100


def test_sleeper_charge_capped_at_maximum():
    # 5000 // 10 = 500 -> 400
    assert tatkal_charge("SL", 5000) == 400


def test_ac_charge_within_range():
    # 1000 * 3 // 10 = 300
    assert tatkal_charge("3A", 1000) == 300


def test_ac_charge_capped_at_maximum():
    # 2000 * 3 // 10 = 600 -> 400
    assert tatkal_charge("2A", 2000) == 400


def test_ac_charge_raised_to_minimum():
    # 200 * 3 // 10 = 60 -> 100
    assert tatkal_charge("1A", 200) == 100


def test_charge_boundaries_are_not_clamped():
    # exactly 400 and exactly 100 stay as they are
    assert tatkal_charge("SL", 4000) == 400
    assert tatkal_charge("SL", 1000) == 100
