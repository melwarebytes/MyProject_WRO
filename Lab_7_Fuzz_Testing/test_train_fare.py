from hypothesis import given, settings, strategies as st
from train_fare import parse_pnr, journey_distance, berth_type, BERTHS

# Each function takes user-typed text, so the fuzzer throws arbitrary Unicode
# strings and None at it. On top of the "must not crash" properties, the
# structured strategies below check that valid input still gives the right answer.

digit = st.sampled_from("0123456789")


# ======================= parse_pnr =======================
@given(st.text() | st.none())
def test_parse_pnr_no_crash(s):
    try:
        parse_pnr(s)
    except Exception as e:
        assert False, f"parse_pnr crashed with: {e!r}"


@given(st.text(alphabet=digit, min_size=10, max_size=10))
def test_parse_pnr_valid_pnr_round_trips(pnr):
    zone, number = parse_pnr(pnr)
    assert zone == int(pnr[0])
    assert number == int(pnr[1:])


@given(st.text(alphabet=digit).filter(lambda t: len(t) != 10))
def test_parse_pnr_rejects_wrong_length(pnr):
    assert parse_pnr(pnr) is None


# =================== journey_distance ====================
@given(st.text() | st.none())
def test_journey_distance_no_crash(s):
    try:
        journey_distance(s)
    except Exception as e:
        assert False, f"journey_distance crashed with: {e!r}"


@given(st.lists(st.integers(min_value=0, max_value=5000), min_size=2))
def test_journey_distance_valid_csv(stops):
    stops = sorted(stops)
    csv = ",".join(str(d) for d in stops)
    assert journey_distance(csv) == stops[-1] - stops[0]


@given(st.lists(st.integers(min_value=0, max_value=5000), min_size=2))
def test_journey_distance_never_negative(stops):
    result = journey_distance(",".join(str(d) for d in stops))
    assert result is None or result >= 0


# ======================= berth_type =======================
@given(st.text() | st.none())
def test_berth_type_no_crash(s):
    try:
        berth_type(s)
    except Exception as e:
        assert False, f"berth_type crashed with: {e!r}"


@given(
    st.sampled_from(["S", "B", "A", "H", "s", "b"]),
    st.integers(min_value=1, max_value=12),
    st.integers(min_value=1, max_value=72),
)
def test_berth_type_valid_seat(prefix, coach_no, seat_no):
    coach, berth = berth_type(f"{prefix}{coach_no}-{seat_no}")
    assert coach == f"{prefix}{coach_no}".upper()
    assert berth == BERTHS[seat_no % 8]


@given(st.integers().filter(lambda n: n < 1 or n > 72))
def test_berth_type_rejects_out_of_range_seat(seat_no):
    assert berth_type(f"S3-{seat_no}") is None
