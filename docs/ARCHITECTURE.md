# Hagstofa AI - Hybrid Approach (Hybrid RAG + API)

Goal: Build a smart search engine for official statistics (Statistics Iceland / Hagstofan) that returns accurate, data-backed answers.

Architecture:
1. Language Understanding & Search (RAG): The user asks a question. RAG searches a local vector database (containing Statistics Iceland metadata) to find the right table ID (e.g., VIS01002) and variables.
2. Data Fetching (Direct PX-API): The system builds a JSON query for Statistics Iceland's PX-Web API and fetches real-time data directly from the database.
3. Answer Generation: An LLM takes the API result and phrases it in natural everyday language, including a reference to the source table.

Tech Stack:
- Frontend: Streamlit (Python)
- Backend: FastAPI / Python
- LLM / RAG: Ollama / Hugging Face (run locally or on NVIDIA DGX Spark).
