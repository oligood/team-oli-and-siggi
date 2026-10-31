import re
import unicodedata
import requests

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


def hreinsa_texta(texti: str) -> str:
    nfkd = unicodedata.normalize("NFKD", str(texti))
    flat = "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()
    for k, v in {"þ": "th", "æ": "ae", "ö": "o", "ð": "d"}.items():
        flat = flat.replace(k, v)
    return flat


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

    if table_code == "VIS01002":
        found_month = None
        for m_key in sorted(MANUDIR_MAPPING.keys(), key=len, reverse=True):
            if re.search(r"\b" + re.escape(m_key), q_clean):
                found_month = MANUDIR_MAPPING[m_key]
                break
        if not found_month:
            found_month = "01"

        is_inflation = any(w in q_clean for w in ["verdbolg", "inflation"])

        for var in variables:
            v_code = var.get("code")
            v_text = hreinsa_texta(var.get("text", ""))
            v_vals = var.get("values", [])

            if "manudur" in v_text or "month" in v_text or v_code == "Mánuður":
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
                for idx, vt in enumerate(v_texts):
                    vt_clean = hreinsa_texta(vt)
                    # Strip leading district numbers like "1 vesturbaer"
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
        return {"ok": False, "error": "No data found for the selected filters."}

    # Map variable codes to valueTexts for readable output
    label_lookup = {}
    for var in variables:
        mapping = dict(zip(var.get("values", []), var.get("valueTexts", [])))
        label_lookup[var.get("code")] = mapping

    var_codes = [col.get("code") for col in api_data.get("columns", []) if col.get("type") != "c"]

    readable_rows = []
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

    summary_text = "; ".join(readable_rows)

    if table_code == "MAN01002" and len(rows) > 1:
        try:
            total = sum(int(r["values"][0]) for r in rows if r.get("values"))
            summary_text = f"Samtals {total} manns ({summary_text})"
        except Exception:
            pass

    # Calculate 12-month inflation if VIS01002 has 2 months
    if table_code == "VIS01002" and len(rows) == 2:
        try:
            v_prev = float(rows[0]["values"][0])
            v_curr = float(rows[1]["values"][0])
            m_prev = rows[0]["key"][0]
            m_curr = rows[1]["key"][0]
            infl = ((v_curr - v_prev) / v_prev) * 100
            summary_text = (
                f"Vísitala neysluverðs í {m_curr} var {v_curr} stig (var {v_prev} stig í {m_prev}). "
                f"12 mánaða breyting (verðbólga) var {infl:.2f}%."
            )
        except Exception:
            pass

    return {
        "ok": True,
        "table_id": table_code,
        "title": title,
        "source_url": table_url,
        "query_used": query_list,
        "facts": readable_rows,
        "summary": summary_text,
    }


if __name__ == "__main__":
    res = fetch_table_data(
        "https://px.hagstofa.is/pxis/api/v1/is/Ibuar/mannfjoldi/2_byggdir/sveitarfelog/MAN02005.px",
        "Hvað búa margir í Kópavogi árið 2025?",
    )
    print(res)
