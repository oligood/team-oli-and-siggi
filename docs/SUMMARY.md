# Project Summary & Step-by-Step Plan

## Overview
We are building a chatbot for Statistics Iceland (Hagstofan) using a hybrid RAG + live PX-Web API setup.
When a user asks a question, our system:
1. Searches ChromaDB to find the right Statistics Iceland table (`search.py`).
2. Queries Statistics Iceland's live PX-Web API (`px.hagstofa.is`) to get the official numbers (`px_api.py`).
3. Uses Ollama (running on the DGX Spark) to write a clear answer based strictly on those numbers, including the source table link (`backend.py` and `ui.py`).

## Starter Repos Reference
From the 3 hackathon tracks in `linkstorepos.txt`:
- **Track 1 (`hagstofa-ai-track1-`)**: Local ChromaDB + Ollama + FastAPI setup.
- **Track 2 (`hagstofa-ai-track2-`)**: Direct PX-Web API querying with FastAPI.
- **Track 3 (`gagnvist-starter`)**: LUMI supercomputer starter kit (contains ~300 MB of split zip archives in `data-release/` that unpack to 5.7 GB, so we do not commit `gagnvist-starter` into our repo).

Our project combines Track 1 (vector search for table metadata) and Track 2 (live PX-Web API data retrieval).

## Role of the NVIDIA DGX Spark (128 GB RAM, GB10)
We use the DGX Spark as our central backend and AI server:
- Runs Ollama (`llama3` / `hagstofa-ai:latest`) and the embedding model (`SentenceTransformer`) on the GPU so responses take 1–2 seconds.
- Holds the ChromaDB vector index in memory.
- Runs the combined FastAPI backend and Streamlit UI for testing and the final demo.

## File Structure & Task Split
- `ingest.py` (Siggi): Fetches table metadata from the PX-Web API and stores embeddings in `./chroma_db`.
- `search.py` (Siggi): Searches `./chroma_db` for the closest matching table given a user question.
- `px_api.py` (Óli): Sends `GET` (metadata) and `POST` (data filter) requests to `px.hagstofa.is` and formats the returned numbers.
- `backend.py` (Shared): FastAPI server (`/query`) connecting `search.py`, `px_api.py`, and Ollama.
- `ui.py` (Óli): Streamlit chat interface for asking questions and displaying answers with source links.

## Running the Project
1. Install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Build the local vector database:
   ```bash
   python ingest.py
   ```
3. Start the FastAPI backend:
   ```bash
   uvicorn backend:app --reload --host 0.0.0.0 --port 8000
   ```
4. Start the Streamlit frontend:
   ```bash
   streamlit run ui.py
   ```
