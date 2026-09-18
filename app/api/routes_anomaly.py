from fastapi import APIRouter, Query
from app.api.schemas import AnomalyResponse
from app.anomaly.detector import detect_anomalies

router = APIRouter()

@router.get("/anomalies", response_model=AnomalyResponse)
def get_anomalies(
    reason: str | None = Query(None, description="Filter by reason"),
    severity: str | None = Query(None, description="Filter by severity"),
):
   
    result = detect_anomalies()
    
    anomalies = result["anomalies"]
    
    if reason:
        anomalies = [a for a in anomalies if a.get("reason") == reason]
    if severity:
        anomalies = [a for a in anomalies if a.get("severity") == severity]
    
    return AnomalyResponse(
        total_anomalies=len(anomalies),
        unique_tickets_flagged=len({a["ticket_id"] for a in anomalies}),
        by_reason=result["by_reason"],
        anomalies=anomalies,
    )