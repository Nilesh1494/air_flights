# Air Tracker: Flight Analytics

Python + AeroDataBox RapidAPI + MySQL + Streamlit.

## Setup
1. Create MySQL database: `CREATE DATABASE flight_analytics;`
2. Copy `.env.example` to `.env`.
3. Put your RapidAPI key in `.env`.
4. Install: `pip install -r requirements.txt`
5. Create tables: `python setup_database.py`
6. Collect data: `python main.py`
7. Run dashboard: `streamlit run app.py`

Never commit `.env` or expose your API key.
