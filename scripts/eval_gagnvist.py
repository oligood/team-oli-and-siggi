"""
eval_gagnvist.py - Runs the official Gagnvist example questions (questions/gagnvist_examples.jsonl,
from the organisers' gagnvist-starter repo) through our pipeline and scores them with the same
rules as `gagnvist evaluate`:

- an answer is right when it states every expected number, rounded to no fewer digits than it
  shows (35.45% and 35% are right for 35.454%, "about 140,000" is not right for 139,804), and
- every number comes from an accepted table.

Usage (from the repo root):
    python3 scripts/eval_gagnvist.py                # real LLM (Ollama), as in production
    python3 scripts/eval_gagnvist.py --no-llm       # template answers only, fast check of retrieval
    python3 scripts/eval_gagnvist.py --level hard --language is
"""

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backend  # noqa: E402

QUESTIONS_FILE = "questions/gagnvist_examples.jsonl"


def stated_numbers(text: str) -> list:
    """Numbers as written, with the number of decimals shown (Icelandic and English styles)."""
    text = re.sub(r"(\d+)\.\s*(?=[a-zA-ZáéíóúýþæöÁÉÍÓÚÝÞÆÖ])", r"\1 ", text)
    out = []
    for tok in re.findall(r"\d+(?:[.,\s]\d+)*", text):
        tok = tok.strip()
        if re.fullmatch(r"\d{1,3}(?:[.\s]\d{3})+(?:,\d+)?", tok):          # 139.804 / 139 804 / 4.941.210,92
            whole, _, dec = tok.replace(" ", ".").partition(",")
            out.append((float(whole.replace(".", "") + ("." + dec if dec else "")), len(dec)))
        elif re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", tok):          # 139,804 / 4,941,210.92
            whole, _, dec = tok.partition(".")
            out.append((float(whole.replace(",", "") + ("." + dec if dec else "")), len(dec)))
        elif re.fullmatch(r"\d+[.,]\d+", tok):                             # 35,45 / 35.45
            out.append((float(tok.replace(",", ".")), len(re.split(r"[.,]", tok)[1])))
        elif " " in tok:
            # A space-joined run that isn't one number ("árið 2025 4.941.211"): read each piece
            for part in tok.split():
                out.extend(stated_numbers(part))
        elif tok.isdigit():
            out.append((float(tok), 0))
    return out


def states(text: str, expected: float) -> bool:
    for value, decimals in stated_numbers(text):
        if round(expected, decimals) == round(value, decimals):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", default=QUESTIONS_FILE)
    ap.add_argument("--no-llm", action="store_true", help="skip the LLM and use the template answer")
    ap.add_argument("--level", action="append")
    ap.add_argument("--language")
    args = ap.parse_args()

    if args.no_llm:
        backend.generate_llm_answer = lambda **kw: kw["facts_summary"]

    rows = [json.loads(line) for line in open(args.file, encoding="utf-8") if line.strip()]
    rows = [r for r in rows if (not args.level or r["level"] in args.level)
            and (not args.language or r["language"] == args.language)]

    score = defaultdict(lambda: [0, 0])
    misses = []
    for r in rows:
        t0 = time.time()
        res = backend.answer_question(r["question"])
        answer = res.get("answer", "")
        tables = set(res.get("tables") or [res.get("table", "NONE")])
        numbers_ok = all(states(answer, a["value"]) for a in r["answers"])
        tables_ok = all(tables & set(p.get("accepted", [p["table"]])) for p in r["parts"])
        right = numbers_ok and tables_ok
        status = "right" if right else ("other table" if numbers_ok else "WRONG")
        for key in (r["level"], r["language"], f"{r['level']}-{r['language']}", "all"):
            score[key][0] += right
            score[key][1] += 1
        print(f"{status:11} {r['level']:6} {r['language']} {'+'.join(sorted(tables)):20} {time.time() - t0:5.1f}s  {r['question'][:70]}")
        if not right:
            misses.append((r, answer, tables))

    print("\nRight answers  English       Icelandic     Together")
    for level in ("easy", "medium", "hard", "all"):
        en, is_ = score[f"{level}-en"], score[f"{level}-is"]
        tot = score[level]
        if level == "all":
            en, is_ = score["en"], score["is"]
        print(f"  {level:12} {en[0]:2} of {en[1]:<7} {is_[0]:2} of {is_[1]:<7} {tot[0]:2} of {tot[1]}")

    if misses:
        print("\nNot right:")
        for r, answer, tables in misses:
            want = " and ".join(f"{a['value']:,}" for a in r["answers"])
            accepted = " + ".join("/".join(p.get("accepted", [p["table"]])[:3]) for p in r["parts"])
            print(f"  {r['id']} ({r['level']})\n    expected  {want} from {accepted}\n"
                  f"    tables    {', '.join(sorted(tables))}\n    answer    {answer[:220]}")


if __name__ == "__main__":
    main()
