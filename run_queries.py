from sql_queries import QUERIES
from database import fetchall

for number, sql in QUERIES.items():
    print(f"\n===== QUERY {number} =====")
    for row in fetchall(sql):
        print(row)
