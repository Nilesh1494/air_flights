from config import AIRPORT_CODES, DAYS_BACK
from api.airport_api import get_airport, save_airport
from api.flight_api import get_airport_flights, save_flights_response
from api.aircraft_api import collect_unique_aircraft
from api.delay_api import collect_delays


def main():
    print("=== AIR TRACKER DATA COLLECTION ===")

    print("\n[1/4] Collecting airports...")
    for code in AIRPORT_CODES:
        try:
            save_airport(get_airport(code))
            print(f"Airport saved: {code}")
        except Exception as exc:
            print(f"Airport {code} failed: {exc}")

    print("\n[2/4] Collecting flights...")
    for code in AIRPORT_CODES:
        try:
            data = get_airport_flights(code)
            count = save_flights_response(data)
            print(f"{code}: {count} flights processed")
        except Exception as exc:
            print(f"Flights {code} failed: {exc}")

    print("\n[3/4] Collecting unique aircraft...")
    collect_unique_aircraft()

    print("\n[4/4] Collecting airport delays...")
    collect_delays(AIRPORT_CODES, DAYS_BACK)

    print("\n=== COLLECTION COMPLETE ===")


if __name__ == "__main__":
    main()
