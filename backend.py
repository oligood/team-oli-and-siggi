import os
from threading import Lock
import requests

from search import find_best_table
from px_api import fetch_table_data

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3")
ollama_lock = Lock()


def generate_llm_answer(question: str, table_title: str, table_id: str, facts_summary: str) -> str:
    system_prompt = (
        "Þú ert upplýsingafulltrúi hjá Hagstofu Íslands. "
        "Svaraðu spurningu notandans stuttlega og nákvæmlega eingöngu út frá gefnum tölum hér að neðan. "
        "Aldrei giska á tölur eða búa til tölur sem eru ekki í gögnunum. "
        "Ef spurt er á ensku skaltu svara á ensku, annars á íslensku. "
        "Nefndu töfluheitið í svarinu."
    )
    full_prompt = (
        f"{system_prompt}\n\n"
        f"Tafla: {table_id} - {table_title}\n"
        f"Gögn frá Hagstofu: {facts_summary}\n\n"
        f"Spurning: {question}\nSvar:"
    )
    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }

    try:
        with ollama_lock:
            res = requests.post(OLLAMA_URL, json=payload, timeout=45)
        if res.status_code == 200:
            text = res.json().get("response", "").strip()
            if text:
                return text
    except Exception:
        pass

    return f"Samkvæmt töflu {table_id} ({table_title}) hjá Hagstofu Íslands: {facts_summary}"


def answer_question(question: str) -> dict:
    if not question.strip():
        return {"ok": False, "answer": "Vinsamlegast sláðu inn spurningu."}

    matched_table = find_best_table(question)
    api_result = fetch_table_data(matched_table["url"], question)

    if not api_result.get("ok"):
        return {
            "ok": False,
            "answer": (
                "Því miður tókst ekki að sækja opinberar tölur frá Hagstofu Íslands "
                f"fyrir þessa fyrirspurn ({api_result.get('error', 'óþekkt villa')})."
            ),
            "table_id": matched_table["id"],
            "source_url": matched_table["url"],
        }

    answer_text = generate_llm_answer(
        question=question,
        table_title=api_result["title"],
        table_id=api_result["table_id"],
        facts_summary=api_result["summary"],
    )

    return {
        "ok": True,
        "answer": answer_text,
        "svar": answer_text,
        "table_id": api_result["table_id"],
        "title": api_result["title"],
        "source_url": api_result["source_url"],
        "facts": api_result["facts"],
        "summary": api_result["summary"],
    }


try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    app = FastAPI(title="Hagstofa AI Backend")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class QueryRequest(BaseModel):
        prompt: str = ""
        spurning: str = ""

    @app.post("/query")
    def query_endpoint(req: QueryRequest):
        q = req.prompt or req.spurning
        return answer_question(q)

    @app.post("/spyrja")
    def spyrja_endpoint(req: QueryRequest):
        q = req.spurning or req.prompt
        return answer_question(q)

except ImportError:
    app = None
