from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_query import router as query_router
from app.api.routes_anomaly import router as anomaly_router
from app.api.routes_tickets import router as tickets_router
from app.api.schemas import HealthResponse
import sqlite3
from pathlib import Path

app = FastAPI(
    title="DOTMappers Support Ticket AI",
    description="NL query + anomaly detection over support tickets",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers register karo
app.include_router(query_router, tags=["NL Query"])
app.include_router(anomaly_router, tags=["Anomalies"])
app.include_router(tickets_router, tags=["Tickets"])

DB_PATH = Path("tickets.db")

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """System zinda hai ya nahi + DB rows count."""
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    conn.close()
    return HealthResponse(
        status="ok",
        db_rows=count,
        model="gemini-3.6-flash",
    )

@app.get("/", tags=["Health"])
def root():
    return {"message": "DOTMappers AI API", "docs": "/docs"}