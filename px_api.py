import re
import time
import unicodedata
import requests

from search import resolve_municipalities, is_part_of_larger_municipality

SVAEDA_MAPPING = {
    "hofudborgarsvaed": "1",
    "reykjavik": "1",
    "sudurnes": "2",
    "vesturland": "3",
    "vestfirdir": "4",
    "nordurland vestra": "5",
    "nordurland eystra": "6",
    "nordurland": "6",
    "austurland": "7",
    "sudurland": "8",
    "capital region": "1",
    "capital area": "1",
    "southern peninsula": "2",
    "west iceland": "3",
    "westfjords": "4",
    "northwest iceland": "5",
    "northeast iceland": "6",
    "east iceland": "7",
    "south iceland": "8",
}

MANUDIR_MAPPING = {
    "januar": "01", "january": "01", "jan": "01",
    "februar": "02", "february": "02", "feb": "02",
    "mars": "03", "march": "03", "mar": "03",
    "april": "04", "apr": "04",
    "mai": "05", "may": "05",
    "juni": "06", "june": "06", "jun": "06",
    "juli": "07", "july": "07", "jul": "07",
    "agust": "08", "august": "08", "aug": "08",
    "september": "09", "sep": "09",
    "oktober": "10", "october": "10", "okt": "10", "oct": "10",
    "november": "11", "nov": "11",
    "desember": "12", "december": "12", "des": "12", "dec": "12",
}

MONTH_NAMES_IS = {
    "01": "janúar", "02": "febrúar", "03": "mars", "04": "apríl",
    "05": "maí", "06": "júní", "07": "júlí", "08": "ágúst",
    "09": "september", "10": "október", "11": "nóvember", "12": "desember"
}

MONTH_NAMES_EN = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December"
}


MEN_PATTERN = r"\b(karl|men\b|male)"
WOMEN_PATTERN = r"\b(kon(a|u|ur|um)\b|women|female)"
# "What percentage / share of ..." needs the total next to the part
SHARE_PATTERN = r"\b(hlutfall|percentage of|share of|what percentage|hve stort hlutfall)"

# Tables answered from a declarative spec instead of a hand-written query builder.
# time: the time variable (None if the table has none); defaults: value per variable;
# match: question patterns that select other values; total: the value to add next to a
# matched one when the question asks for a share; score: variables picked by word overlap
# with the question (e.g. candidate names); what_is/what_en: what the figure measures.
TABLE_SPECS = {
    "MAN00101": {
        "time": "Ár", "defaults": {"Kyn": "Total", "Aldur": "-1"},
        "match": {"Kyn": [(MEN_PATTERN, "1"), (WOMEN_PATTERN, "2")]}, "total": {"Kyn": "Total"},
        "what_is": "Mannfjöldi 1. janúar", "what_en": "Population on 1 January",
    },
    "MAN05101": {
        "time": "Ár", "defaults": {"Eining": "0", "Aldur": "0"},
        "what_is": "Lifandi fædd börn", "what_en": "Live births",
    },
    "MAN43000": {
        "time": "Ár", "defaults": {"Aldur": "-1", "Bakgrunnur": "124", "Kyn": "0"},
        "match": {"Kyn": [(MEN_PATTERN, "1"), (WOMEN_PATTERN, "2")]}, "total": {"Kyn": "0"},
        "what_is": "Innflytjendur 1. janúar", "what_en": "Immigrants on 1 January",
    },
    "THJ01102": {
        "time": "Ár", "defaults": {"Skipting": "11"},
        "what_is": "Verg landsframleiðsla (milljónir króna)", "what_en": "Gross domestic product (ISK million)",
    },
    "SAM01601": {
        "time": "Ár", "defaults": {"Þjóðerni": "Total", "Landshluti": "IS", "Eining": "0", "Mánuður": "0"},
        "match": {"Þjóðerni": [(r"\b(utlend|foreign)", "Foreigners"), (r"\b(islending|icelander)", "IS")]},
        "total": {"Þjóðerni": "Total"},
        "what_is": "Gistinætur á skráðum gististöðum", "what_en": "Overnight stays in registered accommodation",
    },
    "KOS07112": {
        "time": None, "defaults": {"GIld atkvæði": "0", "Kjördæmi": "0"}, "score": ["Frambjóðendur", "Kjördæmi"],
        "what_is": "Gild atkvæði", "what_en": "Valid votes",
    },
    "VIN00920": {
        "time": "Ársfjórðungur", "time_kind": "quarter",
        "defaults": {"Landsvæði": "Alls", "Kyn": "Karlar og konur", "Aldur": "16-74 ára",
                     "Eining": "Atvinnuleysi, % (Hlutfall af vinnuafli)"},
        "match": {"Kyn": [(MEN_PATTERN, "Karlar"), (WOMEN_PATTERN, "Konur")]},
        "what_is": "Atvinnuleysi, % af vinnuafli", "what_en": "Unemployment rate, % of labour force",
    },
}

QUARTER_WORDS = {
    "1": r"\b(first|1st|fyrsta|fyrst)\b", "2": r"\b(second|2nd|odrum|annar|annan)\b",
    "3": r"\b(third|3rd|thridja|thridji)\b", "4": r"\b(fourth|4th|fjorda|fjordi|sidasta)\b",
}


def hreinsa_texta(texti: str) -> str:
    nfkd = unicodedata.normalize("NFKD", str(texti))
    flat = "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()
    for k, v in {"þ": "th", "æ": "ae", "ö": "o", "ð": "d"}.items():
        flat = flat.replace(k, v)
    return flat


def is_english_query(question: str) -> bool:
    q = re.findall(r"[a-z]+", hreinsa_texta(question))
    en_words = {"what", "how", "many", "population", "inflation", "who", "where", "is", "are", "in", "the", "rate", "people", "moved", "district", "wage", "unemployment"}
    matches = sum(1 for w in q if w in en_words)
    # Very short questions ("Inflation?") only have room for one English word
    return matches >= 2 or (len(q) <= 2 and matches >= 1)


def format_num(val, is_is: bool = True) -> str:
    try:
        f = float(val)
        if f.is_integer():
            n = int(f)
            return f"{n:,}".replace(",", ".") if is_is else f"{n:,}"
        formatted = f"{f:,.2f}"
        if is_is:
            return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return formatted
    except Exception:
        return str(val)


def _find_months(q_clean: str) -> list:
    """Month codes ("05") in the order they appear; whole words only, so "margir" isn't read as "mar"(s)."""
    found = []
    for m_key, code in MANUDIR_MAPPING.items():
        for m in re.finditer(r"\b" + re.escape(m_key) + r"\b", q_clean):
            found.append((m.start(), code))
    ordered = []
    for _, code in sorted(found):
        if code not in ordered:
            ordered.append(code)
    return ordered


def _shift_year(period: str, years: int) -> str:
    return f"{int(period[:4]) + years}M{period[5:]}"


def _requested_months(q_clean: str, years: list, v_vals: list) -> tuple[str, list]:
    """
    Which periods of a monthly table ("2024M05") the question asks for:
    ("months", [...]) for named months, ("years", [...]) for years without a month,
    or ("latest", [newest period]) when no period is mentioned.
    """
    months = _find_months(q_clean)
    if months:
        if years and len(months) == 1 and len(set(years)) > 1:
            # "from September 2025 to September 2026": the one month in each year
            targets = [f"{y}M{months[0]}" for y in dict.fromkeys(years)]
        elif years:
            targets = [f"{years[min(i, len(years) - 1)]}M{m}" for i, m in enumerate(months)]
        else:
            # "í maí" without a year: the most recent May that has been published
            last = v_vals[-1]
            y = int(last[:4])
            targets = [f"{y if f'{y}M{m}' <= last else y - 1}M{m}" for m in months]
        targets = [t for t in targets if t in v_vals]
        if targets:
            return "months", targets
    if years:
        valid = [y for y in dict.fromkeys(years) if any(v.startswith(f"{y}M") for v in v_vals)]
        if valid:
            return "years", valid
    return "latest", [v_vals[-1]]


def _sex_noun(sex_label: str, is_en: bool) -> str:
    label = hreinsa_texta(sex_label)
    if label.startswith("kon"):
        return "women" if is_en else "konur"
    if label.startswith("karl"):
        return "men" if is_en else "karlar"
    return "people" if is_en else "manns"


def _match_sex(q_clean: str, v_vals: list, v_texts: list) -> tuple[list, str]:
    total_val = v_vals[0] if v_vals else "0"
    for idx, vt in enumerate(v_texts):
        if any(w in hreinsa_texta(vt) for w in ["alls", "samtals", "total"]):
            total_val = v_vals[idx]
            break

    # Word-start matches: "women" must not also count as "men"
    has_men = bool(re.search(r"\b(karl|men\b|male)", q_clean))
    has_women = bool(re.search(r"\b(kon(a|u|ur|um)\b|women|female)", q_clean))

    if has_men and has_women:
        return ["1", "2"], "Karlar og konur"
    elif has_men:
        return ["1"], "Karlar"
    elif has_women:
        return ["2"], "Konur"
    return [total_val], "Alls"


def _format_month_label(m_code: str, is_is: bool = True) -> str:
    if "M" in m_code:
        y, m = m_code.split("M")
        m_name = MONTH_NAMES_IS.get(m, m) if is_is else MONTH_NAMES_EN.get(m, m)
        return f"{m_name} {y}"
    return m_code


def _is_total_label(label: str) -> bool:
    return hreinsa_texta(label).strip() in ("alls", "total", "allt landid", "samtals", "karlar og konur")


def derive_figures(entries: list, is_en: bool) -> tuple[str, dict]:
    """
    Calculations a question can ask for over two fetched figures: the change and % change
    between two periods, a part's share of a total, or the sum and difference of two parts.
    entries: [{"label": str, "period": str, "value": float}]. Returns (sentence, computed values).
    """
    if len(entries) != 2:
        return "", {}
    a, b = entries
    computed = {}
    if a["period"] != b["period"] and a["label"] == b["label"]:
        first, last = sorted(entries, key=lambda e: e["period"])
        change = round(last["value"] - first["value"], 2)
        pct = round(change / first["value"] * 100, 2) if first["value"] else 0.0
        computed.update(change=change, change_pct=pct)
        if is_en:
            return (f" Change from {first['period']} to {last['period']}: {format_num(change, False)} "
                    f"({format_num(pct, False)}%)."), computed
        return (f" Breyting frá {first['period']} til {last['period']}: {format_num(change, True)} "
                f"({format_num(pct, True)}%)."), computed
    if a["period"] == b["period"]:
        totals = [e for e in entries if _is_total_label(e["label"])]
        parts = [e for e in entries if not _is_total_label(e["label"])]
        if len(totals) == 1 and len(parts) == 1 and totals[0]["value"]:
            share = round(parts[0]["value"] / totals[0]["value"] * 100, 2)
            computed["share_pct"] = share
            if is_en:
                return f" Share of {parts[0]['label']} in the total: {format_num(share, False)}%.", computed
            return f" Hlutfall {parts[0]['label']} af heild: {format_num(share, True)}%.", computed
        total = round(a["value"] + b["value"], 2)
        diff = round(abs(a["value"] - b["value"]), 2)
        computed.update(sum=total, difference=diff)
        if is_en:
            return f" Together: {format_num(total, False)}. Difference: {format_num(diff, False)}.", computed
        return f" Samtals: {format_num(total, True)}. Munur: {format_num(diff, True)}.", computed
    return "", {}


def _best_scoring_value(q_clean: str, v_vals: list, v_texts: list, default: str) -> str:
    """The value whose text shares the most words with the question (candidate names, constituencies)."""
    q_tokens = set(re.findall(r"[a-z0-9]+", q_clean))
    best, best_score = default, 0
    for val, text in zip(v_vals, v_texts):
        tokens = [t for t in re.findall(r"[a-z0-9]+", hreinsa_texta(text)) if len(t) >= 4]
        score = sum(1 for t in tokens if t in q_tokens)
        if score > best_score:
            best, best_score = val, score
    return best


def _period_text(period: str, is_en: bool) -> str:
    if re.fullmatch(r"\d{4}Q\d", period):
        return f"Q{period[-1]} {period[:4]}" if is_en else f"{period[-1]}. ársfjórðungur {period[:4]}"
    if re.fullmatch(r"\d{4}M\d{2}", period):
        return _format_month_label(period, not is_en)
    return period


def format_facts_to_natural_language(table_code: str, title: str, question: str, rows: list, label_lookup: dict, var_codes: list, computed: dict) -> str:
    is_en = is_english_query(question)

    if table_code in TABLE_SPECS:
        spec = TABLE_SPECS[table_code]
        entries = computed.get("entries", [])
        what = spec["what_en"] if is_en else spec["what_is"]
        parts = []
        for e in entries:
            prefix = f"{e['label']}, " if e["label"] else ""
            parts.append(f"{prefix}{_period_text(e['period'], is_en)}: {format_num(e['value'], not is_en)}".strip(" :"))
        derived, extra = derive_figures(entries, is_en)
        computed.update(extra)
        if is_en:
            return f"According to Statistics Iceland (table {table_code}), {what}: " + "; ".join(parts) + "." + derived
        return f"Samkvæmt Hagstofu Íslands (tafla {table_code}), {what}: " + "; ".join(parts) + "." + derived

    if table_code == "VIS01002":
        periods = computed.get("periods", [])
        if len(periods) >= 2:
            first, last = periods[0], periods[-1]
            change = computed.get("inflation_change_pp", 0.0)
            idx_change = round(last["index"] - first["index"], 2)
            computed["index_change"] = idx_change
            f_txt = _format_month_label(first["month"], not is_en)
            l_txt = _format_month_label(last["month"], not is_en)
            if is_en:
                direction = "rose" if change > 0 else "fell" if change < 0 else "was unchanged"
                by = f" by {format_num(abs(change), False)} percentage points" if change else ""
                return (
                    f"According to Statistics Iceland (table {table_code}), 12-month inflation was "
                    f"{format_num(first['inflation'], False)}% in {f_txt} and {format_num(last['inflation'], False)}% in {l_txt}, "
                    f"so inflation {direction}{by} between the two months. The Consumer Price Index stood at "
                    f"{format_num(first['index'], False)} and {format_num(last['index'], False)} points respectively, "
                    f"a change of {format_num(idx_change, False)} points."
                )
            direction = "hækkaði" if change > 0 else "lækkaði" if change < 0 else "stóð í stað"
            by = f" um {format_num(abs(change), True)} prósentustig" if change else ""
            return (
                f"Samkvæmt vísitölu neysluverðs hjá Hagstofu Íslands (tafla {table_code}) mældist 12 mánaða verðbólga "
                f"{format_num(first['inflation'], True)}% í {f_txt} og {format_num(last['inflation'], True)}% í {l_txt}. "
                f"Verðbólgan {direction}{by} á milli mánaðanna. Vísitalan var {format_num(first['index'], True)} stig "
                f"í {f_txt} og {format_num(last['index'], True)} stig í {l_txt}, breyting um {format_num(idx_change, True)} stig."
            )

        m_curr = computed.get("m_curr", "")
        m_prev = computed.get("m_prev", "")
        v_curr = computed.get("v_curr", 0.0)
        v_prev = computed.get("v_prev", 0.0)
        infl = computed.get("infl", 0.0)
        m_curr_txt = _format_month_label(m_curr, not is_en)
        m_prev_txt = _format_month_label(m_prev, not is_en)

        if is_en:
            return (
                f"According to Statistics Iceland (table {table_code}), the Consumer Price Index in {m_curr_txt} "
                f"was {format_num(v_curr, False)} points (compared to {format_num(v_prev, False)} points in {m_prev_txt}). "
                f"The 12-month inflation rate was {format_num(infl, False)}%."
            )
        return (
            f"Samkvæmt vísitölu neysluverðs hjá Hagstofu Íslands (tafla {table_code}) var vísitalan "
            f"{format_num(v_curr, True)} stig í {m_curr_txt} (samanborið við {format_num(v_prev, True)} stig í {m_prev_txt}). "
            f"12 mánaða verðbólga mældist {format_num(infl, True)}%."
        )

    elif table_code == "MAN00000":
        val = rows[-1]["values"][0] if rows and rows[-1].get("values") else "N/A"
        year = rows[-1]["key"][0] if rows and rows[-1].get("key") else "2026"
        if is_en:
            return (
                f"According to Statistics Iceland key population figures (table {table_code}), "
                f"the population of Iceland was {format_num(val, False)} on January 1, {year}."
            )
        return (
            f"Samkvæmt lykiltölum Hagstofu Íslands (tafla {table_code}) voru {format_num(val, True)} "
            f"íbúar á Íslandi þann 1. janúar {year}."
        )

    elif table_code == "MAN02005":
        entries = []
        for r in rows:
            k = dict(zip(var_codes, r.get("key", [])))
            entries.append({
                "name": label_lookup.get("Sveitarfélag", {}).get(k.get("Sveitarfélag", ""), "sveitarfélaginu"),
                "noun": _sex_noun(label_lookup.get("Kyn", {}).get(k.get("Kyn", ""), ""), is_en),
                "value": r["values"][0] if r.get("values") else "N/A",
                "year": k.get("Ár", "2026"),
            })
        if len(entries) > 1:
            def shown(e):
                if e["name"] == "Alls":
                    return "Iceland (total)" if is_en else "Allt landið"
                return e["name"]
            if is_en:
                parts = "; ".join(f"{shown(e)} ({e['year']}): {format_num(e['value'], False)} {e['noun']}" for e in entries)
                text = f"According to Statistics Iceland (table {table_code}), population on January 1: {parts}."
            else:
                parts = "; ".join(f"{shown(e)} ({e['year']}): {format_num(e['value'], True)} {e['noun']}" for e in entries)
                text = f"Samkvæmt mannfjöldatölum Hagstofu Íslands (tafla {table_code}), mannfjöldi 1. janúar: {parts}."
            try:
                derived, extra = derive_figures(
                    [{"label": e["name"], "period": e["year"], "value": float(e["value"])} for e in entries], is_en)
                computed.update(extra)
                text += derived
            except ValueError:
                pass
            if (len(entries) == 2 and "difference" in computed and entries[0]["noun"] == entries[1]["noun"]
                    and entries[0]["year"] == entries[1]["year"] and "Alls" not in (entries[0]["name"], entries[1]["name"])):
                bigger = max(entries, key=lambda e: float(e["value"]))["name"]
                diff = computed["difference"]
                text += (f" {bigger} has {format_num(diff, False)} more." if is_en
                         else f" Fleiri búa í {bigger}; munurinn er {format_num(diff, True)}.")
            return text

        val = entries[0]["value"] if entries else "N/A"
        muni_name = entries[0]["name"] if entries else "sveitarfélaginu"
        noun = entries[0]["noun"] if entries else ("people" if is_en else "manns")
        year = entries[0]["year"] if entries else "2026"
        # Asked about a town inside a merged municipality: say plainly there is no separate figure,
        # so the model has no gap to fill with a number of its own
        part_of = is_part_of_larger_municipality(hreinsa_texta(question))
        if is_en:
            note = (
                f" The place asked about is part of the municipality of {muni_name}; Statistics Iceland does not "
                f"publish a separate population figure for it in this table, only for {muni_name} as a whole."
            ) if part_of else ""
            return (
                f"According to Statistics Iceland (table {table_code}), {format_num(val, False)} {noun} lived in "
                f"{muni_name} as of January 1, {year}.{note}"
            )
        note = (
            f" Staðurinn sem spurt er um tilheyrir sveitarfélaginu {muni_name}. Hagstofan birtir ekki sérstaka "
            f"mannfjöldatölu fyrir hann í þessari töflu, aðeins fyrir sveitarfélagið í heild."
        ) if part_of else ""
        return (
            f"Samkvæmt mannfjöldatölum Hagstofu Íslands (tafla {table_code}) bjuggu {format_num(val, True)} "
            f"{noun} í {muni_name} þann 1. janúar {year}.{note}"
        )

    elif table_code == "MAN03270":
        val = rows[0]["values"][0] if rows and rows[0].get("values") else "N/A"
        keys = rows[0].get("key", [])
        dist_code = keys[0] if keys else ""
        dist_name = label_lookup.get("Hverfi", {}).get(dist_code, "hverfinu")
        year = keys[2] if len(keys) > 2 else "2026"
        noun = _sex_noun(label_lookup.get("Kyn", {}).get(dict(zip(var_codes, keys)).get("Kyn", ""), ""), is_en)
        if is_en:
            return (
                f"According to Statistics Iceland (table {table_code}), {format_num(val, False)} {noun} lived in "
                f"{dist_name} in Reykjavík on January 1, {year}."
            )
        return (
            f"Samkvæmt mannfjöldagögnum Hagstofu Íslands (tafla {table_code}) bjuggu {format_num(val, True)} "
            f"{noun} í hverfinu {dist_name} í Reykjavík þann 1. janúar {year}."
        )

    elif table_code == "MAN01002":
        total = computed.get("total_migration", 0)
        year = rows[0]["key"][1] if rows and len(rows[0].get("key", [])) > 1 else "2024"

        # Name the origin/destination regions and give the per-region breakdown, so the
        # answer states exactly what was summed instead of "between the selected regions"
        origins, dests, parts = [], [], []
        for r in rows:
            labels = [label_lookup.get(var_codes[i], {}).get(k, k) for i, k in enumerate(r.get("key", [])) if i < len(var_codes)]
            origin = next((l.rsplit(" - ", 1)[0] for l in labels if l.endswith("brottfluttir")), "")
            dest = next((l.rsplit(" - ", 1)[0] for l in labels if l.endswith("aðfluttir")), "")
            origins.append(origin)
            dests.append(dest)
            if r.get("values"):
                parts.append((origin, dest, r["values"][0]))
        single_dest = dests[0] if dests and len(set(dests)) == 1 else ""
        single_origin = origins[0] if origins and len(set(origins)) == 1 else ""

        if is_en:
            if single_dest and not single_origin:
                head = f"{format_num(total, False)} people moved to {single_dest} from other regions of Iceland in {year}"
                breakdown = "; ".join(f"{o}: {format_num(v, False)}" for o, _, v in parts)
            elif single_origin and not single_dest:
                head = f"{format_num(total, False)} people moved from {single_origin} to other regions of Iceland in {year}"
                breakdown = "; ".join(f"{d}: {format_num(v, False)}" for _, d, v in parts)
            else:
                head = f"{format_num(total, False)} people moved from {single_origin or 'the selected regions'} to {single_dest or 'the selected regions'} in {year}"
                breakdown = ""
            tail = f" Breakdown: {breakdown}." if breakdown and len(parts) > 1 else ""
            return f"According to Statistics Iceland regional migration records (table {table_code}), {head}.{tail}"

        if single_dest and not single_origin:
            head = f"fluttu {format_num(total, True)} manns til svæðisins {single_dest} frá öðrum landshlutum árið {year}"
            breakdown = "; ".join(f"frá {o}: {format_num(v, True)}" for o, _, v in parts)
        elif single_origin and not single_dest:
            head = f"fluttu {format_num(total, True)} manns frá svæðinu {single_origin} til annarra landshluta árið {year}"
            breakdown = "; ".join(f"til {d}: {format_num(v, True)}" for _, d, v in parts)
        else:
            head = f"fluttu {format_num(total, True)} manns frá {single_origin or 'tilgreindum svæðum'} til {single_dest or 'tilgreindra svæða'} árið {year}"
            breakdown = ""
        tail = f" Sundurliðun: {breakdown}." if breakdown and len(parts) > 1 else ""
        return f"Samkvæmt búferlaflutningatölum Hagstofu Íslands (tafla {table_code}) {head}.{tail}"

    elif table_code == "LAU04000":
        periods = computed.get("periods", [])
        if len(periods) >= 2:
            first, last, change = periods[0], periods[-1], computed["index_change"]
            f_txt = _format_month_label(first["month"], not is_en)
            l_txt = _format_month_label(last["month"], not is_en)
            if is_en:
                return (f"According to Statistics Iceland wage statistics (table {table_code}), the Wage Index was "
                        f"{format_num(first['index'], False)} points in {f_txt} and {format_num(last['index'], False)} points "
                        f"in {l_txt}, a change of {format_num(change, False)} points.")
            return (f"Samkvæmt launavísitölu Hagstofu Íslands (tafla {table_code}) var launavísitalan "
                    f"{format_num(first['index'], True)} stig í {f_txt} og {format_num(last['index'], True)} stig í {l_txt}, "
                    f"breyting um {format_num(change, True)} stig.")
        idx_val = computed.get("wage_index", "N/A")
        change_a = computed.get("wage_growth", "N/A")
        m_code = computed.get("m_curr", "")
        m_txt = _format_month_label(m_code, not is_en)
        if is_en:
            return (
                f"According to Statistics Iceland wage statistics (table {table_code}), the Wage Index in {m_txt} "
                f"stood at {format_num(idx_val, False)} points, representing a 12-month wage growth of {format_num(change_a, False)}%."
            )
        return (
            f"Samkvæmt launavísitölu Hagstofu Íslands (tafla {table_code}) stóð launavísitalan í "
            f"{format_num(idx_val, True)} stigum í {m_txt}. 12 mánaða hækkun launa mældist {format_num(change_a, True)}%."
        )

    elif table_code == "VIN00001":
        years_out = computed.get("years", [])
        months_out = computed.get("months", [])
        if years_out or len(months_out) >= 2:
            if years_out:
                labels = [y["year"] for y in years_out]
                if is_en:
                    parts = [f"{format_num(y['avg_rate'], False)}% in {y['year']} (on average {format_num(y['avg_count'], False)} "
                             f"unemployed, mean of {y['months']} months)" for y in years_out]
                else:
                    parts = [f"{format_num(y['avg_rate'], True)}% árið {y['year']} (að meðaltali {format_num(y['avg_count'], True)} "
                             f"manns án atvinnu, meðaltal {y['months']} mánaða)" for y in years_out]
            else:
                labels = [_format_month_label(m["month"], not is_en) for m in months_out]
                parts = [f"{format_num(m['rate'], not is_en)}% {'in' if is_en else 'í'} {lbl} "
                         f"({format_num(m['count'], not is_en)} {'unemployed' if is_en else 'manns án atvinnu'})"
                         for m, lbl in zip(months_out, labels)]
            if is_en:
                text = f"According to the Statistics Iceland Labour Force Survey (table {table_code}), unemployment was " + "; ".join(parts) + "."
            else:
                text = f"Samkvæmt vinnumarkaðsrannsókn Hagstofu Íslands (tafla {table_code}) var atvinnuleysi " + "; ".join(parts) + "."
            if "count_change" in computed:
                cc, rc = computed["count_change"], computed["rate_change_pp"]
                if is_en:
                    direction = "rose" if cc > 0 else "fell" if cc < 0 else "was unchanged"
                    text += (f" The number of unemployed {direction}" + (f" by {format_num(abs(cc), False)}" if cc else "")
                             + f" between {labels[0]} and {labels[-1]}, a change of {format_num(abs(rc), False)} percentage points in the rate.")
                else:
                    direction = "fjölgaði" if cc > 0 else "fækkaði" if cc < 0 else "stóð fjöldinn í stað"
                    text += (f" Atvinnulausum {direction}" + (f" um {format_num(abs(cc), True)}" if cc else "")
                             + f" á milli {labels[0]} og {labels[-1]}, og atvinnuleysishlutfallið breyttist um "
                             f"{format_num(abs(rc), True)} prósentustig.")
            return text

        rate = computed.get("unemployment_rate", "N/A")
        count = computed.get("unemployed_count", "N/A")
        m_code = computed.get("m_curr", "")
        m_txt = _format_month_label(m_code, not is_en)
        if is_en:
            return (
                f"According to the Statistics Iceland Labour Force Survey (table {table_code}), the unemployment rate in {m_txt} "
                f"was {format_num(rate, False)}% (approx. {format_num(count, False)} people)."
            )
        return (
            f"Samkvæmt vinnumarkaðsrannsókn Hagstofu Íslands (tafla {table_code}) mældist atvinnuleysi í {m_txt} "
            f"{format_num(rate, True)}% ({format_num(count, True)} manns voru án atvinnu)."
        )

    elif table_code == "SAM02001":
        count = computed.get("passenger_count", "N/A")
        cat_name = computed.get("category_name", "farþegar")
        m_code = computed.get("m_curr", "")
        m_txt = _format_month_label(m_code, not is_en)
        if "M" not in m_code:
            # Whole-year total
            m_txt = f"{m_code} as a whole" if is_en else f"árinu {m_code} í heild"
        if is_en:
            return (
                f"According to Statistics Iceland (table {table_code}), a total of {format_num(count, False)} passengers "
                f"({cat_name}) passed through Keflavík Airport in {m_txt}."
            )
        return (
            f"Samkvæmt tölum Hagstofu Íslands um farþega (tafla {table_code}) fóru alls {format_num(count, True)} "
            f"farþegar ({cat_name}) um Keflavíkurflugvöll í {m_txt}."
        )

    # Generic fallback
    if is_en:
        return f"According to Statistics Iceland table {table_code} ({title}): {computed.get('raw_summary', '')}"
    return f"Samkvæmt töflu {table_code} ({title}) hjá Hagstofu Íslands: {computed.get('raw_summary', '')}"


def _request_with_retry(method: str, url: str, retries: int = 2, **kwargs) -> requests.Response:
    """PX-API occasionally returns 429/5xx or drops the connection; retry those with a short backoff."""
    for attempt in range(retries + 1):
        try:
            res = requests.request(method, url, **kwargs)
            if res.status_code not in (429, 500, 502, 503, 504) or attempt == retries:
                return res
        except requests.RequestException:
            if attempt == retries:
                raise
        time.sleep(1.5 * (attempt + 1))


def fetch_table_data(table_url: str, question: str) -> dict:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    try:
        meta_res = _request_with_retry("GET", table_url, headers=headers, timeout=15)
        if meta_res.status_code != 200:
            return {"ok": False, "error": f"Failed to fetch metadata (status {meta_res.status_code})."}
        metadata = meta_res.json()
    except Exception as e:
        return {"ok": False, "error": f"Connection error: {e}"}

    title = metadata.get("title", "Hagstofa Íslands")
    variables = metadata.get("variables", [])
    q_clean = hreinsa_texta(question)
    years = re.findall(r"\b(20\d{2}|19\d{2})\b", q_clean)

    table_code = table_url.split("/")[-1].replace(".px", "")
    query_list = []
    computed = {}

    if table_code == "VIS01002":
        for var in variables:
            v_code = var.get("code")
            v_text = hreinsa_texta(var.get("text", ""))
            v_vals = var.get("values", [])

            if "manudur" in v_text or "month" in v_text or v_code == "Mánuður":
                kind, targets = _requested_months(q_clean, years, v_vals)
                if kind == "years":
                    # A year without a month: December (or the latest month published that year)
                    targets = [max(v for v in v_vals if v.startswith(f"{y}M")) for y in targets]
                computed["periods"] = targets
                # Each period plus the same month a year earlier, for 12-month inflation
                selected = sorted({p for t in targets for p in (_shift_year(t, -1), t) if p in v_vals})
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": selected}})
            elif "grunnur" in v_text:
                g_val = v_vals[0] if v_vals else "B1988"
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [g_val]}})
            elif "visitala" in v_text:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[0]]}})
            else:
                if v_vals:
                    query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[-1]]}})

    elif table_code == "LAU04000":
        for var in variables:
            v_code = var.get("code")
            v_text = hreinsa_texta(var.get("text", ""))
            v_vals = var.get("values", [])
            if "manudur" in v_text or v_code == "Mánuður":
                kind, targets = _requested_months(q_clean, years, v_vals)
                if kind == "years":
                    targets = [max(v for v in v_vals if v.startswith(f"{y}M")) for y in targets]
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": targets}})
            elif "eining" in v_text or v_code == "Eining":
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": ["index", "change_A"]}})
            else:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[-1]]}})

    elif table_code == "VIN00001":
        for var in variables:
            v_code = var.get("code")
            v_text = hreinsa_texta(var.get("text", ""))
            v_vals = var.get("values", [])
            if "manudur" in v_text or v_code == "Mánuður":
                kind, targets = _requested_months(q_clean, years, v_vals)
                if kind == "years":
                    # Whole years: all published months, averaged below
                    targets = [v for v in v_vals if v[:4] in targets]
                computed["period_kind"] = kind
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": targets}})
            elif "kyn" in v_text or "aldur" in v_text:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": ["0"]}})
            elif "eining" in v_text or v_code == "Eining":
                # 7 = Atvinnuleysi %, 3 = Atvinnulausir fjöldi
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": ["7", "3"]}})
            else:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[0]]}})

    elif table_code == "SAM02001":
        # Farþegar um Keflavíkurflugvöll
        cat_val = "0"  # Farþegar alls
        if any(w in q_clean for w in ["utlend", "foreign", "ferdamann", "ferdamenn", "erlend", "tourist"]):
            cat_val = "2"  # Útlendingar alls
        elif any(w in q_clean for w in ["islend", "iceland"]):
            cat_val = "1"  # Ísland
        elif any(w in q_clean for w in ["bandarik", "usa", "american"]):
            cat_val = "5"  # Bandaríkin

        for var in variables:
            v_code = var.get("code")
            v_text = hreinsa_texta(var.get("text", ""))
            v_vals = var.get("values", [])
            if "rikisfang" in v_text or v_code == "Ríkisfang":
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [cat_val]}})
            elif "manudur" in v_text or v_code == "Mánuður":
                kind, targets = _requested_months(q_clean, years, v_vals)
                if kind == "years":
                    # A whole year: all its months, summed below
                    targets = [v for v in v_vals if v[:4] == targets[-1]]
                else:
                    targets = [targets[-1]]
                computed["period_kind"] = kind
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": targets}})
            else:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[-1]]}})

    elif table_code == "MAN01002":
        found_regions = sorted([
            (q_clean.find(s), code)
            for s, code in SVAEDA_MAPPING.items()
            if q_clean.find(s) != -1
        ])
        regions = []
        for _, code in found_regions:
            if not regions or regions[-1] != code:
                regions.append(code)

        all_domestic = ["1", "2", "3", "4", "5", "6", "7", "8"]
        if len(regions) >= 2:
            brott_vals = [regions[0]]
            ad_vals = [regions[1]]
        elif len(regions) == 1:
            r_code = regions[0]
            others = [c for c in all_domestic if c != r_code]
            if "fra " in q_clean or "from " in q_clean:
                brott_vals = [r_code]
                ad_vals = others
            else:
                brott_vals = others
                ad_vals = [r_code]
        else:
            brott_vals = ["6"]
            ad_vals = ["1"]

        for var in variables:
            v_code = var.get("code")
            v_text = hreinsa_texta(var.get("text", ""))
            v_vals = var.get("values", [])
            v_texts = var.get("valueTexts", [])

            if "kyn" in v_text:
                sex_vals, _ = _match_sex(q_clean, v_vals, v_texts)
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": sex_vals}})
            elif "aldur" in v_text:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[0]]}})
            elif "ar" in v_text:
                y = [years[0]] if (years and years[0] in v_vals) else [v_vals[-1]]
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": y}})
            elif "brott" in v_text:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": brott_vals}})
            elif "adflutning" in v_text:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": ad_vals}})
            else:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[0]]}})

    elif table_code in ("MAN02005", "MAN03270"):
        for var in variables:
            v_code = var.get("code")
            v_text = hreinsa_texta(var.get("text", ""))
            v_vals = var.get("values", [])
            v_texts = var.get("valueTexts", [])

            if "sveitarfelag" in v_text or "hverfi" in v_text:
                matched_val = v_vals[0]
                # Named places, incl. old/merged names (Seyðisfjörður -> Múlaþing) that stem matching can't
                # find; several for comparisons ("Kópavogur eða Hafnarfjörður")
                aliases = resolve_municipalities(q_clean) if "sveitarfelag" in v_text else []
                matched_vals = [v_vals[v_texts.index(n)] for n in aliases if n in v_texts]
                if not matched_vals:
                    for idx, vt in enumerate(v_texts):
                        vt_clean = hreinsa_texta(vt)
                        vt_words = [w for w in vt_clean.split() if not w.isdigit() and len(w) >= 4]
                        for w in vt_words:
                            stem = w[:6] if len(w) >= 6 else w
                            if stem in q_clean:
                                matched_val = v_vals[idx]
                                break
                        if matched_val != v_vals[0]:
                            break
                    matched_vals = [matched_val]
                # "What percentage of Iceland's population lived in Reykjavík?" also needs the national total
                if ("sveitarfelag" in v_text and re.search(SHARE_PATTERN, q_clean)
                        and re.search(r"\b(island|iceland|landsm)", q_clean) and v_vals[0] not in matched_vals):
                    matched_vals.append(v_vals[0])
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": matched_vals}})
            elif "aldur" in v_text:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[0]]}})
            elif "ar" in v_text:
                # Every year asked about ("from 1 January 2025 to 1 January 2026"), else the latest
                y = [yr for yr in dict.fromkeys(years) if yr in v_vals] or [v_vals[-1]]
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": y}})
            elif "kyn" in v_text:
                sex_vals, _ = _match_sex(q_clean, v_vals, v_texts)
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": sex_vals}})
            else:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[0]]}})

    elif table_code in TABLE_SPECS:
        spec = TABLE_SPECS[table_code]
        asks_share = bool(re.search(SHARE_PATTERN, q_clean))
        for var in variables:
            v_code = var.get("code")
            v_vals = var.get("values", [])
            v_texts = var.get("valueTexts", [])
            if v_code == spec["time"]:
                if spec.get("time_kind") == "quarter":
                    sel = [f"{y}Q{n}" for y in dict.fromkeys(years) for n, pat in QUARTER_WORDS.items()
                           if re.search(pat, q_clean) and f"{y}Q{n}" in v_vals]
                else:
                    sel = [y for y in dict.fromkeys(years) if y in v_vals]
                sel = sel or [v_vals[-1]]
            elif v_code in spec.get("score", []):
                sel = [_best_scoring_value(q_clean, v_vals, v_texts, spec["defaults"].get(v_code, v_vals[0]))]
            else:
                sel = [val for pat, val in spec.get("match", {}).get(v_code, []) if re.search(pat, q_clean)]
                if sel and asks_share and v_code in spec.get("total", {}):
                    sel.append(spec["total"][v_code])
                sel = sel or [spec["defaults"].get(v_code, v_vals[0])]
            query_list.append({"code": v_code, "selection": {"filter": "item", "values": sel}})

    else:
        # MAN00000 and generic tables
        for var in variables:
            v_code = var.get("code")
            v_text = hreinsa_texta(var.get("text", ""))
            v_vals = var.get("values", [])
            if "ar" in v_text:
                y = [years[0]] if (years and years[0] in v_vals) else [v_vals[-1]]
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": y}})
            else:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[0]]}})

    try:
        data_res = _request_with_retry(
            "POST",
            table_url,
            json={"query": query_list, "response": {"format": "json"}},
            headers=headers,
            timeout=15,
        )
        if data_res.status_code != 200:
            return {"ok": False, "error": f"PX-API query failed (status {data_res.status_code})."}
        api_data = data_res.json()
    except Exception as e:
        return {"ok": False, "error": f"Data fetch error: {e}"}

    rows = api_data.get("data", [])
    if not rows:
        return {"ok": False, "error": "Engin gögn fundust fyrir valdar breytur."}

    # Map variable codes to valueTexts for readable output
    label_lookup = {}
    for var in variables:
        mapping = dict(zip(var.get("values", []), var.get("valueTexts", [])))
        label_lookup[var.get("code")] = mapping

    var_codes = [col.get("code") for col in api_data.get("columns", []) if col.get("type") != "c"]

    readable_rows = []
    structured_chart_data = []

    for r in rows:
        keys = r.get("key", [])
        vals = r.get("values", [])
        labels = []
        for idx, k in enumerate(keys):
            v_code = var_codes[idx] if idx < len(var_codes) else ""
            lbl = label_lookup.get(v_code, {}).get(k, k)
            labels.append(f"{v_code}: {lbl}")
        val_str = vals[0] if vals else "N/A"
        readable_rows.append(f"{', '.join(labels)} = {val_str}")
        try:
            val_flt = float(val_str)
            label_disp = " - ".join(label_lookup.get(var_codes[idx], {}).get(k, k) for idx, k in enumerate(keys))
            structured_chart_data.append({"Liður": label_disp, "Gildi": val_flt})
        except Exception:
            pass

    computed["raw_summary"] = "; ".join(readable_rows)

    if table_code == "VIS01002":
        try:
            by_month = {r["key"][0]: float(r["values"][0]) for r in rows if r.get("values")}
            periods = []
            for t in computed.get("periods", []):
                prev = _shift_year(t, -1)
                if t in by_month and prev in by_month:
                    periods.append({
                        "month": t,
                        "index": by_month[t],
                        "index_prev_year": by_month[prev],
                        "inflation": round((by_month[t] - by_month[prev]) / by_month[prev] * 100, 2),
                    })
            computed["periods"] = periods
            if periods:
                last = periods[-1]
                computed["v_prev"] = last["index_prev_year"]
                computed["v_curr"] = last["index"]
                computed["m_prev"] = _shift_year(last["month"], -1)
                computed["m_curr"] = last["month"]
                computed["infl"] = last["inflation"]
            if len(periods) >= 2:
                computed["inflation_change_pp"] = round(periods[-1]["inflation"] - periods[0]["inflation"], 2)
        except Exception:
            pass

    elif table_code in TABLE_SPECS:
        spec = TABLE_SPECS[table_code]
        varying = {q["code"] for q in query_list if len(q["selection"]["values"]) > 1} - {spec["time"]}
        entries = []
        for r in rows:
            k = dict(zip(var_codes, r.get("key", [])))
            try:
                value = float(r["values"][0])
            except (ValueError, IndexError, KeyError):
                continue
            label = ", ".join(label_lookup.get(c, {}).get(k[c], k[c]) for c in var_codes if c in varying)
            entries.append({"label": label, "period": k.get(spec["time"], "") if spec["time"] else "", "value": value})
        computed["entries"] = entries

    elif table_code == "MAN02005" and len(rows) == 2:
        try:
            computed["difference"] = abs(int(rows[0]["values"][0]) - int(rows[1]["values"][0]))
        except Exception:
            pass

    elif table_code == "MAN01002":
        try:
            total = sum(int(r["values"][0]) for r in rows if r.get("values"))
            computed["total_migration"] = total
        except Exception:
            pass

    elif table_code == "LAU04000":
        try:
            index_by_month = {}
            for r in sorted(rows, key=lambda r: r.get("key", [""])[0]):
                if len(r.get("key", [])) > 1:
                    e_code = r["key"][1]
                    if e_code == "index":
                        computed["wage_index"] = float(r["values"][0])
                        index_by_month[r["key"][0]] = float(r["values"][0])
                    elif e_code == "change_A":
                        computed["wage_growth"] = float(r["values"][0])
                    computed["m_curr"] = r["key"][0]
            if len(index_by_month) >= 2:
                computed["periods"] = [{"month": m, "index": v} for m, v in sorted(index_by_month.items())]
                computed["index_change"] = round(computed["periods"][-1]["index"] - computed["periods"][0]["index"], 2)
        except Exception:
            pass

    elif table_code == "VIN00001":
        by_month = {}
        for r in rows:
            keys = r.get("key", [])
            if len(keys) > 2 and r.get("values"):
                try:
                    entry = by_month.setdefault(keys[0], {})
                    if keys[2] == "7":
                        entry["rate"] = float(r["values"][0])
                    elif keys[2] == "3":
                        entry["count"] = int(r["values"][0])
                except ValueError:
                    pass
        months = sorted(m for m, e in by_month.items() if "rate" in e and "count" in e)
        if months:
            computed["unemployment_rate"] = by_month[months[-1]]["rate"]
            computed["unemployed_count"] = by_month[months[-1]]["count"]
            computed["m_curr"] = months[-1]
        if computed.get("period_kind") == "years":
            years_out = []
            for y in sorted({m[:4] for m in months}):
                ms = [by_month[m] for m in months if m.startswith(y)]
                years_out.append({
                    "year": y,
                    "months": len(ms),
                    "avg_rate": round(sum(e["rate"] for e in ms) / len(ms), 2),
                    "avg_count": round(sum(e["count"] for e in ms) / len(ms)),
                })
            computed["years"] = years_out
            if len(years_out) >= 2:
                computed["count_change"] = years_out[-1]["avg_count"] - years_out[0]["avg_count"]
                computed["rate_change_pp"] = round(years_out[-1]["avg_rate"] - years_out[0]["avg_rate"], 2)
        elif len(months) >= 2:
            computed["months"] = [{"month": m, **by_month[m]} for m in months]
            computed["count_change"] = by_month[months[-1]]["count"] - by_month[months[0]]["count"]
            computed["rate_change_pp"] = round(by_month[months[-1]]["rate"] - by_month[months[0]]["rate"], 2)

    elif table_code == "SAM02001":
        try:
            if rows:
                computed["passenger_count"] = sum(int(r["values"][0]) for r in rows if r.get("values"))
                cat_code = rows[0]["key"][0]
                computed["category_name"] = label_lookup.get("Ríkisfang", {}).get(cat_code, "farþegar")
                # A whole year is reported as the year itself ("2024"), a single month as "2024M07"
                computed["m_curr"] = rows[0]["key"][1][:4] if len(rows) > 1 else rows[0]["key"][1]
                computed["months_summed"] = len(rows)
        except Exception:
            pass

    natural_summary = format_facts_to_natural_language(
        table_code=table_code,
        title=title,
        question=question,
        rows=rows,
        label_lookup=label_lookup,
        var_codes=var_codes,
        computed=computed,
    )

    return {
        "ok": True,
        "table_id": table_code,
        "title": title,
        "source_url": table_url,
        "query_used": query_list,
        "facts": readable_rows,
        "summary": natural_summary,
        "structured_data": structured_chart_data,
        "computed": computed,
    }
