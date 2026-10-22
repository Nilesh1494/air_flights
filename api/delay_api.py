from datetime import date, timedelta
from api.api_client import request_json
from database import execute


def get_delay(airport_iata, delay_date):
    return request_json(
        f"/airports/iata/{airport_iata}/delays/{delay_date}"
    )


def save_delay(airport_iata, delay_date, data):
    dep = data.get("departuresDelayInformation") or {}
    arr = data.get("arrivalsDelayInformation") or {}

    total = int(dep.get("numTotal", 0) or 0) + int(arr.get("numTotal", 0) or 0)
    cancelled = int(dep.get("numCancelled", 0) or 0) + int(arr.get("numCancelled", 0) or 0)

    medians = [
        x for x in (dep.get("medianDelay"), arr.get("medianDelay"))
        if isinstance(x, (int, float))
    ]
    median = round(sum(medians) / len(medians)) if medians else None

    delayed = 0
    for info in (dep, arr):
        qualified = info.get("numQualifiedTotal")
        if isinstance(qualified, int):
            delayed += max(0, qualified)

    sql = '''
    INSERT INTO airport_delays
    (airport_iata, delay_date, total_flights, delayed_flights,
     avg_delay_min, median_delay_min, canceled_flights)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      total_flights=VALUES(total_flights),
      delayed_flights=VALUES(delayed_flights),
      avg_delay_min=VALUES(avg_delay_min),
      median_delay_min=VALUES(median_delay_min),
      canceled_flights=VALUES(canceled_flights)
    '''

    execute(sql, (
        airport_iata, delay_date, total, delayed,
        None, median, cancelled
    ))


def collect_delays(airport_codes, days_back=3):
    today = date.today()

    for code in airport_codes:
        for offset in range(days_back):
            day = today - timedelta(days=offset)

            try:
                data = get_delay(code, day.isoformat())
                save_delay(code, day, data)
                print(f"Delay saved: {code} {day}")
            except Exception as exc:
                print(f"Delay {code} {day} failed: {exc}")
