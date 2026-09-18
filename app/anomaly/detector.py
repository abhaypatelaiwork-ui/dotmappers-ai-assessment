import pandas as pd
import sqlite3
from pathlib import Path
from app.anomaly.rules import (
    flag_stale_high_priority,
    flag_slow_response,
    flag_long_resolution,
    flag_low_rating,
    flag_escalated_stuck,
)
from app.anomaly.stats import flag_zscore, flag_iqr
from app.anomaly.ml_model import flag_isolation_forest

DB_PATH = Path("tickets.db")

def load_data() -> pd.DataFrame:
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM tickets", conn)
    conn.close()
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df

def detect_anomalies() -> dict:
  
    df = load_data()
    all_flags = []
    
    
    all_flags.append(flag_stale_high_priority(df))
    all_flags.append(flag_slow_response(df))
    all_flags.append(flag_long_resolution(df))
    all_flags.append(flag_low_rating(df))
    all_flags.append(flag_escalated_stuck(df))
    
    
    all_flags.append(flag_zscore(df, "resolution_time_hrs", threshold=2.0))
    all_flags.append(flag_iqr(df, "resolution_time_hrs", multiplier=1.5))
    
   
    all_flags.append(flag_isolation_forest(df))
    
    
    combined = pd.concat(all_flags, ignore_index=True)
    combined = combined.fillna("")  
    if "created_at" in combined.columns:
        combined["created_at"] = combined["created_at"].astype(str)
    
    
    reason_counts = combined["reason"].value_counts().to_dict()
    
    
    tickets = combined.to_dict(orient="records")
    
    return {
        "total_anomalies": len(combined),
        "unique_tickets_flagged": combined["ticket_id"].nunique(),
        "by_reason": reason_counts,
        "anomalies": tickets,
    }