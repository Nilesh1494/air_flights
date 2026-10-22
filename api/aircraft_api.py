from api.api_client import request_json
from database import execute, fetchall


def get_aircraft(registration):
    return request_json(f"/aircrafts/reg/{registration}")


def get_manufacturer(data):
    manufacturer = data.get("manufacturer")
    if manufacturer:
        return manufacturer

    for field in ("productionLine", "typeName"):
        value = data.get(field)
        if isinstance(value, str) and value:
            return value.split()[0]

    return None


def save_aircraft(data):
    registration = data.get("reg") or data.get("registration")
    model = data.get("typeName") or data.get("model")
    icao_type = (
        data.get("icaoCode")
        or data.get("icaoTypeCode")
        or data.get("icaoType")
        or data.get("iataCodeLong")
        or data.get("modelCode")
    )
    owner = data.get("airlineName") or data.get("owner")
    manufacturer = get_manufacturer(data)

    if not registration:
        return

    sql = '''
    INSERT INTO aircraft
    (registration, model, manufacturer, icao_type_code, owner)
    VALUES (%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      model=VALUES(model),
      manufacturer=VALUES(manufacturer),
      icao_type_code=VALUES(icao_type_code),
      owner=VALUES(owner)
    '''

    execute(sql, (registration, model, manufacturer, icao_type, owner))


def collect_unique_aircraft():
    rows = fetchall('''
        SELECT DISTINCT aircraft_registration
        FROM flights
        WHERE aircraft_registration IS NOT NULL
          AND aircraft_registration <> ''
    ''')

    for row in rows:
        reg = row["aircraft_registration"]
        try:
            data = get_aircraft(reg)
            save_aircraft(data)
            print(f"Aircraft saved: {reg}")
        except Exception as exc:
            print(f"Aircraft {reg} failed: {exc}")
