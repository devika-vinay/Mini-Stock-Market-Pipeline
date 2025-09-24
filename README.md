# Mini Stocks Analytics

An end-to-end mini project:
- ETL from prepackaged synthetic CSVs
- Feature engineering (returns, MA20/MA50, rolling vol)
- SQLite warehouse table 
- Streamlit UI for inputs, table & chart
- Docker for containerization

## Quickstart (Local)
```bash
pip install -r requirements.txt
streamlit run src/app_streamlit.py
```
Open http://localhost:8501


## Run with Docker
```bash
docker build -t mini-pipeline-ui .
docker run --rm -p 8501:8501 mini-pipeline-ui
```

## What This Demonstrates 

- **Pipelines & ETL**: repeatable UI to ingest, transform, and load curated tables.
- **Data quality**: defensive checks (no data -> fail fast), derived metrics.
- **DevEx**: Docker image, CLI args, logging, unit test.
- **Analytics**: volatility, MA crossovers, Sharpe-friendly features.
- **BI**: quick charts and an easy path to Tableau/Looker Studio via SQLite export.
