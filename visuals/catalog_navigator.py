"""
visuals/catalog_navigator.py - Gagnvirkt Töflusafn og Lýsigagnaskoðari Hagstofunnar

Hleður inn yfir 100 töflum úr 'data/hagstofa_catalog.json' og veitir
leitar-, flokkunar- og fyrirspurnarviðmót með rómverskri hönnun.
"""

import json
import os
from typing import Dict, List, Optional

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "hagstofa_catalog.json")

CATEGORY_ICONS = {
    "Efnahagur": "🏛️",
    "Ibuar": "👥",
    "Samfelag": "⚖️",
    "Sogulegar": "📜",
    "Umhverfi": "🌋",
    "Atvinnuvegir": "🚢",
    "General": "📊",
}


def load_full_catalog() -> List[Dict]:
    """Hleður inn töfluskránni af disknum."""
    if not os.path.exists(CATALOG_PATH):
        return []
    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def search_catalog(
    catalog: List[Dict],
    query: str = "",
    category: Optional[str] = None,
) -> List[Dict]:
    """Sía töflusafnið eftir leitarorði og málaflokki."""
    results = catalog
    if category and category != "Allir flokkar":
        results = [t for t in results if t.get("category", "") == category]

    if query.strip():
        q_lower = query.lower().strip()
        filtered = []
        for t in results:
            t_id = t.get("id", "").lower()
            t_title = t.get("title", "").lower()
            t_cat = t.get("category", "").lower()
            if q_lower in t_id or q_lower in t_title or q_lower in t_cat:
                filtered.append(t)
        results = filtered

    return results


def render_catalog_card_html(table: Dict) -> str:
    """Býr til glæsilegt rómverskt spjald fyrir eina töflu."""
    cat = table.get("category", "General")
    icon = CATEGORY_ICONS.get(cat, "📊")
    t_id = table.get("id", "N/A")
    title = table.get("title", "")
    url = table.get("url", "#")

    return f"""
<div style="background-color: #EDE8E1; border: 1.5px solid #C5A059; border-radius: 3px;
            padding: 1.1rem 1.4rem; margin-bottom: 0.9rem; box-shadow: 0 2px 6px rgba(0,0,0,0.12);
            transition: transform 0.2s ease;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
        <span style="font-family: 'Cinzel', serif; font-size: 0.72rem; font-weight: 700;
                     letter-spacing: 0.2em; color: #8B6914; text-transform: uppercase;">
            {icon} {cat} &nbsp;&middot;&nbsp; TAFLA {t_id}
        </span>
        <a href="{url}" target="_blank" style="font-family: 'Cinzel', serif; font-size: 0.7rem;
                                              color: #1A2E40; text-decoration: none; border-bottom: 1px dotted #8B6914;">
            PX-Web Slóð &rarr;
        </a>
    </div>
    <div style="font-family: 'Lora', Georgia, serif; font-size: 1.05rem; font-weight: 600;
                color: #1A2530; line-height: 1.4; margin-bottom: 0.5rem;">
        {title}
    </div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #556B2F;">
        ENDPOINT: {url}
    </div>
</div>
"""
