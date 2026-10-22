from datetime import datetime, timezone

from api.api_client import request_json
from database import execute, execute_many


FLIGHT_UPSERT_SQL = '''
INSERT INTO flights
(flight_id, flight_number, aircraft_registration, origin_iata,
 destination_iata, scheduled_departure, actual_departure,
 scheduled_arrival, actual_arrival, status, airline_code)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE
  aircraft_registration=VALUES(aircraft_registration),
  actual_departure=VALUES(actual_departure),
  actual_arrival=VALUES(actual_arrival),
  status=VALUES(status),
  airline_code=VALUES(airline_code)
'''

def get_airport_iata(obj):
    airport = obj.get("airport") or {}

    return (
        airport.get("iata")
        or airport.get("iataCode")
    )


def get_time(obj, key):
    value = obj.get(key) or {}

    return (
        value.get("utc")
        or value.get("local")
    )
    
def get_actual_time(obj):
    for key in ("revisedTime", "actualTime", "estimatedTime"):
        value = obj.get(key) or {}

        if value.get("local") or value.get("utc"):
            return (
                value.get("local")
                or value.get("utc")
            )

    return None


def normalize_datetime(value):
    """Convert an AeroDataBox timestamp into a timezone-free UTC datetime."""
    if not value or not isinstance(value, str):
        return value

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value

    if parsed.tzinfo is None:
        return parsed

    return parsed.astimezone(timezone.utc).replace(tzinfo=None)
    

def get_airport_flights(iata_code):
    """Get a 12-hour flight window using the AeroDataBox query options."""
    params = {
        "withPrivate": "true",
        "withCodeshared": "true",
        "withCargo": "true",
        "offsetMinutes": "-120",
        "durationMinutes": "720",
        "withCancelled": "true",
        "withLeg": "true",
        "withLocation": "false",
    }

    return request_json(
        f"/flights/airports/iata/{iata_code}",
        params=params,
        timeout=90,
    )


def save_flight(flight):
    execute(FLIGHT_UPSERT_SQL, parse_flight(flight))

def parse_flight(flight, origin_fallback=None, destination_fallback=None):
    """
    Convert AeroDataBox flight JSON into
    values required by the flights table.
    """

    departure = flight.get("departure") or {}
    arrival = flight.get("arrival") or {}
    aircraft = flight.get("aircraft") or {}
    airline = flight.get("airline") or {}

    flight_number = (
        flight.get("number")
        or flight.get("flightNumber")
    )

    aircraft_registration = (
        aircraft.get("reg")
        or aircraft.get("registration")
    )

    origin_iata = get_airport_iata(departure) or origin_fallback
    destination_iata = get_airport_iata(arrival) or destination_fallback

    scheduled_departure = get_time(
        departure,
        "scheduledTime"
    )

    scheduled_arrival = get_time(arrival, "scheduledTime")

    actual_departure = get_actual_time(
        departure
    )

    actual_arrival = get_actual_time(
        arrival
    )

    airline_code = (
        airline.get("iata")
        or airline.get("icao")
        or airline.get("iataCode")
        or airline.get("icaoCode")
    )

    # Create a unique ID for the flight
    flight_id = "|".join([
        str(flight_number or ""),
        str(scheduled_departure or ""),
        str(origin_iata or ""),
        str(destination_iata or "")
    ])

    return (
        flight_id,
        flight_number,
        aircraft_registration,
        origin_iata,
        destination_iata,
        normalize_datetime(scheduled_departure),
        normalize_datetime(actual_departure),
        normalize_datetime(scheduled_arrival),
        normalize_datetime(actual_arrival),
        flight.get("status"),
        airline_code
    )
    
def save_flights_response(data, airport_iata):
    rows = []

    for flight in data.get("departures", []) or []:
        rows.append(parse_flight(flight, origin_fallback=airport_iata))

    for flight in data.get("arrivals", []) or []:
        rows.append(parse_flight(flight, destination_fallback=airport_iata))

    rows_by_id = {row[0]: row for row in rows}
    execute_many(FLIGHT_UPSERT_SQL, list(rows_by_id.values()))
    return len(rows_by_id)
