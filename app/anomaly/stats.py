import pandas as pd
import numpy as np

def flag_zscore(df: pd.DataFrame, column: str, threshold: float = 2.0) -> pd.DataFrame:
   
    data = df[df[column].notna()].copy()
    mean = data[column].mean()
    std = data[column].std()
    
    if std == 0:
        return pd.DataFrame() 
    
    data["z_score"] = (data[column] - mean) / std
    mask = data["z_score"].abs() > threshold
    result = data[mask].copy()
    result["reason"] = f"zscore_outlier_{column}"
    result["severity"] = "high"
    return result[["ticket_id", column, "z_score", "reason", "severity"]]

def flag_iqr(df: pd.DataFrame, column: str, multiplier: float = 1.5) -> pd.DataFrame:
    
    data = df[df[column].notna()].copy()
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    upper = Q3 + multiplier * IQR
    lower = Q1 - multiplier * IQR
    
    mask = (data[column] > upper) | (data[column] < lower)
    result = data[mask].copy()
    result["reason"] = f"iqr_outlier_{column}"
    result["severity"] = "medium"
    return result[["ticket_id", column, "reason", "severity"]]