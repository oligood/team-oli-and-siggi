import os
from threading import Lock
import requests

from search import find_best_table
from px_api import fetch_table_data, is_english_query

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://10.10.40.6:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3:70b")
ollama_lock = Lock()


def generate_llm_answer(question: str, table_title: str, table_id: str, facts_summary: str) -> str:
    is_en = is_english_query(question)
    
    if is_en:
        system_prompt = (
            "You are an official representative for Statistics Iceland (Hagstofa Íslands). "
            "Answer the user's question clearly, politely, and accurately based strictly on the official data provided below. "
            "Never guess or make up numbers that are not in the data. "
            "Always reference the official table code in your answer."
        )
    else:
        system_prompt = (
            "Þú ert upplýsingafulltrúi hjá Hagstofu Íslands. "
            "Svaraðu spurningu notandans skýrt, kurteislega og nákvæmlega eingöngu út frá gefnum opinberum tölum hér að neðan. "
            "Aldrei giska á tölur eða búa til tölur sem eru ekki í gögnunum. "
            "Nefndu töfluheiti eða töflunúmer í svarinu."
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
            res = requests.post(OLLAMA_URL, json=payload, timeout=15)
        if res.status_code == 200:
            text = res.json().get("response", "").strip()
            if text:
                return text
    except Exception:
        pass

    return facts_summary


def answer_question(question: str) -> dict:
    if not question.strip():
        return {
            "ok": False,
            "answer": "Vinsamlegast sláðu inn spurningu.",
            "svar": "Vinsamlegast sláðu inn spurningu.",
            "table": "NONE",
            "action": "REJECT",
        }

    is_en = is_english_query(question)
    matched_table = find_best_table(question)

    if not matched_table:
        if is_en:
            msg = (
                "Sorry, I could not find an official Statistics Iceland table matching this query. "
                "I can currently provide statistics for the Consumer Price Index (inflation), population figures, "
                "municipalities, Reykjavík districts, internal migration, the wage index, unemployment rates, "
                "and airport passenger traffic."
            )
        else:
            msg = (
                "Því miður hef ég ekki aðgang að opinberri Hagstofutöflu sem svarar þessari fyrirspurn. "
                "Ég hef aðgang að opinberum tölum um vísitölu neysluverðs (verðbólgu), lykiltölur mannfjölda, "
                "sveitarfélög, hverfi í Reykjavík, búferlaflutninga, launavísitölu, atvinnuleysi og farþega um Keflavíkurflugvöll."
            )
        return {
            "ok": False,
            "answer": msg,
            "svar": msg,
            "table": "NONE",
            "action": "REJECT",
        }

    api_result = fetch_table_data(matched_table["url"], question)

    if not api_result.get("ok"):
        err_msg = api_result.get("error", "óþekkt villa")
        if is_en:
            msg = f"Unable to fetch official data from Statistics Iceland ({err_msg})."
        else:
            msg = f"Því miður tókst ekki að sækja opinberar tölur frá Hagstofu Íslands fyrir þessa fyrirspurn ({err_msg})."
        return {
            "ok": False,
            "answer": msg,
            "svar": msg,
            "table": matched_table.get("id"),
            "table_id": matched_table.get("id"),
            "source_url": matched_table.get("url"),
            "action": "FAIL",
        }

    answer_text = generate_llm_answer(
        question=question,
        table_title=api_result["title"],
        table_id=api_result["table_id"],
        facts_summary=api_result["summary"],
    )

    action_type = "FETCH_SPECIFIC" if any(char.isdigit() for char in question) else "FETCH_LATEST"
    model_prompt = (
        f"Kerfi: Hagstofa Íslands Assistant (70B)\n"
        f"Tafla: {api_result['table_id']} - {api_result['title']}\n"
        f"Útdráttur: {api_result['summary']}\n"
        f"Spurning: {question}"
    )

    return {
        "ok": True,
        "answer": answer_text,
        "svar": answer_text,
        "table": api_result["table_id"],
        "table_id": api_result["table_id"],
        "title": api_result["title"],
        "source_url": api_result["source_url"],
        "action": action_type,
        "model_prompt": model_prompt,
        "raw_data": api_result.get("query_used", []),
        "raw_px": api_result.get("query_used", []),
        "facts": api_result["facts"],
        "summary": api_result["summary"],
        "query_used": api_result.get("query_used", []),
        "structured_data": api_result.get("structured_data", []),
        "computed": api_result.get("computed", {}),
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
        query: str = ""
        prompt: str = ""
        spurning: str = ""

    @app.post("/query")
    def query_endpoint(req: QueryRequest):
        q = req.query or req.prompt or req.spurning
        return answer_question(q)

    @app.post("/spyrja")
    def spyrja_endpoint(req: QueryRequest):
        q = req.spurning or req.query or req.prompt
        return answer_question(q)

except ImportError:
    app = None
