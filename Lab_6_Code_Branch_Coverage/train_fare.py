RATE_PER_KM = {"SL": 1, "3A": 2, "2A": 3, "1A": 5}


def base_fare(travel_class, distance_km):
    if travel_class not in RATE_PER_KM:
        raise ValueError("unknown class")
    if distance_km <= 0:
        raise ValueError("invalid distance")
    fare = RATE_PER_KM[travel_class] * distance_km
    if fare < 50:
        fare = 50
    return fare


def concession(age, gender, is_tatkal):
    if is_tatkal:
        return 0
    if age < 5:
        return 100
    elif age <= 12:
        return 50
    elif age >= 60:
        if gender == "F":
            return 50
        return 40
    return 0


def tatkal_charge(travel_class, fare):
    if travel_class == "SL":
        charge = fare // 10
    else:
        charge = fare * 3 // 10
    if charge > 400:
        charge = 400
    elif charge < 100:
        charge = 100
    return charge
