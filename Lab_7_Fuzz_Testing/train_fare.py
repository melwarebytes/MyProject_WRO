BERTHS = ["SU", "LB", "MB", "UB", "LB", "MB", "UB", "SL"]

PNR_LENGTH = 10
MIN_SEAT, MAX_SEAT = 1, 72          # seats per sleeper / AC coach
MAX_FIELD_LEN = 1000                # guard against huge inputs (DoS)


def _is_ascii_digits(text):
    """True only for non-empty plain 0-9 strings.

    str.isdigit() alone is not enough: it accepts Unicode digits such as
    '²' or '٣' that int() then rejects or silently converts.
    """
    return isinstance(text, str) and text != "" and text.isascii() and text.isdigit()


def parse_pnr(pnr):
    """Split a 10-digit PNR into (zone, number). Returns None if invalid."""
    if not isinstance(pnr, str):
        return None
    pnr = pnr.strip()
    if len(pnr) != PNR_LENGTH or not _is_ascii_digits(pnr):
        return None
    return int(pnr[0]), int(pnr[1:])


def journey_distance(distances_csv):
    """Distance between first and last station from cumulative km markers.

    Returns None for anything that is not at least two non-negative,
    non-decreasing integers separated by commas.
    """
    if not isinstance(distances_csv, str) or len(distances_csv) > MAX_FIELD_LEN:
        return None
    parts = [p.strip() for p in distances_csv.split(",")]
    if len(parts) < 2 or not all(_is_ascii_digits(p) for p in parts):
        return None
    distances = [int(p) for p in parts]
    if any(b < a for a, b in zip(distances, distances[1:])):
        return None                 # km markers can't go backwards
    return distances[-1] - distances[0]


def berth_type(seat):
    """Turn 'S3-45' into ('S3', 'MB'). Returns None if invalid."""
    if not isinstance(seat, str) or len(seat) > MAX_FIELD_LEN:
        return None
    parts = seat.strip().split("-")
    if len(parts) != 2:
        return None
    coach, number = parts[0].strip(), parts[1].strip()
    if not (coach.isascii() and coach.isalnum()) or not _is_ascii_digits(number):
        return None
    seat_no = int(number)
    if not MIN_SEAT <= seat_no <= MAX_SEAT:
        return None
    return coach.upper(), BERTHS[seat_no % 8]


def _show(label, result, hint):
    if result is None:
        print(f"Invalid input. {hint}")
    else:
        print(label, result)


def main():
    print("==== Running parse_pnr ====")
    user_input = input("Enter a 10 digit PNR (e.g. 4521367890): ")
    _show("Zone and Number:", parse_pnr(user_input),
          "PNR must be exactly 10 digits.")

    print("\n==== Running journey_distance ====")
    user_input = input("Enter station distances as CSV (e.g. 0,120,340): ")
    _show("Total Distance:", journey_distance(user_input),
          "Give at least two non-negative, increasing whole numbers.")

    print("\n==== Running berth_type ====")
    user_input = input("Enter coach and seat (e.g. S3-45): ")
    _show("Coach and Berth:", berth_type(user_input),
          "Use COACH-SEAT with a seat number from 1 to 72.")


if __name__ == "__main__":
    main()
