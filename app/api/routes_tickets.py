import sqlite3
from pathlib import Path
from fastapi import APIRouter, Query
from app.api.schemas import TicketResponse

router = APIRouter()
DB_PATH = Path("tickets.db")

@router.get("/tickets", response_model=TicketResponse)
def list_tickets(
    status: str | None = Query(None),
    priority: str | None = Query(None),
    category: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
   
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if category:
        query += " AND category = ?"
        params.append(category)
    
    query += f" LIMIT {limit}"
    
    import pandas as pd
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    
    return TicketResponse(
        total=len(df),
        tickets=df.fillna("").to_dict(orient="records"),
    )