import time
from fastapi import APIRouter, HTTPException
from app.api.schemas import QueryRequest, QueryResponse
from app.llm.chain import generate_sql
from app.llm.executor import execute_sql

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
def nl_query(req: QueryRequest):
    
    start = time.time()
    
    try:
       
        sql = generate_sql(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
    
    try:
        
        df = execute_sql(sql)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL execution failed: {str(e)}")
    
    
    if df.empty:
        answer = "Koi result nahi mila is question ke liye."
    elif len(df) == 1 and len(df.columns) == 1:
        
        val = df.iloc[0, 0]
        answer = f"Answer: {val}"
    else:
       
        answer = f"{len(df)} rows mile. Pehla result: {df.iloc[0].to_dict()}"
    
    latency = (time.time() - start) * 1000
    
    return QueryResponse(
        answer=answer,
        sql=sql,
        rows=df.fillna("").to_dict(orient="records"),
        row_count=len(df),
        latency_ms=round(latency, 2),
    )