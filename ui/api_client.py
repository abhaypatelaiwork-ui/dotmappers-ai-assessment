import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8080").rstrip("/")
TIMEOUT = 30
QUERY_TIMEOUT = 120


def health_check() -> dict:
    
    try:
        r = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def ask_question(question: str) -> dict:
    
    try:
        r = requests.post(
            f"{API_URL}/query",
            json={"question": question},
            timeout=QUERY_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"API error: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}


def get_anomalies(reason: str | None = None, severity: str | None = None) -> dict:
    
    params = {}
    if reason:
        params["reason"] = reason
    if severity:
        params["severity"] = severity
    try:
        r = requests.get(f"{API_URL}/anomalies", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "anomalies": [], "total_anomalies": 0}


def get_tickets(status: str | None = None, priority: str | None = None,
                category: str | None = None, limit: int = 100) -> dict:
   
    params = {"limit": limit}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if category:
        params["category"] = category
    try:
        r = requests.get(f"{API_URL}/tickets", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "tickets": [], "total": 0}