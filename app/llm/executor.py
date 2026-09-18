import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("tickets.db")

def execute_sql(sql: str) -> pd.DataFrame:
  
    # Safety: sirf SELECT allow
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Sirf SELECT queries allowed hain!")
    
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(sql, conn)
    finally:
        conn.close()
    return df