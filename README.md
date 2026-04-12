# ⬡ DataMind — Autonomous AI Data Analyst

A production-grade, full-stack AI data analysis system. Upload any CSV or XLSX dataset, ask questions in plain English, and get instant insights with charts and downloadable PDF reports.

---

## 🏗 Architecture

```
Frontend (React + Vite + Plotly)
        ↕ REST API
Backend (FastAPI + Python)
        ↕
Analysis Engine (Pandas + Scikit-learn + Plotly)
        ↕
PDF Reports (ReportLab)
```

---

## ✨ Features

| Feature | Description |
|---|---|
| **Universal Data Ingestion** | CSV, XLSX — auto-clean, auto-schema detect |
| **Column Intelligence** | Fuzzy-matches column names — never hardcoded |
| **Query Understanding** | Classifies intent: aggregation, trend, correlation, comparison, prediction, distribution, anomaly |
| **7 Analysis Types** | See below |
| **Smart Insights** | Human-readable narratives with key numbers |
| **Interactive Charts** | Plotly — bar, line, heatmap, histogram, scatter, anomaly plot |
| **PDF Reports** | Downloadable per-query report with chart embedding |
| **Search History** | Last 10 queries with FIFO eviction, click to re-run |
| **Auto-Suggestions** | Dataset-aware query suggestions |
| **Anomaly Detection** | IQR-based outlier flagging |

### Analysis Types
- **Aggregation** — sum, mean, max, min, count, median, std (grouped by category)
- **Trend** — time series with resampling, multi-column
- **Correlation** — Pearson heatmap + top pairs with interpretation
- **Comparison** — grouped bar charts with % contribution
- **Prediction** — Linear Regression forecast with R² score
- **Distribution** — Histogram + box plot + skewness + outlier count
- **Anomaly** — IQR method, anomaly scatter plot

---

## 🚀 Setup

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload CSV/XLSX file |
| `POST` | `/analyze` | Run natural language analysis |
| `GET` | `/history` | Last 10 queries |
| `GET` | `/suggestions` | Dataset-aware suggestions |
| `GET` | `/summary` | Dataset overview |
| `GET` | `/report/{id}.pdf` | Download PDF report |
| `GET` | `/health` | Health check |

### POST /analyze Request
```json
{ "query": "What is the average revenue by region?" }
```

### POST /analyze Response
```json
{
  "query": "...",
  "intent": "aggregation",
  "metric": "revenue",
  "aggregation": "mean",
  "group_by": "region",
  "result": "Mean of 'revenue' = 45,230.00",
  "insight": "**North** leads with average revenue of **62,100** (34% of total).",
  "graph": { ... },
  "pdf_link": "/report/abc123.pdf",
  "columns_used": ["revenue", "region"]
}
```

---

## 📂 Project Structure

```
ai_analyst/
├── backend/
│   ├── main.py          # FastAPI app — all-in-one production backend
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Full React dashboard
│   │   └── main.jsx     # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 🔧 Configuration

The backend reads from environment variables (all optional):

| Variable | Default | Description |
|---|---|---|
| `MAX_FILE_SIZE_MB` | `50` | Max upload size |
| `MAX_QUERY_LENGTH` | `2000` | Max query chars |
| `REPORTS_DIR` | `/tmp/ai_analyst_reports` | PDF storage path |

---

## 💡 Example Queries

The system dynamically adapts to your dataset's actual column names:

```
"What is the total revenue?"
"Average sales by region"
"Show the trend of profit over time"
"What columns are correlated?"
"Compare revenue vs profit"
"Predict next month's sales"
"Show distribution of price"
"Detect anomalies in orders"
"Top 10 cities by revenue"
```

---

## 🔑 Design Principles

- **ZERO hardcoded column names** — all detection is dynamic via fuzzy matching
- **Never crashes** — all analysis paths have try/except with informative error messages
- **FIFO history** — oldest entries auto-removed when 10 limit is reached
- **Schema-aware suggestions** — query suggestions generated from actual column names
- **Dark theme** — production-ready UI with DM Mono + Syne typography