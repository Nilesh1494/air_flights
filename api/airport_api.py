from api.api_client import request_json
from database import execute


def get_airport(iata_code):
    return request_json(f"/airports/iata/{iata_code}")


def get_text(value, *keys):
    """Return a text value from either a string or a nested API object."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in keys:
            if value.get(key) is not None:
                return value[key]
    return None


def save_airport(data):
    sql = '''
    INSERT INTO airport
    (icao_code, iata_code, name, city, country, continent,
     latitude, longitude, timezone)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      icao_code=VALUES(icao_code),
      name=VALUES(name),
      city=VALUES(city),
      country=VALUES(country),
      continent=VALUES(continent),
      latitude=VALUES(latitude),
      longitude=VALUES(longitude),
      timezone=VALUES(timezone)
    '''

    location = data.get("location") or {}

    execute(sql, (
        data.get("icao"),
        data.get("iata") or data.get("code"),
        data.get("fullName") or data.get("shortName") or data.get("name"),
        data.get("municipalityName") or data.get("city"),
        get_text(data.get("country"), "name", "code"),
        get_text(data.get("continent"), "name", "code"),
        location.get("lat", data.get("latitude")),
        location.get("lon", data.get("longitude")),
        data.get("timeZone") or data.get("time_zone"),
    ))
