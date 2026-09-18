import pandas as pd
import sqlite3
from pathlib import Path

# Paths
CSV_PATH = Path("data/support_tickets.csv")
DB_PATH = Path("tickets.db")

def ingest_data():
   
    
    # 1. CSV load karo
    print(f"📂 Loading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # 2. Date column ko proper datetime banao
    df["created_at"] = pd.to_datetime(df["created_at"])
    
    # 3. Column names check karo
    print(f"📋 Columns: {list(df.columns)}")
    
    # 4. Missing values dekho
    print(f"❓ Missing values:\n{df.isnull().sum()}")
    
    # 5. SQLite mein save karo
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("tickets", conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ Data saved to {DB_PATH}")
    
    return df

if __name__ == "__main__":
    ingest_data()