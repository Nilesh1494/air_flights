QUERIES = {
1: '''
SELECT a.model, COUNT(f.flight_id) AS flight_count
FROM aircraft a
JOIN flights f ON f.aircraft_registration = a.registration
GROUP BY a.model;
''',
2: '''
SELECT a.registration, a.model, COUNT(f.flight_id) AS flight_count
FROM aircraft a
JOIN flights f ON f.aircraft_registration = a.registration
GROUP BY a.registration, a.model
HAVING COUNT(f.flight_id) > 3;
''',
3: '''
SELECT a.name, COUNT(f.flight_id) AS outbound_flights
FROM airport a
JOIN flights f ON f.origin_iata = a.iata_code
GROUP BY a.airport_id, a.name
HAVING COUNT(f.flight_id) > 3;
''',
4: '''
SELECT a.name, a.city, COUNT(f.flight_id) AS arriving_flights
FROM airport a
JOIN flights f ON f.destination_iata = a.iata_code
GROUP BY a.airport_id, a.name, a.city
ORDER BY arriving_flights DESC
LIMIT 3;
''',
5: '''
SELECT f.flight_number, o.name AS origin, d.name AS destination,
CASE WHEN o.country = d.country THEN 'Domestic'
     ELSE 'International' END AS flight_type
FROM flights f
LEFT JOIN airport o ON o.iata_code = f.origin_iata
LEFT JOIN airport d ON d.iata_code = f.destination_iata;
''',
6: '''
SELECT f.flight_number, f.aircraft_registration AS aircraft,
o.name AS departure_airport,
COALESCE(f.actual_arrival, f.scheduled_arrival) AS arrival_time
FROM flights f
LEFT JOIN airport o ON o.iata_code = f.origin_iata
WHERE f.destination_iata = 'DEL'
ORDER BY arrival_time DESC
LIMIT 5;
''',
7: '''
SELECT a.name, a.iata_code
FROM airport a
LEFT JOIN flights f ON f.destination_iata = a.iata_code
WHERE f.flight_id IS NULL;
''',
8: '''
SELECT airline_code,
SUM(CASE WHEN status = 'On Time' THEN 1 ELSE 0 END) AS on_time,
SUM(CASE WHEN status = 'Delayed' THEN 1 ELSE 0 END) AS delayed_flights,
SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled
FROM flights
GROUP BY airline_code
ORDER BY airline_code;
''',
9: '''
SELECT f.flight_number, f.aircraft_registration,
o.name AS origin_airport, d.name AS destination_airport,
f.scheduled_departure
FROM flights f
LEFT JOIN airport o ON o.iata_code = f.origin_iata
LEFT JOIN airport d ON d.iata_code = f.destination_iata
WHERE LOWER(f.status) = 'cancelled'
ORDER BY f.scheduled_departure DESC;
''',
10: '''
SELECT f.origin_iata, f.destination_iata,
COUNT(DISTINCT a.model) AS aircraft_models
FROM flights f
JOIN aircraft a ON a.registration = f.aircraft_registration
GROUP BY f.origin_iata, f.destination_iata
HAVING COUNT(DISTINCT a.model) > 2
ORDER BY aircraft_models DESC;
''',
11: '''
SELECT d.name AS destination_airport,
ROUND(100.0 *
SUM(CASE WHEN LOWER(f.status) = 'delayed' THEN 1 ELSE 0 END)
 / NULLIF(COUNT(f.flight_id), 0), 2) AS delayed_percentage
FROM airport d
JOIN flights f ON f.destination_iata = d.iata_code
GROUP BY d.airport_id, d.name
ORDER BY delayed_percentage DESC;
'''
}
