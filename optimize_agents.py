"""
optimize_agents.py - LLM-as-a-Judge & Agentic Stress Testing Loop across Epochs

Reads 'stress_tests.json' (Golden Dataset / Fasit-skrá) and evaluates:
1. Table Retrieval Accuracy (Verifies that find_best_table matches expected_table)
2. Payload & Action Matching (Verifies REJECT, FETCH_LATEST, FETCH_SPECIFIC)
3. Hallucination Detection:
   - Deterministic Number Verifier: Ensures no numbers in the natural language
     answer were fabricated or hallucinated outside the raw Hagstofa API payload.
   - LLM-as-a-Judge: If Ollama (e.g. Llama 3 70B on NVIDIA DGX Spark) is reachable,
     prompts the LLM judge to verify factual accuracy and absence of hallucinations.
"""

import os
import re
import json
import time
import requests
from search import find_best_table
from px_api import fetch_table_data
from backend import generate_llm_answer, answer_question, MODEL_NAME

STRESS_TESTS_FILE = os.getenv("STRESS_TESTS_FILE", "stress_tests.json")
JUDGE_OLLAMA_URL = os.getenv("JUDGE_OLLAMA_URL", os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate"))
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "llama3:70b")
ENABLE_LLM_JUDGE = os.getenv("ENABLE_LLM_JUDGE", "false").lower() in ("true", "1", "yes")

REPORT_PATH = "docs/EVALUATION_REPORT.md"
REPORTS_DIR = "docs/reports"
HISTORY_PATH = os.path.join(REPORTS_DIR, "history.json")
RUN_NOTE = os.getenv("RUN_NOTE", "")  # Optional comment for the leaderboard, e.g. RUN_NOTE="Post-fix search.py"

# EVALUATION_REPORT.md is partly hand-written; each run only replaces the text between these markers
LEADERBOARD_START, LEADERBOARD_END = "<!-- AUTO:LEADERBOARD:START -->", "<!-- AUTO:LEADERBOARD:END -->"
LATEST_START, LATEST_END = "<!-- AUTO:LATEST:START -->", "<!-- AUTO:LATEST:END -->"


def load_stress_tests(file_path: str = STRESS_TESTS_FILE) -> list:
    """Loads stress test cases supporting both standard JSON lists and JSONL format."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fann ekki prófunarskrá: '{file_path}'")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
        return [data]
    except json.JSONDecodeError:
        cases = []
        for line in content.splitlines():
            line = line.strip()
            if line:
                cases.append(json.loads(line))
        return cases


def extract_answer_numbers(text: str) -> set:
    """Extracts all numeric tokens from natural language text, normalizing decimals & thousands."""
    # Convert date ordinals like "1. janúar" -> "1 janúar"
    clean_text = re.sub(r"(\d+)\.\s*(?=[a-zA-ZáéíóúýþæöÁÉÍÓÚÝÞÆÖ])", r"\1 ", str(text))
    tokens = re.findall(r"\b\d+(?:[\.,]\d+)*\b", clean_text)
    nums = set()

    for tok in tokens:
        # Icelandic thousands with dot: 40.286 or 394.324
        if re.match(r"^\d{1,3}(?:\.\d{3})+$", tok):
            nums.add(round(float(tok.replace(".", "")), 2))
        # English thousands with comma: 40,286
        elif re.match(r"^\d{1,3}(?:,\d{3})+$", tok):
            nums.add(round(float(tok.replace(",", "")), 2))
        # Icelandic decimal with comma: 5,90 or 700,40
        elif re.match(r"^\d+,\d+$", tok):
            nums.add(round(float(tok.replace(",", ".")), 2))
        # English decimal with dot: 5.90 or 700.40
        elif re.match(r"^\d+\.\d{1,2}$", tok):
            nums.add(round(float(tok), 2))
        else:
            try:
                nums.add(round(float(tok), 2))
            except ValueError:
                pass
    return nums


def extract_allowed_numbers(api_res: dict, query: str = "") -> set:
    """Extracts all legitimate numbers present in raw Hagstofa API data, computed metrics, and question."""
    allowed = {1.0, 12.0}  # Common context constants (1st of month, 12-month change)

    data_str = (
        str(api_res.get("facts", []))
        + " "
        + str(api_res.get("computed", {}))
        + " "
        + str(api_res.get("query_used", []))
        + " "
        + str(query)
    )

    for tok in re.findall(r"\b\d+(?:[\.,]\d+)*\b", data_str):
        clean = tok.replace(",", ".")
        try:
            allowed.add(round(float(clean), 2))
        except ValueError:
            pass

    for d in re.findall(r"\d+", data_str):
        allowed.add(round(float(d), 2))

    # Include digits from table ID (e.g. MAN02005 -> 2005, 2005.0)
    table_id = api_res.get("table_id", "")
    for d in re.findall(r"\d+", table_id):
        allowed.add(round(float(d), 2))

    return allowed


def evaluate_hallucinations(answer: str, api_result: dict, query: str) -> dict:
    """
    Evaluation function:
    Checks if the final natural language answer includes any hallucinated numbers
    that were not present anywhere in the raw API response or query.
    """
    ans_nums = extract_answer_numbers(answer)
    allowed_nums = extract_allowed_numbers(api_result, query)
    hallucinated = ans_nums - allowed_nums

    return {
        "passed": len(hallucinated) == 0,
        "hallucinated_numbers": sorted(list(hallucinated)),
        "found_numbers": sorted(list(ans_nums)),
    }


def call_llm_as_a_judge(raw_facts: str, answer: str, query: str) -> dict:
    """
    LLM-as-a-Judge:
    Queries a large model (e.g. Llama 3 70B on NVIDIA DGX Spark) to verify factual adherence.
    """
    prompt = (
        "Þú ert óháður dómari (LLM-as-a-Judge) sem metur áreiðanleika gagna fyrir Hagstofu Íslands.\n\n"
        f"Opinber raungögn frá Hagstofunni:\n{raw_facts}\n\n"
        f"Spurning notandans:\n{query}\n\n"
        f"Svar frá AI-kerfinu:\n{answer}\n\n"
        "Verkefni: Er AI-kerfið að ljúga, giska eða búa til tölur (hallucinate) sem ekki eru studdar af gögnunum?\n"
        "Svaraðu nákvæmlega á eftirfarandi formi:\n"
        "DÓMUR: [PASS eða FAIL]\n"
        "RÖK: [Stutt útskýring]"
    )
    payload = {
        "model": JUDGE_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0},
    }
    try:
        res = requests.post(JUDGE_OLLAMA_URL, json=payload, timeout=20)
        if res.status_code == 200:
            text = res.json().get("response", "").strip()
            verdict = "PASS" if "PASS" in text.upper() and "FAIL" not in text.upper() else "FAIL"
            return {"active": True, "verdict": verdict, "notes": text}
    except Exception:
        pass

    return {"active": False, "verdict": "SKIPPED", "notes": "LLM Judge not reached / offline"}


class StressTestRunner:
    def __init__(self, test_cases: list):
        self.test_cases = test_cases

    def run_epoch(self, epoch_num: int) -> dict:
        print(f"\n=======================================================")
        print(f" 🧪 KEYRI STRESS TESTS & LLM-AS-A-JUDGE - EPOCH {epoch_num}")
        print(f"=======================================================")

        table_matches = 0
        action_matches = 0
        hallucination_passes = 0
        total = len(self.test_cases)
        latencies = []
        epoch_details = []

        for idx, case in enumerate(self.test_cases, 1):
            query = case.get("query") or case.get("question")
            expected_table = case.get("expected_table", "NONE")
            expected_action = case.get("expected_action", "FETCH_LATEST")
            t_start = time.time()

            # 1. Verify Table Matching
            matched_tbl = find_best_table(query)
            matched_id = matched_tbl["id"] if matched_tbl else "NONE"
            table_pass = (matched_id == expected_table)
            if table_pass:
                table_matches += 1

            # 2. Verify Action & Retrieve Data
            action_pass = False
            hallucination_result = {"passed": True, "hallucinated_numbers": []}
            judge_feedback = {"active": False, "verdict": "SKIPPED"}
            final_answer = ""
            raw_facts = ""

            if expected_action == "REJECT":
                # System must reject out-of-domain queries gracefully
                res = answer_question(query)
                action_pass = (res.get("ok") is False)
                final_answer = res.get("answer", "")
                # Rejections must not contain made-up statistics
                hallucination_result = evaluate_hallucinations(final_answer, {}, query)

            else:
                # Normal retrieval (FETCH_LATEST or FETCH_SPECIFIC)
                if matched_tbl:
                    api_res = fetch_table_data(matched_tbl["url"], query)
                    action_pass = api_res.get("ok", False)
                    raw_facts = api_res.get("summary", "")
                    
                    final_answer = generate_llm_answer(
                        question=query,
                        table_title=api_res.get("title", ""),
                        table_id=matched_id,
                        facts_summary=raw_facts,
                    )

                    # 3. Check for Hallucinated Numbers
                    hallucination_result = evaluate_hallucinations(final_answer, api_res, query)

                    # 4. LLM-as-a-Judge (if enabled or available on Spark)
                    if ENABLE_LLM_JUDGE:
                        judge_feedback = call_llm_as_a_judge(raw_facts, final_answer, query)

            if action_pass:
                action_matches += 1

            dur = time.time() - t_start
            latencies.append(dur)

            hallu_pass = hallucination_result["passed"]
            if hallu_pass:
                hallucination_passes += 1

            overall_pass = table_pass and action_pass and hallu_pass
            status_str = "PASS" if overall_pass else "FAIL"

            print(
                f"[{status_str}] #{idx:02d} Q: '{query}' | "
                f"Tafla: {matched_id} (búist við: {expected_table}) | "
                f"Action: {expected_action} ({'OK' if action_pass else 'FAIL'}) | "
                f"Hallucination: {'0' if hallu_pass else 'FAIL ' + str(hallucination_result['hallucinated_numbers'])} "
                f"[{dur:.2f}s]"
            )

            epoch_details.append({
                "query": query,
                "expected_table": expected_table,
                "matched_table": matched_id,
                "table_pass": table_pass,
                "expected_action": expected_action,
                "action_pass": action_pass,
                "hallucination_free": hallu_pass,
                "hallucinated_numbers": hallucination_result["hallucinated_numbers"],
                "judge_verdict": judge_feedback["verdict"],
                "overall_pass": overall_pass,
                "latency_sec": round(dur, 3),
                "answer": final_answer,
            })

        table_accuracy = round((table_matches / total) * 100, 1)
        action_accuracy = round((action_matches / total) * 100, 1)
        hallu_free_pct = round((hallucination_passes / total) * 100, 1)
        avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
        overall_passes = sum(1 for d in epoch_details if d["overall_pass"])

        summary = {
            "epoch": epoch_num,
            "total_tests": total,
            "overall_pass_pct": round((overall_passes / total) * 100, 1),
            "table_retrieval_pct": table_accuracy,
            "action_match_pct": action_accuracy,
            "hallucination_free_pct": hallu_free_pct,
            "avg_latency_sec": avg_latency,
            "details": epoch_details,
        }

        print(f"\n--- SAMANTEKT EPOCH {epoch_num} ---")
        print(f"• Table Match Accuracy       : {table_accuracy}% ({table_matches}/{total})")
        print(f"• Expected Action & Payload  : {action_accuracy}% ({action_matches}/{total})")
        print(f"• Zero Hallucinated Numbers  : {hallu_free_pct}% ({hallucination_passes}/{total})")
        print(f"• Meðalviðbragðstími         : {avg_latency} sek")
        return summary


def _load_run_history() -> list:
    if not os.path.exists(HISTORY_PATH):
        return []
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-")


def _pass_mark(ok: bool) -> str:
    return "✅" if ok else "❌"


def render_run_details(run: dict, epochs: list, test_cases: list) -> str:
    """Markdown breakdown of one run: epoch summary plus per-test results of the final epoch."""
    lines = [
        f"- **Dagsetning:** {run['timestamp']}",
        f"- **Svarlíkan:** `{run['answer_model']}`",
        f"- **Dómari (LLM-as-a-Judge):** `{run['judge_model']}`" if run["judge_enabled"] else "- **Dómari (LLM-as-a-Judge):** óvirkur",
        f"- **Prófunarskrá:** `{STRESS_TESTS_FILE}` ({len(test_cases)} tilvik)",
        "",
        "#### Niðurstöður yfir Epochs",
        "",
        "| Epoch | Heildarárangur | Table Match | Action / API Match | Zero Hallucinated Numbers | Meðaltími |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for h in epochs:
        lines.append(
            f"| {h['epoch']} | {h['overall_pass_pct']}% | {h['table_retrieval_pct']}% | {h['action_match_pct']}% "
            f"| {h['hallucination_free_pct']}% | {h['avg_latency_sec']}s |"
        )

    lines += [
        "",
        f"#### Sundurliðun prófa (epoch {epochs[-1]['epoch']})",
        "",
        "| # | Niðurstaða | Spurning | Tafla (vænt) | Action | Ofskynjaðar tölur | Dómari |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for idx, d in enumerate(epochs[-1]["details"], 1):
        table_cell = f"`{d['matched_table']}`"
        if not d["table_pass"]:
            table_cell += f" (vænt `{d['expected_table']}`)"
        hallu_cell = ", ".join(str(n) for n in d["hallucinated_numbers"]) if d["hallucinated_numbers"] else "–"
        query = d["query"].replace("|", "\\|")
        lines.append(
            f"| {idx} | {_pass_mark(d['overall_pass'])} | {query} | {table_cell} "
            f"| `{d['expected_action']}` {_pass_mark(d['action_pass'])} | {hallu_cell} | {d['judge_verdict']} |"
        )
    return "\n".join(lines) + "\n"


def render_leaderboard(history: list) -> str:
    lines = [
        "| Keyrsla | Dagsetning & Tími | Dómara-módel | Prófunarsett | Table Match | Action Match | Zero Hallucination | Meðalsvartími | Athugasemdir |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for n, h in enumerate(history, 1):
        judge = f"`{h['judge_model']}`" if h.get("judge_enabled") else "– (óvirkur)"
        test_set = h.get("test_set") or f"{h['total_tests']} próf"
        note = h.get("note", "")
        if h.get("archive"):
            note = f"{note} ([skýrsla]({h['archive']}))".strip()
        lines.append(
            f"| **Run {n}** | {h['timestamp'][:16]} | {judge} | {test_set} "
            f"| **{h['table_retrieval_pct']}%** | **{h['action_match_pct']}%** | **{h['hallucination_free_pct']}%** "
            f"| {h['avg_latency_sec']}s | {note} |"
        )
    return "\n".join(lines) + "\n"


def _replace_block(doc: str, start: str, end: str, body: str) -> str:
    block = f"{start}\n{body}{end}"
    if start in doc and end in doc:
        return doc[:doc.index(start)] + block + doc[doc.index(end) + len(end):]
    return doc.rstrip() + f"\n\n{block}\n"


def save_reports(epochs: list, test_cases: list) -> None:
    """
    Appends this run to the run history, archives the full run under docs/reports/,
    and refreshes the auto-generated leaderboard and latest-run sections of
    docs/EVALUATION_REPORT.md, leaving the hand-written analysis untouched.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    final = epochs[-1]
    now = time.localtime()

    run = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", now),
        "answer_model": MODEL_NAME,
        "judge_model": JUDGE_MODEL,
        "judge_enabled": ENABLE_LLM_JUDGE,
        "total_tests": len(test_cases),
        "epochs": len(epochs),
        "overall_pass_pct": final["overall_pass_pct"],
        "table_retrieval_pct": final["table_retrieval_pct"],
        "action_match_pct": final["action_match_pct"],
        "hallucination_free_pct": final["hallucination_free_pct"],
        "avg_latency_sec": final["avg_latency_sec"],
        "note": RUN_NOTE,
    }

    model_tag = _safe_name(JUDGE_MODEL if ENABLE_LLM_JUDGE else MODEL_NAME)
    archive_name = f"eval_{model_tag}_{len(test_cases)}tests_{time.strftime('%Y%m%d-%H%M%S', now)}.md"
    run["archive"] = f"reports/{archive_name}"

    details_md = render_run_details(run, epochs, test_cases)
    with open(os.path.join(REPORTS_DIR, archive_name), "w", encoding="utf-8") as f:
        f.write(f"# Matskeyrsla {run['timestamp']}\n\n")
        f.write(details_md)

    history = _load_run_history()
    history.append(run)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    doc = "# LLM-as-a-Judge Evaluation & Stress Testing Benchmark\n"
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            doc = f.read()
    doc = _replace_block(doc, LEADERBOARD_START, LEADERBOARD_END, render_leaderboard(history))
    doc = _replace_block(doc, LATEST_START, LATEST_END, details_md)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(doc)

    print(f"\n✅ Matsskýrsla uppfærð í '{REPORT_PATH}' ({len(history)} keyrslur í sögu).")
    print(f"✅ Keyrsla vistuð í '{os.path.join(REPORTS_DIR, archive_name)}'.")

def run_evaluation_loop(num_epochs: int = 2):
    test_cases = load_stress_tests(STRESS_TESTS_FILE)
    print(f"Hleð inn {len(test_cases)} prófunartilvikum úr '{STRESS_TESTS_FILE}'...")
    runner = StressTestRunner(test_cases)
    history = []

    for ep in range(1, num_epochs + 1):
        summary = runner.run_epoch(ep)
        history.append(summary)

    print("\n=======================================================")
    print(" 🏆 LOKANIÐURSTÖÐUR - STRESS TESTS (LLM-AS-A-JUDGE)")
    print("=======================================================")
    print(f"{'Epoch':<8} {'Table Match':<14} {'Action/API':<14} {'0-Hallucination':<18} {'Latency':<10}")
    print("-" * 64)
    for h in history:
        print(
            f"{h['epoch']:<8} "
            f"{str(h['table_retrieval_pct']) + '%':<14} "
            f"{str(h['action_match_pct']) + '%':<14} "
            f"{str(h['hallucination_free_pct']) + '%':<18} "
            f"{str(h['avg_latency_sec']) + 's':<10}"
        )

    save_reports(history, test_cases)
    return history


if __name__ == "__main__":
    run_evaluation_loop(num_epochs=2)
