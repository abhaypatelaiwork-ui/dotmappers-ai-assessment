import sqlite3
import pandas as pd

conn = sqlite3.connect("tickets.db")


print(pd.read_sql("SELECT COUNT(*) AS total FROM tickets", conn))


print(pd.read_sql(
    "SELECT status, COUNT(*) FROM tickets GROUP BY status", conn))


print(pd.read_sql("SELECT * FROM tickets LIMIT 3", conn))

conn.close()