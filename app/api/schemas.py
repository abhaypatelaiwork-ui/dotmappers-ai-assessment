from pydantic import BaseModel, Field
from typing import Any, Optional


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500,
                          description="Natural language question")

class QueryResponse(BaseModel):
    answer: str
    sql: str
    rows: list[dict[str, Any]]
    row_count: int
    latency_ms: float


class AnomalyItem(BaseModel):
    ticket_id: str
    reason: str
    severity: str
    details: dict[str, Any] = {}

class AnomalyResponse(BaseModel):
    total_anomalies: int
    unique_tickets_flagged: int
    by_reason: dict[str, int]
    anomalies: list[dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    db_rows: int
    model: str


class TicketResponse(BaseModel):
    total: int
    tickets: list[dict[str, Any]]