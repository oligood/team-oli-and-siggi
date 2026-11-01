"""
visuals/geo_iceland.py - Gagnvirkt Íslandskort og Svæðagreining Hagstofu Íslands

Inniheldur ítarleg SVG-hnit fyrir alla landshluta Íslands, hverfi Reykjavíkur,
búferlaflutningaörvar milli svæða og mannfjöldahitakort.
"""

import json
from typing import Dict, List, Optional, Tuple

REGIONS_DATA = {
    "1": {
        "id": "1",
        "name": "Höfuðborgarsvæðið",
        "latin": "Regio Capitalis",
        "population_2026": 248760,
        "population_2020": 233034,
        "population_2010": 202341,
        "population_2000": 175000,
        "area_km2": 1042,
        "center_x": 190,
        "center_y": 380,
        "municipalities": [
            "Reykjavíkurborg", "Kópavogsbær", "Hafnarfjarðarkaupstaður",
            "Garðabær", "Mosfellsbær", "Seltjarnarnesbær", "Kjósarhreppur"
        ],
        "svg_path": (
            "M 175,360 L 195,362 L 205,375 L 210,390 L 195,400 L 180,395 "
            "L 170,380 L 175,360 Z"
        ),
        "color": "#8B6914",
    },
    "2": {
        "id": "2",
        "name": "Suðurnes",
        "latin": "Promontorium Australe",
        "population_2026": 32150,
        "population_2020": 27829,
        "population_2010": 21359,
        "population_2000": 16400,
        "area_km2": 829,
        "center_x": 140,
        "center_y": 425,
        "municipalities": ["Reykjanesbær", "Suðurnesjabær", "Grindavíkurbær", "Vogar"],
        "svg_path": (
            "M 155,400 L 180,395 L 170,420 L 150,445 L 120,440 L 125,415 "
            "L 145,405 L 155,400 Z"
        ),
        "color": "#A07828",
    },
    "3": {
        "id": "3",
        "name": "Vesturland",
        "latin": "Terra Occidentalis",
        "population_2026": 17890,
        "population_2020": 16669,
        "population_2010": 15370,
        "population_2000": 14250,
        "area_km2": 9554,
        "center_x": 190,
        "center_y": 290,
        "municipalities": [
            "Akraneskaupstaður", "Borgarbyggð", "Snæfellsbær",
            "Grundarfjarðarbær", "Stykkishólmur", "Dalabyggð", "Hvalfjarðarsveit"
        ],
        "svg_path": (
            "M 175,360 L 170,330 L 130,310 L 80,315 L 65,305 L 85,295 "
            "L 140,290 L 180,265 L 210,270 L 225,310 L 210,350 L 195,362 Z"
        ),
        "color": "#B8860B",
    },
    "4": {
        "id": "4",
        "name": "Vestfirðir",
        "latin": "Sinus Occidentales",
        "population_2026": 7450,
        "population_2020": 7115,
        "population_2010": 7374,
        "population_2000": 8150,
        "area_km2": 9409,
        "center_x": 150,
        "center_y": 170,
        "municipalities": [
            "Ísafjarðarbær", "Vesturbyggð", "Bolungarvíkurkaupstaður",
            "Súðavíkurhreppur", "Tálknafjarðarhreppur", "Strandabyggð", "Kaldrananeshreppur"
        ],
        "svg_path": (
            "M 140,290 L 120,265 L 90,260 L 80,230 L 105,210 L 95,180 "
            "L 115,140 L 145,120 L 170,135 L 160,170 L 195,190 L 180,240 "
            "L 180,265 L 140,290 Z"
        ),
        "color": "#997300",
    },
    "5": {
        "id": "5",
        "name": "Norðurland vestra",
        "latin": "Septentrio Occidentalis",
        "population_2026": 7520,
        "population_2020": 7322,
        "population_2010": 7393,
        "population_2000": 7890,
        "area_km2": 12737,
        "center_x": 300,
        "center_y": 210,
        "municipalities": [
            "Skagafjörður", "Húnabyggð", "Húnaþing vestra", "Skagaströnd"
        ],
        "svg_path": (
            "M 210,270 L 225,230 L 250,195 L 290,175 L 340,190 L 330,240 "
            "L 300,270 L 250,285 L 210,270 Z"
        ),
        "color": "#A67C00",
    },
    "6": {
        "id": "6",
        "name": "Norðurland eystra",
        "latin": "Septentrio Orientalis",
        "population_2026": 32180,
        "population_2020": 30600,
        "population_2010": 28925,
        "population_2000": 26800,
        "area_km2": 21968,
        "center_x": 450,
        "center_y": 200,
        "municipalities": [
            "Akureyrarbær", "Norðurþing", "Fjallabyggð", "Dalvíkurbyggð",
            "Eyjafjarðarsveit", "Hörgársveit", "Svalbarðsstrandarhreppur",
            "Grýtubakkahreppur", "Þingeyjarsveit", "Tjörneshreppur"
        ],
        "svg_path": (
            "M 340,190 L 375,170 L 415,160 L 475,165 L 530,195 L 515,250 "
            "L 450,280 L 370,270 L 330,240 Z"
        ),
        "color": "#B8860B",
    },
    "7": {
        "id": "7",
        "name": "Austurland",
        "latin": "Terra Orientalis",
        "population_2026": 11490,
        "population_2020": 10850,
        "population_2010": 12459,
        "population_2000": 11780,
        "area_km2": 22721,
        "center_x": 600,
        "center_y": 290,
        "municipalities": ["Múlaþing", "Fjarðabyggð", "Vopnafjarðarhreppur", "Fljótsdalshreppur"],
        "svg_path": (
            "M 530,195 L 590,210 L 650,240 L 680,280 L 670,340 L 610,380 "
            "L 560,350 L 520,300 L 515,250 Z"
        ),
        "color": "#C5A059",
    },
    "8": {
        "id": "8",
        "name": "Suðurland",
        "latin": "Terra Meridionalis",
        "population_2026": 34850,
        "population_2020": 31544,
        "population_2010": 23894,
        "population_2000": 21100,
        "area_km2": 24560,
        "center_x": 360,
        "center_y": 380,
        "municipalities": [
            "Sveitarfélagið Árborg", "Reykjanesbær (hluti)", "Hveragerðisbær",
            "Sveitarfélagið Ölfus", "Rangárþing eystra", "Rangárþing ytra",
            "Mýrdalshreppur", "Skaftárhreppur", "Sveitarfélagið Hornafjörður",
            "Vestmannaeyjabær", "Bláskógabyggð", "Grímsnes- og Grafningshreppur",
            "Hrunamannahreppur", "Skeiða- og Gnúpverjahreppur", "Flóahreppur"
        ],
        "svg_path": (
            "M 210,390 L 225,350 L 250,285 L 300,270 L 370,270 L 450,280 "
            "L 520,300 L 560,350 L 540,410 L 450,440 L 350,450 L 260,435 "
            "L 210,390 Z"
        ),
        "color": "#D4AF37",
    },
}

MIGRATION_FLOWS_2024 = [
    {"from": "6", "to": "1", "label": "Norðurland eystra → Höfuðborgarsvæðið", "count": 607},
    {"from": "8", "to": "1", "label": "Suðurland → Höfuðborgarsvæðið", "count": 1023},
    {"from": "2", "to": "1", "label": "Suðurnes → Höfuðborgarsvæðið", "count": 2129},
    {"from": "3", "to": "1", "label": "Vesturland → Höfuðborgarsvæðið", "count": 477},
    {"from": "7", "to": "1", "label": "Austurland → Höfuðborgarsvæðið", "count": 250},
    {"from": "4", "to": "1", "label": "Vestfirðir → Höfuðborgarsvæðið", "count": 249},
    {"from": "5", "to": "1", "label": "Norðurland vestra → Höfuðborgarsvæðið", "count": 170},
    {"from": "1", "to": "8", "label": "Höfuðborgarsvæðið → Suðurland", "count": 1240},
    {"from": "1", "to": "2", "label": "Höfuðborgarsvæðið → Suðurnes", "count": 1850},
    {"from": "1", "to": "6", "label": "Höfuðborgarsvæðið → Norðurland eystra", "count": 520},
]

REYKJAVIK_DISTRICTS = {
    "1": {"name": "Vesturbær", "pop_2026": 16453, "code": "1", "color": "#8B6914"},
    "2": {"name": "Miðborg", "pop_2026": 11200, "code": "2", "color": "#A07828"},
    "3": {"name": "Hlíðar", "pop_2026": 10850, "code": "3", "color": "#B8860B"},
    "4": {"name": "Laugardalur", "pop_2026": 19400, "code": "4", "color": "#C5A059"},
    "5": {"name": "Háaleiti og Bústaðir", "pop_2026": 16100, "code": "5", "color": "#997300"},
    "6": {"name": "Breiðholt", "pop_2026": 21800, "code": "6", "color": "#D4AF37"},
    "7": {"name": "Árbær", "pop_2026": 12100, "code": "7", "color": "#A67C00"},
    "8": {"name": "Grafarvogur", "pop_2026": 18200, "code": "8", "color": "#8B6914"},
    "9": {"name": "Kjalarnes", "pop_2026": 1150, "code": "9", "color": "#A07828"},
    "10": {"name": "Grafarholt og Úlfarsárdalur", "pop_2026": 12551, "code": "10", "color": "#C5A059"},
}


def generate_iceland_svg(
    selected_region_id: Optional[str] = None,
    show_migration: bool = True,
    color_mode: str = "density",
) -> str:
    """Býr til fullbúið SVG-kort af Íslandi með hnitum landshluta og búferlaflutningum."""
    width = 750
    height = 500

    max_pop = max(r["population_2026"] for r in REGIONS_DATA.values())

    svg_parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: #1A2E40; border: 2px solid #C5A059; border-radius: 4px; box-shadow: 0 4px 18px rgba(0,0,0,0.45); width: 100%; height: auto;">',
        '<defs>',
        '  <linearGradient id="oceanGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '    <stop offset="0%" stop-color="#182A3A" />',
        '    <stop offset="100%" stop-color="#121F2B" />',
        '  </linearGradient>',
        '  <linearGradient id="goldFlow" x1="0%" y1="0%" x2="100%" y2="0%">',
        '    <stop offset="0%" stop-color="#FFE082" stop-opacity="0.8" />',
        '    <stop offset="100%" stop-color="#C5A059" stop-opacity="0.2" />',
        '  </linearGradient>',
        '  <marker id="goldArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#FFD700" />',
        '  </marker>',
        '  <filter id="goldGlow" x="-20%" y="-20%" width="140%" height="140%">',
        '    <feGaussianBlur stdDeviation="3" result="glow" />',
        '    <feComposite in="SourceGraphic" in2="glow" operator="over" />',
        '  </filter>',
        '</defs>',
        f'<rect width="{width}" height="{height}" fill="url(#oceanGrad)" />',
        '<!-- Rómversk skreyting á ramma -->',
        f'<rect x="8" y="8" width="{width-16}" height="{height-16}" fill="none" stroke="#C5A059" stroke-width="1" stroke-dasharray="8,4" opacity="0.4" />',
        '<text x="25" y="35" font-family="Cinzel, Georgia, serif" font-size="14" fill="#C5A059" letter-spacing="3" opacity="0.85">TABULA ISLANDIAE &middot; HAGSTOFA ÍSLANDS</text>',
        '<text x="25" y="52" font-family="Lora, serif" font-size="10" fill="#8FA5BC" font-style="italic">Mannfjöldi og búferlaflutningar milli landsvæða</text>',
        '<g id="regions">',
    ]

    for r_id, r in REGIONS_DATA.items():
        is_selected = selected_region_id == r_id
        
        if color_mode == "density":
            ratio = r["population_2026"] / max_pop
            fill_color = f"rgba(197, 160, 89, {0.25 + ratio * 0.65:.2f})"
        else:
            fill_color = r["color"]

        stroke_color = "#FFD700" if is_selected else "#C5A059"
        stroke_width = "3.5" if is_selected else "1.5"
        filter_attr = 'filter="url(#goldGlow)"' if is_selected else ""

        svg_parts.append(
            f'  <path id="reg-{r_id}" d="{r["svg_path"]}" fill="{fill_color}" '
            f'stroke="{stroke_color}" stroke-width="{stroke_width}" {filter_attr} '
            f'style="cursor: pointer; transition: all 0.25s ease;" />'
        )

        svg_parts.append(
            f'  <text x="{r["center_x"]}" y="{r["center_y"]}" text-anchor="middle" '
            f'font-family="Cinzel, serif" font-size="11" font-weight="700" fill="#FFFFFF" '
            f'style="text-shadow: 0 1px 4px rgba(0,0,0,0.9); pointer-events: none;">'
            f'{r["name"]}'
            f'</text>'
        )
        svg_parts.append(
            f'  <text x="{r["center_x"]}" y="{r["center_y"] + 14}" text-anchor="middle" '
            f'font-family="JetBrains Mono, monospace" font-size="10" fill="#FFD700" '
            f'style="text-shadow: 0 1px 3px rgba(0,0,0,0.9); pointer-events: none;">'
            f'{r["population_2026"]:,} íbúar'
            f'</text>'
        )

    svg_parts.append('</g>')

    if show_migration:
        svg_parts.append('<g id="migration-arrows" opacity="0.95">')
        for flow in MIGRATION_FLOWS_2024:
            r_from = REGIONS_DATA.get(flow["from"])
            r_to = REGIONS_DATA.get(flow["to"])
            if r_from and r_to:
                fx, fy = r_from["center_x"], r_from["center_y"]
                tx, ty = r_to["center_x"], r_to["center_y"]
                
                # Bogin lína milli miðpunkta
                mx = (fx + tx) / 2 + (fy - ty) * 0.15
                my = (fy + ty) / 2 + (tx - fx) * 0.15

                stroke_w = max(1.5, min(6.0, flow["count"] / 350))
                svg_parts.append(
                    f'  <path d="M {fx},{fy} Q {mx},{my} {tx},{ty}" fill="none" '
                    f'stroke="url(#goldFlow)" stroke-width="{stroke_w:.1f}" '
                    f'marker-end="url(#goldArrow)" stroke-linecap="round" />'
                )
        svg_parts.append('</g>')

    # Skýringamynd (Legend) neðst til hægri
    svg_parts.extend([
        '<g transform="translate(560, 410)">',
        '  <rect width="170" height="75" fill="rgba(26,46,64,0.85)" stroke="#C5A059" stroke-width="1" rx="3" />',
        '  <text x="10" y="20" font-family="Cinzel, serif" font-size="10" font-weight="700" fill="#C5A059">SKÝRINGAR</text>',
        '  <circle cx="20" cy="38" r="5" fill="rgba(197,160,89,0.8)" stroke="#FFD700" />',
        '  <text x="35" y="42" font-family="Lora, serif" font-size="10" fill="#EAE3D6">Mannfjöldi 2026</text>',
        '  <line x1="12" y1="58" x2="28" y2="58" stroke="#FFD700" stroke-width="2.5" marker-end="url(#goldArrow)" />',
        '  <text x="35" y="62" font-family="Lora, serif" font-size="10" fill="#EAE3D6">Búferlaflutningar (2024)</text>',
        '</g>',
        '</svg>',
    ])

    return "\n".join(svg_parts)


def generate_reykjavik_districts_svg() -> str:
    """Býr til sérhæft SVG-hverfakort fyrir Reykjavík."""
    width = 700
    height = 420
    
    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: #1A2E40; border: 2px solid #C5A059; border-radius: 4px; width: 100%; height: auto;">',
        '<text x="20" y="35" font-family="Cinzel, Georgia, serif" font-size="13" fill="#C5A059" letter-spacing="2">HVERFI REYKJAVÍKUR (TAFLA MAN03270)</text>',
        '<g transform="translate(30, 60)">',
    ]

    total_reykjavik = sum(d["pop_2026"] for d in REYKJAVIK_DISTRICTS.values())
    y_offset = 0

    for code, d in sorted(REYKJAVIK_DISTRICTS.items(), key=lambda x: x[1]["pop_2026"], reverse=True):
        bar_len = int((d["pop_2026"] / 25000) * 380)
        pct = (d["pop_2026"] / total_reykjavik) * 100

        parts.append(f'<g transform="translate(0, {y_offset})">')
        parts.append(
            f'  <text x="0" y="16" font-family="Lora, serif" font-size="12" fill="#EAE3D6">'
            f'{d["name"]}'
            f'</text>'
        )
        parts.append(
            f'  <rect x="200" y="4" width="{bar_len}" height="16" fill="{d["color"]}" '
            f'stroke="#1A2E40" rx="2" />'
        )
        parts.append(
            f'  <text x="{210 + bar_len}" y="16" font-family="JetBrains Mono, monospace" font-size="11" fill="#FFD700">'
            f'{d["pop_2026"]:,} ({pct:.1f}%)'
            f'</text>'
        )
        parts.append('</g>')
        y_offset += 30

    parts.append('</g>')
    parts.append('</svg>')
    return "\n".join(parts)


def get_regional_summary_table() -> List[Dict]:
    """Skilar yfirliti yfir alla landshluta til birtingar í töflu."""
    rows = []
    for r in REGIONS_DATA.values():
        growth_20yr = ((r["population_2026"] - r["population_2000"]) / r["population_2000"]) * 100
        density = r["population_2026"] / r["area_km2"]
        rows.append({
            "Landshluti": r["name"],
            "Rómverskt heiti": r["latin"],
            "Íbúafjöldi 2026": f"{r['population_2026']:,}",
            "Íbúafjöldi 2000": f"{r['population_2000']:,}",
            "26 ára breyting": f"{growth_20yr:+.1f}%",
            "Flatarmál (km²)": f"{r['area_km2']:,}",
            "Þéttleiki (íb/km²)": f"{density:.1f}",
            "Sveitarfélög": len(r["municipalities"]),
        })
    return rows
