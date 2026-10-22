from database import execute

TABLES = [
    '''
    CREATE TABLE IF NOT EXISTS airport (
        airport_id INT AUTO_INCREMENT PRIMARY KEY,
        icao_code VARCHAR(4) UNIQUE,
        iata_code VARCHAR(3) UNIQUE,
        name VARCHAR(255) NOT NULL,
        city VARCHAR(120),
        country VARCHAR(120),
        continent VARCHAR(64),
        latitude DECIMAL(9,6),
        longitude DECIMAL(9,6),
        timezone VARCHAR(100)
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS aircraft (
        aircraft_id INT AUTO_INCREMENT PRIMARY KEY,
        registration VARCHAR(20) UNIQUE,
        model VARCHAR(100),
        manufacturer VARCHAR(100),
        icao_type_code VARCHAR(30),
        owner VARCHAR(150)
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS flights (
        flight_id VARCHAR(255) PRIMARY KEY,
        flight_number VARCHAR(50),
        aircraft_registration VARCHAR(20),
        origin_iata VARCHAR(3),
        destination_iata VARCHAR(3),
        scheduled_departure DATETIME NULL,
        actual_departure DATETIME NULL,
        scheduled_arrival DATETIME NULL,
        actual_arrival DATETIME NULL,
        status VARCHAR(50),
        airline_code VARCHAR(20),
        INDEX idx_origin (origin_iata),
        INDEX idx_destination (destination_iata),
        INDEX idx_aircraft (aircraft_registration),
        INDEX idx_departure (scheduled_departure)
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS airport_delays (
        delay_id INT AUTO_INCREMENT PRIMARY KEY,
        airport_iata VARCHAR(3),
        delay_date DATE,
        total_flights INT DEFAULT 0,
        delayed_flights INT DEFAULT 0,
        avg_delay_min INT NULL,
        median_delay_min INT NULL,
        canceled_flights INT DEFAULT 0,
        UNIQUE KEY uq_airport_date (airport_iata, delay_date)
    )
    '''
]

for table_sql in TABLES:
    execute(table_sql)

print("Database tables created successfully.")
