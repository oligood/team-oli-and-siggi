import re
import unicodedata
import requests

from search import resolve_municipality

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


def hreinsa_texta(texti: str) -> str:
    nfkd = unicodedata.normalize("NFKD", str(texti))
    flat = "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()
    for k, v in {"þ": "th", "æ": "ae", "ö": "o", "ð": "d"}.items():
        flat = flat.replace(k, v)
    return flat


def is_english_query(question: str) -> bool:
    q = hreinsa_texta(question).split()
    en_words = {"what", "how", "many", "population", "inflation", "who", "where", "is", "are", "in", "the", "rate", "people", "moved", "district", "wage", "unemployment"}
    matches = sum(1 for w in q if w in en_words)
    return matches >= 2


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


def _match_sex(q_clean: str, v_vals: list, v_texts: list) -> tuple[list, str]:
    total_val = v_vals[0] if v_vals else "0"
    for idx, vt in enumerate(v_texts):
        if any(w in hreinsa_texta(vt) for w in ["alls", "samtals", "total"]):
            total_val = v_vals[idx]
            break

    has_men = any(w in q_clean for w in ["karl", "men", "male"])
    has_women = any(w in q_clean for w in ["konu", "konur", "kona", "women", "female"])

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


def format_facts_to_natural_language(table_code: str, title: str, question: str, rows: list, label_lookup: dict, var_codes: list, computed: dict) -> str:
    is_en = is_english_query(question)

    if table_code == "VIS01002":
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
        val = rows[0]["values"][0] if rows and rows[0].get("values") else "N/A"
        keys = rows[0].get("key", [])
        muni_code = keys[0] if keys else ""
        muni_name = label_lookup.get("Sveitarfélag", {}).get(muni_code, "sveitarfélaginu")
        year = keys[2] if len(keys) > 2 else "2026"
        if is_en:
            return (
                f"According to Statistics Iceland (table {table_code}), the population of {muni_name} "
                f"was {format_num(val, False)} as of January 1, {year}."
            )
        return (
            f"Samkvæmt mannfjöldatölum Hagstofu Íslands (tafla {table_code}) bjuggu {format_num(val, True)} "
            f"manns í {muni_name} þann 1. janúar {year}."
        )

    elif table_code == "MAN03270":
        val = rows[0]["values"][0] if rows and rows[0].get("values") else "N/A"
        keys = rows[0].get("key", [])
        dist_code = keys[0] if keys else ""
        dist_name = label_lookup.get("Hverfi", {}).get(dist_code, "hverfinu")
        year = keys[2] if len(keys) > 2 else "2026"
        if is_en:
            return (
                f"According to Statistics Iceland (table {table_code}), {format_num(val, False)} people lived in "
                f"{dist_name} in Reykjavík on January 1, {year}."
            )
        return (
            f"Samkvæmt mannfjöldagögnum Hagstofu Íslands (tafla {table_code}) bjuggu {format_num(val, True)} "
            f"manns í hverfinu {dist_name} í Reykjavík þann 1. janúar {year}."
        )

    elif table_code == "MAN01002":
        total = computed.get("total_migration", 0)
        year = rows[0]["key"][1] if rows and len(rows[0].get("key", [])) > 1 else "2024"
        if is_en:
            return (
                f"According to Statistics Iceland regional migration records (table {table_code}), "
                f"a total of {format_num(total, False)} people moved between the selected regions in {year}."
            )
        return (
            f"Samkvæmt búferlaflutningatölum Hagstofu Íslands (tafla {table_code}) fluttu alls "
            f"{format_num(total, True)} manns á milli tilgreindra svæða árið {year}."
        )

    elif table_code == "LAU04000":
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


def fetch_table_data(table_url: str, question: str) -> dict:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    try:
        meta_res = requests.get(table_url, headers=headers, timeout=15)
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
        found_month = None
        for m_key in sorted(MANUDIR_MAPPING.keys(), key=len, reverse=True):
            if re.search(r"\b" + re.escape(m_key), q_clean):
                found_month = MANUDIR_MAPPING[m_key]
                break

        for var in variables:
            v_code = var.get("code")
            v_text = hreinsa_texta(var.get("text", ""))
            v_vals = var.get("values", [])

            if "manudur" in v_text or "month" in v_text or v_code == "Mánuður":
                if not found_month:
                    m_target = v_vals[-1]
                    target_year = int(m_target[:4])
                    found_month = m_target[-2:]
                else:
                    target_year = int(years[0]) if years else int(v_vals[-1][:4])
                    m_target = f"{target_year}M{found_month}"
                    if m_target not in v_vals:
                        m_target = v_vals[-1]
                        target_year = int(m_target[:4])
                        found_month = m_target[-2:]

                prev_target = f"{target_year - 1}M{found_month}"
                selected = [m for m in [prev_target, m_target] if m in v_vals]
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
                found_month = None
                for m_key in sorted(MANUDIR_MAPPING.keys(), key=len, reverse=True):
                    if re.search(r"\b" + re.escape(m_key), q_clean):
                        found_month = MANUDIR_MAPPING[m_key]
                        break
                if found_month and years:
                    target = f"{years[0]}M{found_month}"
                    sel = [target] if target in v_vals else [v_vals[-1]]
                else:
                    sel = [v_vals[-1]]
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": sel}})
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
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[-1]]}})
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
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[-1]]}})
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
                # Old/merged names (Seyðisfjörður -> Múlaþing) can't be found by stem matching
                alias = resolve_municipality(q_clean) if "sveitarfelag" in v_text else None
                if alias in v_texts:
                    matched_val = v_vals[v_texts.index(alias)]
                else:
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
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [matched_val]}})
            elif "aldur" in v_text:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[0]]}})
            elif "ar" in v_text:
                y = [years[0]] if (years and years[0] in v_vals) else [v_vals[-1]]
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": y}})
            elif "kyn" in v_text:
                sex_vals, _ = _match_sex(q_clean, v_vals, v_texts)
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": sex_vals}})
            else:
                query_list.append({"code": v_code, "selection": {"filter": "item", "values": [v_vals[0]]}})

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
        data_res = requests.post(
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

    if table_code == "VIS01002" and len(rows) >= 2:
        try:
            v_prev = float(rows[0]["values"][0])
            v_curr = float(rows[1]["values"][0])
            m_prev = rows[0]["key"][0]
            m_curr = rows[1]["key"][0]
            infl = ((v_curr - v_prev) / v_prev) * 100
            computed["v_prev"] = v_prev
            computed["v_curr"] = v_curr
            computed["m_prev"] = m_prev
            computed["m_curr"] = m_curr
            computed["infl"] = infl
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
            for r in rows:
                if len(r.get("key", [])) > 1:
                    e_code = r["key"][1]
                    if e_code == "index":
                        computed["wage_index"] = float(r["values"][0])
                    elif e_code == "change_A":
                        computed["wage_growth"] = float(r["values"][0])
                    computed["m_curr"] = r["key"][0]
        except Exception:
            pass

    elif table_code == "VIN00001":
        try:
            for r in rows:
                if len(r.get("key", [])) > 2:
                    e_code = r["key"][2]
                    if e_code == "7":
                        computed["unemployment_rate"] = float(r["values"][0])
                    elif e_code == "3":
                        computed["unemployed_count"] = int(r["values"][0])
                    computed["m_curr"] = r["key"][0]
        except Exception:
            pass

    elif table_code == "SAM02001":
        try:
            if rows:
                computed["passenger_count"] = int(rows[0]["values"][0])
                cat_code = rows[0]["key"][0]
                computed["category_name"] = label_lookup.get("Ríkisfang", {}).get(cat_code, "farþegar")
                computed["m_curr"] = rows[0]["key"][1]
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
