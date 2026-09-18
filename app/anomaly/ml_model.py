import pandas as pd
from sklearn.ensemble import IsolationForest

def flag_isolation_forest(df: pd.DataFrame) -> pd.DataFrame:
   
    features = ["response_time_hrs", "resolution_time_hrs", "customer_rating"]
    data = df[features].dropna().copy()
    
    if len(data) < 10:
        return pd.DataFrame() 
    
    model = IsolationForest(
        contamination=0.05,      
        random_state=42
    )
    data["anomaly"] = model.fit_predict(data[features])
    data["score"] = model.decision_function(data[features])
    
    result = data[data["anomaly"] == -1].copy()
    
    result = result.join(df[["ticket_id"]].loc[result.index])
    result["reason"] = "isolation_forest_outlier"
    result["severity"] = "high"
    return result[["ticket_id", "response_time_hrs", "resolution_time_hrs",
                   "customer_rating", "score", "reason", "severity"]]