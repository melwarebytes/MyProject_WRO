import pytest
from train_fare import base_fare, concession, tatkal_charge

#Example test cases:
def test_sleeper_fare():
    assert base_fare("SL", 500) == 500

def test_adult_no_concession():
    assert concession(30, "M", False) == 0

#Write the rest of the test cases so that the code is 90- 100% covered.
