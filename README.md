# 🎫 DOTMappers Support Ticket AI

An AI-powered system that ingests customer support tickets, answers natural-language
questions, and automatically flags anomalies — exposed via a REST API and a
Streamlit UI.

Built for the DOTMappers AI Engineer assessment.

---

## ✨ Features

| # | Feature | How it works |
|---|---------|--------------|
| 1 | **Ingest & query** | CSV → SQLite (`tickets.db`), queryable via SQL |
| 2 | **Natural-language Q&A** | Gemini 2.0 Flash converts English → SQL → answer |
| 3 | **Anomaly detection** | 5 rules + z-score + IQR + Isolation Forest |
| 4 | **REST API + UI** | FastAPI (4 endpoints) + Streamlit (3 tabs) |

---

## 🏗️ Architecture

```
                    ┌──────────────────────┐
                    │  support_tickets.csv │
                    └──────────┬───────────┘
                               │ ingest.py
                               ▼
                    ┌──────────────────────┐
                    │   SQLite (500 rows)  │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼─────────────────┐
              ▼                ▼                 ▼
      ┌──────────────┐  ┌─────────────┐  ┌─────────────────┐
      │ LangChain +  │  │ Anomaly     │  │  Raw ticket     │
      │ Gemini       │  │ Detector    │  │  filters        │
      │ (NL → SQL)   │  │ (rules+ML)  │  │                 │
      └──────┬───────┘  └──────┬──────┘  └────────┬────────┘
             │                 │                  │
             └────────┬────────┴──────────────────┘
                      ▼
              ┌───────────────┐
              │   FastAPI     │
              │  /query       │
              │  /anomalies   │
              │  /tickets     │
              │  /health      │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │  Streamlit    │
              │  UI (3 tabs)  │
              └───────────────┘
```

**Why this design?**

- **SQLite** — zero setup, portable, evaluator-friendly. 500 rows don't need a real DB.
- **LLM → SQL** — deterministic, verifiable, handles any analytical question the evaluator throws.
- **Rules + ML for anomalies** — rules catch obvious cases (explainable), Isolation Forest catches multivariate surprises.
- **FastAPI + Streamlit** — both required per the brief. Auto-generated `/docs` is a bonus.

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| Data | Pandas + SQLite |
| LLM | Google Gemini 2.0 Flash (free tier) |
| Orchestration | LangChain (LCEL) |
| API | FastAPI + Uvicorn |
| UI | Streamlit |
| Anomaly | Pandas + scikit-learn |
| Container | Docker + docker-compose |

---

## 🚀 Setup & Run

### Option 1 — Docker (recommended)

```bash
# 1. Clone
git clone <your-repo-url>
cd dotmappers-ai-assessment

# 2. Configure
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 3. Run
docker compose up --build
```

- API  → http://localhost:8000
- Docs → http://localhost:8000/docs
- UI   → http://localhost:8501

### Option 2 — Local Python

```bash
# 1. Install
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env          # then add GOOGLE_API_KEY

# 3. Ingest data
python app/ingest.py

# 4. Start API (Terminal 1)
python -m uvicorn app.main:app --reload --port 8000

# 5. Start UI (Terminal 2)
streamlit run ui/streamlit_app.py --server.port 8501
```

---

## 📡 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check + row count |
| POST | `/query` | `{"question": "..."}` → answer + SQL |
| GET | `/anomalies` | Flagged tickets (filters: `reason`, `severity`) |
| GET | `/tickets` | Raw tickets (filters: `status`, `priority`, `category`, `limit`) |

Interactive docs: **http://localhost:8000/docs**

---

## 💬 Example Queries

| Question | What happens |
|----------|--------------|
| `How many tickets are currently open?` | LLM → `SELECT COUNT(*) WHERE status='Open'` |
| `Which agent has the lowest average rating?` | LLM → `GROUP BY agent_id ORDER BY AVG(customer_rating)` |
| `Show me Critical tickets unresolved for 12+ hours` | LLM → filter on priority + resolution_time |
| `Average rating for Technical tickets?` | LLM → `AVG(customer_rating) WHERE category='Technical'` |

Every `/query` response includes the **generated SQL** — full transparency.

---

## 🚨 Anomaly Types

| Rule | Flag when |
|------|-----------|
| `stale_high_priority` | High/Critical, unresolved, > 24h old |
| `slow_first_response` | First reply took > 4h |
| `long_resolution` | Resolved but took > 72h |
| `low_customer_rating` | Rating ≤ 2 |
| `escalated_unresolved` | Escalated but never resolved |
| `zscore_outlier_resolution_time_hrs` | Resolution > mean + 2σ |
| `iqr_outlier_resolution_time_hrs` | Resolution > Q3 + 1.5·IQR |
| `isolation_forest_outlier` | Multivariate outlier (response + resolution + rating) |

---

## ⚠️ Known Limitations

- **Free-tier rate limits** — Gemini free tier caps requests/day. Local Ollama fallback can be added.
- **Static "now"** — "this week" queries anchor to `MAX(created_at)` in the dataset, not real time.
- **No auth** — out of scope for this assessment.
- **SQLite concurrency** — fine for 500 rows, wouldn't scale to millions.
- **LLM hallucination** — mitigated by strict prompt + SQL guard (SELECT-only), but not eliminated.

---

## 📁 Project Structure

```
dotmappers-ai-assessment/
├── app/
│   ├── main.py                 # FastAPI entrypoint
│   ├── config.py               # Centralized config
│   ├── ingest.py               # CSV → SQLite
│   ├── llm/                    # NL → SQL chain
│   ├── anomaly/                # Rules + stats + ML
│   └── api/                    # Routes + schemas
├── ui/
│   ├── streamlit_app.py        # UI entrypoint
│   ├── api_client.py           # HTTP client
│   └── components.py           # Reusable UI blocks
├── data/support_tickets.csv
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🧪 Sample Output

**Request:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How many critical tickets are unresolved?"}'
```

**Response:**
```json
{
  "answer": "Answer: 12",
  "sql": "SELECT COUNT(*) FROM tickets WHERE priority='Critical' AND status != 'Resolved';",
  "rows": [{"COUNT(*)": 12}],
  "row_count": 1,
  "latency_ms": 842.31
}
```

---

## 📄 License

Built for the DOTMappers AI Engineer assessment.