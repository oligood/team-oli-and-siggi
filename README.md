# team-oli-and-siggi

Hagstofa AI chatbot using hybrid RAG (ChromaDB) and live Statistics Iceland PX-Web API queries.

See [`docs/SUMMARY.md`](docs/SUMMARY.md) and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for details.

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python ingest.py
uvicorn backend:app --reload --port 8000
streamlit run ui.py
```
