# Project Summary: What We Have to Do (Step by Step)

## What is this project?
We are building a **simple chatbot for Statistics Iceland (Hagstofan)**.
A user types a question (like *"What was the inflation in 2024?"* or *"How many people moved to Reykjavík in 2024?"*), our code fetches the real numbers from Statistics Iceland, and an AI turns those numbers into a polite, readable sentence with a link to the official source table.

To pass, we only need:
1. **A working web chat page** (where you type a question and see the answer + source).
2. **A backend** that gets real numbers from Statistics Iceland (never making up numbers).
3. **5–7 short slides** for a quick 10-minute demo showing how it works.

---

## Understanding the 3 Starter Repos (in `linkstorepos.txt`)
The organizers gave everyone 3 different starter options (you only need ONE working system):
1. **Track 1 (`hagstofa-ai-track1-`)**: **Local Vector DB (ChromaDB) + Excel + Ollama.** Already has `app.py` and `ingest.py` ready to go.
2. **Track 2 (`hagstofa-ai-track2-`)**: **Direct Live API (`px.hagstofa.is`).** Already has a FastAPI `app.py` that fetches live numbers from Hagstofan's API without needing a big database.
3. **Track 3 (`gagnvist-starter`)**: **Supercomputer (LUMI in Finland) kit.** Has 5.7 GB of offline data and requires LUMI SSH keys and tunnels. *(Overkill if you don't have LUMI SSH set up!)*

Our plan in `ARCHITECTURE.md` combines the easy parts of **Track 1 & Track 2**: find the right table using search/RAG, fetch the real numbers via the PX-Web API, and show the answer in a Streamlit web page.

> **Important note for Óli about `gagnvist-starter`:**
> Do **NOT** push the whole `gagnvist-starter` folder to our Git repo! It contains ~300 MB of split zip files (`data-release/`) that unpack to 5.7 GB and has its own `.git` folder. Instead, we can just borrow small table description files from `gagnvist-starter/cards/` if needed, and use the lightweight code from Track 1 and Track 2.

---

## How We Use the NVIDIA DGX Spark (128 GB RAM + GB10 GPU)
Think of the **DGX Spark** as our **shared AI powerhouse and central server** so our personal laptops don't have to do heavy lifting:
1. **Runs the AI Models (Ollama + Embeddings):** Our chatbot uses an embedding model (`BAAI/bge-m3`) to search tables and a language model (via Ollama, like `llama3` or a bigger 32B/70B model) to write the final answer. On the Spark, these run in 1–2 seconds instead of slowing down our laptops.
2. **Holds the Vector Database in RAM:** The Spark has 128 GB of memory, so it easily holds ChromaDB and the table catalog in memory.
3. **Our Shared "Meeting Point" for the Demo:**
   - **On our laptops:** We write our separate Python files (`ui.py`, `px_api.py`, `ingest.py`, `search.py`) and push them to GitHub.
   - **On the Spark:** We `git pull` our repo, and run the whole combined system (Ollama + ChromaDB + FastAPI + Streamlit UI) right on the Spark for testing and the final demo.

---

## Step-by-Step Plan (Who Does What)

### Step 1: Set Up the Repo Structure (5 minutes)
So you two don't overwrite each other's files while working on separate computers, **work in separate files**:
- **Óli's files:** `ui.py` (Streamlit chat page) and `px_api.py` (fetching numbers from Hagstofan's API).
- **Siggi's files:** `ingest.py` (putting table descriptions into ChromaDB) and `search.py` (finding the right table for a user's question).
- **Shared file later:** `backend.py` / `app.py` (connects Siggi's search + Óli's API call).

### Step 2: Siggi's Job (Table Search / RAG)
1. **Create `ingest.py`:** Take a list of Hagstofan tables (titles, IDs like `VIS01002`, `MAN00000`, `MAN01002`, and what variables they have) and save them into a local ChromaDB folder. *(You can use the starter code from `hagstofa-ai-track1-` or the table cards from `gagnvist-starter/cards/`).*
2. **Create `search.py`:** Write a single function `find_best_table(question: str)` that searches ChromaDB and returns the best matching table URL/ID.
3. **Test it in terminal:** Make sure asking *"inflation"* returns `VIS01002` and asking *"population"* returns `MAN00000`.

### Step 3: Óli's Job (API Data Fetching & Chat UI)
1. **Create `px_api.py`:** Write a function `fetch_table_data(table_url, question)` that sends a `GET` (for metadata) and `POST` (for numbers) to `https://px.hagstofa.is/...` and returns the real numbers + table title. *(He can copy/adapt the working code directly from `hagstofa-ai-track2-/app.py`!)*
2. **Create `ui.py` (Streamlit):** Build a simple chat page with `st.chat_input()` where a user types a question, sees a loading spinner, and gets back the answer and the source link.

### Step 4: Connect Them Together (Both of You)
1. When the user types a question in Óli's `ui.py`:
   - Call Siggi's `find_best_table(question)` to get the table URL.
   - Pass that URL to Óli's `fetch_table_data(table_url, question)` to get the official numbers.
   - Send the numbers + question to the LLM (or format them cleanly in Python) to write a short answer with the official source link.
2. If no data is found or the API fails, return *"Sorry, I could not find official statistics for that question"* (never guess numbers!).

### Step 5: Test & Make 5 Slides to Pass
1. Test 3–4 real questions in the browser (e.g., inflation in 2024, population, domestic migration).
2. Make a quick 5–7 slide presentation showing:
   - What your chatbot does (screenshot).
   - How it works (Search -> Live PX-API -> Answer with source).
   - One example that works well, and one known limitation.
