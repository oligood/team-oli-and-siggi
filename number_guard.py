"""
number_guard.py - Deterministic check that every number in a generated answer
comes from the Hagstofa API response (or the question itself).

Used both at answer time (backend.generate_verified_answer) and in evaluation
(optimize_agents.py), so the production guard and the benchmark measure the same thing.
"""

import re


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


def find_unsupported_numbers(answer: str, api_res: dict, query: str = "") -> list:
    """Numbers in the answer that are not backed by the API data or the question."""
    return sorted(extract_answer_numbers(answer) - extract_allowed_numbers(api_res, query))
