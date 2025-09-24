# Mini Stocks Analytics

An end-to-end mini project:
- ETL from prepackaged synthetic CSVs
- Feature engineering (returns, MA20/MA50, rolling vol)
- SQLite warehouse table 
- Docker for containerization
- Streamlit UI for inputs, table & chart


## Quickstart (Deployed)
- Open link: https://mini-stock-market-pipeline.streamlit.app/
- Choose ticker names from dropdown
- Choose timeframe for analysis
- Choose between individual tickers to get visualizations
- Export summary csv


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
- **Data quality**: defensive checks (no data -> fail), derived metrics.
- **DevEx**: Docker image, logging, unit test.
- **Analytics**: volatility, MA crossovers.
- **BI**: quick charts and an easy path to Tableau/Looker Studio via SQLite export.
