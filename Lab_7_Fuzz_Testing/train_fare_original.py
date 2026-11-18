BERTHS = ["SU", "LB", "MB", "UB", "LB", "MB", "UB", "SL"]

def parse_pnr(pnr):
    return int(pnr[0]), int(pnr[1:])

def journey_distance(distances_csv):
    distances = [int(d) for d in distances_csv.split(',')]
    return distances[-1] - distances[0]

def berth_type(seat):
    coach, number = seat.split('-')
    return coach.upper(), BERTHS[int(number) % 8]

def main():
    print("==== Running parse_pnr ====")
    user_input = input("Enter a 10 digit PNR (e.g. 4521367890): ")
    result = parse_pnr(user_input)
    print("Zone and Number:", result)

    print("\n==== Running journey_distance ====")
    user_input = input("Enter station distances as CSV (e.g. 0,120,340): ")
    result = journey_distance(user_input)
    print("Total Distance:", result)

    print("\n==== Running berth_type ====")
    user_input = input("Enter coach and seat (e.g. S3-45): ")
    result = berth_type(user_input)
    print("Coach and Berth:", result)

if __name__ == "__main__":
    main()
