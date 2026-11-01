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
from backend import generate_llm_answer, answer_question

STRESS_TESTS_FILE = os.getenv("STRESS_TESTS_FILE", "stress_tests.json")
JUDGE_OLLAMA_URL = os.getenv("JUDGE_OLLAMA_URL", os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate"))
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "llama3:70b")
ENABLE_LLM_JUDGE = os.getenv("ENABLE_LLM_JUDGE", "false").lower() in ("true", "1", "yes")


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
                "latency_sec": round(dur, 3),
                "answer": final_answer,
            })

        table_accuracy = round((table_matches / total) * 100, 1)
        action_accuracy = round((action_matches / total) * 100, 1)
        hallu_free_pct = round((hallucination_passes / total) * 100, 1)
        avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

        summary = {
            "epoch": epoch_num,
            "total_tests": total,
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

    # Save report
    os.makedirs("docs", exist_ok=True)
    report_path = "docs/EVALUATION_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# LLM-as-a-Judge Evaluation & Stress Testing Report\n\n")
        f.write(f"- **Dagsetning:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Prófunarskrá:** `{STRESS_TESTS_FILE}` ({len(test_cases)} tilvik)\n\n")
        f.write("## Niðurstöður yfir Epochs\n\n")
        f.write("| Epoch | Table Match | Action / API Match | Zero Hallucinated Numbers | Meðaltími |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for h in history:
            f.write(f"| {h['epoch']} | {h['table_retrieval_pct']}% | {h['action_match_pct']}% | {h['hallucination_free_pct']}% | {h['avg_latency_sec']}s |\n")
        f.write("\n\n### Prófunartilvik og hegðun\n\n")
        for c in test_cases:
            f.write(f"- **Spurning:** {c.get('query')} | **Tafla:** `{c.get('expected_table')}` | **Action:** `{c.get('expected_action')}`\n")

    print(f"\n✅ Matsskýrsla vistuð í '{report_path}'.")
    return history


if __name__ == "__main__":
    run_evaluation_loop(num_epochs=2)
