import pandas as pd
from datetime import datetime


def get_reference_now(df: pd.DataFrame) -> pd.Timestamp:
    """Dataset ka max created_at = 'aaj'."""
    return df["created_at"].max()

def flag_stale_high_priority(df: pd.DataFrame) -> pd.DataFrame:
    """
    High/Critical priority tickets jo 24 ghante se zyada purane
    hain aur abhi tak resolved nahi hue.
    """
    now = get_reference_now(df)
    mask = (
        df["priority"].isin(["High", "Critical"])
        & (df["status"] != "Resolved")
        & ((now - df["created_at"]).dt.total_seconds() / 3600 > 24)
    )
    result = df[mask].copy()
    result["reason"] = "stale_high_priority"
    result["severity"] = "high"
    return result[["ticket_id", "priority", "status", "created_at", "reason", "severity"]]

def flag_slow_response(df: pd.DataFrame) -> pd.DataFrame:
    """Jin tickets ka first response 4 ghante se zyada tha."""
    mask = df["response_time_hrs"] > 4.0
    result = df[mask].copy()
    result["reason"] = "slow_first_response"
    result["severity"] = "medium"
    return result[["ticket_id", "response_time_hrs", "agent_id", "reason", "severity"]]

def flag_long_resolution(df: pd.DataFrame) -> pd.DataFrame:
    """Jin resolved tickets ko 72 ghante se zyada lage."""
    mask = df["resolution_time_hrs"] > 72.0
    result = df[mask].copy()
    result["reason"] = "long_resolution"
    result["severity"] = "high"
    return result[["ticket_id", "resolution_time_hrs", "agent_id", "reason", "severity"]]

def flag_low_rating(df: pd.DataFrame) -> pd.DataFrame:
    """Jin tickets ko 2 ya usse kam rating mili."""
    mask = df["customer_rating"] <= 2
    result = df[mask].copy()
    result["reason"] = "low_customer_rating"
    result["severity"] = "medium"
    return result[["ticket_id", "customer_rating", "agent_id", "reason", "severity"]]

def flag_escalated_stuck(df: pd.DataFrame) -> pd.DataFrame:
    """Escalated tickets jo resolve nahi hue."""
    mask = (df["status"] == "Escalated")
    result = df[mask].copy()
    result["reason"] = "escalated_unresolved"
    result["severity"] = "high"
    return result[["ticket_id", "priority", "agent_id", "reason", "severity"]]