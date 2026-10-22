import pandas as pd
import plotly.express as px
import streamlit as st

from database import fetchall
from sql_queries import QUERIES


st.set_page_config(page_title="Air Tracker", page_icon="✈️", layout="wide")


def as_frame(rows):
    return pd.DataFrame(rows)


def show_table(rows, empty_message="No records found."):
    frame = as_frame(rows)
    if frame.empty:
        st.info(empty_message)
    else:
        st.dataframe(frame, width="stretch", hide_index=True)
    return frame


QUERY_LABELS = {
    1: "Show the total number of flights for each aircraft model, listing the model and its count.",
    2: "List all aircraft (registration, model) that have been assigned to more than 5 flights.",
    3: "For each airport, display its name and the number of outbound flights, but only for airports with more than 5 flights.",
    4: "Find the top 3 destination airports (name, city) by number of arriving flights, sorted by count descending.",
    5: "Show for each flight: number, origin, destination, and a label 'Domestic' or 'International' using CASE WHEN on country match.",
    6: "Show the 5 most recent arrivals at DEL airport including flight number, aircraft, departure airport name, and arrival time, ordered by latest arrival.",
    7: "Find all airports with no arriving flights (never used as a destination in flights table).",
    8: "For each airline, count the number of flights by status using CASE WHEN.",
    9: "Show all cancelled flights, with aircraft and both airports, ordered by departure time descending.",
    10: "List all city pairs (origin-destination) that have more than 2 different aircraft models operating flights between them.",
    11: "For each destination airport, compute the percentage of delayed flights among all arrivals, sorted by highest percentage.",
}

st.title("Air Tracker: Flight Analytics")

try:
    summary = fetchall('''
        SELECT
            (SELECT COUNT(*) FROM airport) AS airports,
            (SELECT COUNT(*) FROM flights) AS flights,
            (SELECT COUNT(*) FROM aircraft) AS aircraft,
            (SELECT AVG(GREATEST(TIMESTAMPDIFF(
                MINUTE, scheduled_arrival, actual_arrival
            ), 0))
             FROM flights
             WHERE scheduled_arrival IS NOT NULL
               AND actual_arrival IS NOT NULL) AS average_delay
    ''')[0]
except Exception as exc:
    st.error(f"Could not read the flight analytics database: {exc}")
    st.stop()

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Airports", summary["airports"])
metric_2.metric("Flights", summary["flights"])
metric_3.metric("Aircraft", summary["aircraft"])
metric_4.metric(
    "Average arrival delay",
    f"{summary['average_delay']:.1f} min" if summary["average_delay"] else "No data",
)

dashboard_tab, flights_tab, airport_tab, delays_tab, routes_tab, queries_tab = st.tabs(
    [
        "Dashboard",
        "Flight Search",
        "Airport Details",
        "Delay Analysis",
        "Routes",
        "SQL Queries",
    ]
)

with dashboard_tab:
    st.subheader("Airport Activity")
    airport_activity = fetchall('''
        SELECT a.iata_code, a.name, COUNT(f.flight_id) AS flight_count
        FROM airport a
        LEFT JOIN flights f
            ON f.origin_iata = a.iata_code OR f.destination_iata = a.iata_code
        GROUP BY a.airport_id, a.iata_code, a.name
        ORDER BY flight_count DESC
        LIMIT 10
    ''')
    activity_frame = show_table(airport_activity, "Collect airport and flight data to see activity.")
    if not activity_frame.empty:
        chart = px.bar(
            activity_frame,
            x="iata_code",
            y="flight_count",
            color="flight_count",
            hover_name="name",
            color_continuous_scale="Teal",
        )
        chart.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(chart, width="stretch")

with flights_tab:
    st.subheader("Search Flights")
    filter_data = fetchall('''
        SELECT MIN(DATE(scheduled_departure)) AS earliest_date,
               MAX(DATE(scheduled_departure)) AS latest_date
        FROM flights
        WHERE scheduled_departure IS NOT NULL
    ''')[0]
    status_rows = fetchall(
        "SELECT DISTINCT status FROM flights WHERE status IS NOT NULL ORDER BY status"
    )
    airline_rows = fetchall(
        "SELECT DISTINCT airline_code FROM flights WHERE airline_code IS NOT NULL ORDER BY airline_code"
    )
    origin_rows = fetchall(
        "SELECT DISTINCT origin_iata FROM flights WHERE origin_iata IS NOT NULL ORDER BY origin_iata"
    )

    filter_1, filter_2, filter_3, filter_4 = st.columns(4)
    flight_number = filter_1.text_input("Flight number")
    selected_status = filter_2.selectbox(
        "Status", ["All"] + [row["status"] for row in status_rows]
    )
    selected_airline = filter_3.selectbox(
        "Airline", ["All"] + [row["airline_code"] for row in airline_rows]
    )
    selected_origin = filter_4.selectbox(
        "Origin", ["All"] + [row["origin_iata"] for row in origin_rows]
    )

    date_range = None
    if filter_data["earliest_date"] and filter_data["latest_date"]:
        date_range = st.date_input(
            "Scheduled departure range",
            value=(filter_data["earliest_date"], filter_data["latest_date"]),
            min_value=filter_data["earliest_date"],
            max_value=filter_data["latest_date"],
        )

    flight_sql = '''
        SELECT flight_number, airline_code, aircraft_registration, origin_iata,
               destination_iata, scheduled_departure, actual_departure,
               scheduled_arrival, actual_arrival, status
        FROM flights
        WHERE 1 = 1
    '''
    flight_params = []
    if flight_number:
        flight_sql += " AND flight_number LIKE %s"
        flight_params.append(f"%{flight_number}%")
    if selected_status != "All":
        flight_sql += " AND status = %s"
        flight_params.append(selected_status)
    if selected_airline != "All":
        flight_sql += " AND airline_code = %s"
        flight_params.append(selected_airline)
    if selected_origin != "All":
        flight_sql += " AND origin_iata = %s"
        flight_params.append(selected_origin)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        flight_sql += " AND DATE(scheduled_departure) BETWEEN %s AND %s"
        flight_params.extend(date_range)
    flight_sql += " ORDER BY scheduled_departure DESC LIMIT 500"
    show_table(fetchall(flight_sql, flight_params), "No flights match these filters.")

with airport_tab:
    st.subheader("Airport Details")
    airports = fetchall('''
        SELECT iata_code, name, city, country, continent, latitude, longitude, timezone
        FROM airport
        ORDER BY name
    ''')
    airport_options = {
        f"{row['iata_code']} - {row['name']}": row for row in airports if row["iata_code"]
    }
    if not airport_options:
        st.info("Collect airport data to use the airport viewer.")
    else:
        selected_label = st.selectbox("Airport", list(airport_options))
        selected_airport = airport_options[selected_label]
        detail_1, detail_2, detail_3 = st.columns(3)
        detail_1.metric("City", selected_airport["city"] or "Unknown")
        detail_2.metric("Country", selected_airport["country"] or "Unknown")
        detail_3.metric("Timezone", selected_airport["timezone"] or "Unknown")
        st.caption(
            f"Coordinates: {selected_airport['latitude']}, {selected_airport['longitude']}"
        )
        st.markdown("#### Linked Flights")
        linked_flights = fetchall('''
            SELECT flight_number, airline_code, origin_iata, destination_iata,
                   scheduled_departure, scheduled_arrival, status
            FROM flights
            WHERE origin_iata = %s OR destination_iata = %s
            ORDER BY scheduled_departure DESC
            LIMIT 200
        ''', (selected_airport["iata_code"], selected_airport["iata_code"]))
        show_table(linked_flights, "No linked flights were found.")

with delays_tab:
    st.subheader("Delay Analysis")
    delay_rows = fetchall('''
        SELECT COALESCE(a.name, f.destination_iata) AS airport,
               f.destination_iata AS airport_iata,
               COUNT(*) AS total_flights,
               SUM(CASE WHEN TIMESTAMPDIFF(
                   MINUTE, f.scheduled_arrival, f.actual_arrival
               ) > 0 THEN 1 ELSE 0 END) AS delayed_flights,
               ROUND(AVG(GREATEST(TIMESTAMPDIFF(
                   MINUTE, f.scheduled_arrival, f.actual_arrival
               ), 0)), 1) AS average_delay_minutes,
               ROUND(100.0 * SUM(CASE WHEN TIMESTAMPDIFF(
                   MINUTE, f.scheduled_arrival, f.actual_arrival
               ) > 0 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2)
                   AS delayed_percentage
        FROM flights f
        LEFT JOIN airport a ON a.iata_code = f.destination_iata
        WHERE f.destination_iata IS NOT NULL
          AND f.scheduled_arrival IS NOT NULL
          AND f.actual_arrival IS NOT NULL
        GROUP BY f.destination_iata, a.name
        ORDER BY delayed_percentage DESC, average_delay_minutes DESC
    ''')
    delay_frame = show_table(delay_rows, "Collect flight timing data to see airport delay analysis.")
    if not delay_frame.empty:
        delay_chart = px.bar(
            delay_frame,
            x="airport_iata",
            y="delayed_percentage",
            color="average_delay_minutes",
            hover_name="airport",
            labels={"delayed_percentage": "Delayed flights (%)"},
            color_continuous_scale="Reds",
        )
        delay_chart.update_layout(coloraxis_colorbar_title="Average delay (min)")
        st.plotly_chart(delay_chart, width="stretch")

with routes_tab:
    st.subheader("Route Leaderboards")
    route_column, airport_column = st.columns(2)
    with route_column:
        st.markdown("#### Busiest Routes")
        busiest_routes = fetchall('''
            SELECT origin_iata, destination_iata, COUNT(*) AS flight_count
            FROM flights
            WHERE origin_iata IS NOT NULL AND destination_iata IS NOT NULL
            GROUP BY origin_iata, destination_iata
            ORDER BY flight_count DESC
            LIMIT 10
        ''')
        show_table(busiest_routes, "No complete routes found.")
    with airport_column:
        st.markdown("#### Most Delayed Airports")
        delayed_airports = fetchall('''
            SELECT COALESCE(a.name, f.destination_iata) AS airport,
                   f.destination_iata AS airport_iata,
                   ROUND(100.0 * SUM(CASE WHEN TIMESTAMPDIFF(
                       MINUTE, f.scheduled_arrival, f.actual_arrival
                   ) > 0 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2)
                       AS delayed_percentage
            FROM flights f
            LEFT JOIN airport a ON a.iata_code = f.destination_iata
            WHERE f.destination_iata IS NOT NULL
              AND f.scheduled_arrival IS NOT NULL
              AND f.actual_arrival IS NOT NULL
            GROUP BY f.destination_iata, a.name
            ORDER BY delayed_percentage DESC
            LIMIT 10
        ''')
        show_table(delayed_airports, "No delay data found.")

with queries_tab:
    st.subheader("SQL Query Execution")
    selected_query = st.selectbox(
        "Select query",
        options=list(QUERIES),
        format_func=lambda number: f"Query {number}: {QUERY_LABELS[number]}",
    )
    st.caption(QUERY_LABELS[selected_query])
    st.code(QUERIES[selected_query], language="sql")

    if st.button("Run Selected Query", type="primary"):
        try:
            show_table(fetchall(QUERIES[selected_query]))
        except Exception as exc:
            st.error(f"Query could not be executed: {exc}")

    with st.expander("Project Evaluation Criteria"):
        st.markdown(
            """
            1. Data Extraction Accuracy: successful API retrieval without missing values.
            2. SQL Database Design: normalized tables and correct relationships.
            3. Query Efficiency: optimized queries that retrieve insights quickly.
            4. Streamlit Application Functionality: smooth navigation and interactive displays.
            5. Project Completeness: end-to-end API, SQL, and dashboard workflow.
            6. Documentation Quality: all required project files are available in GitHub.
            7. Presentation and Usability: intuitive views with meaningful insights.
            8. Error Handling and Innovation: resilient API/database handling and useful analysis.
            """
        )
