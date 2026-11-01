"""
visuals/trade_and_fisheries.py - Sjávarútvegur, Þorskastríðin og Útflutningsverðmæti

Geymir söguleg gögn Hagstofu Íslands um fiskveiðar, síldarárin, Þorskastríðin við Breta
og þróun landhelginnar úr 3 mílum í 200 sjómílur (Töflur SOG04010, XLAN10201).
"""

from typing import Dict, List, Optional, Tuple

# Þorskastríðin og útfærsla landhelginnar
COD_WARS_TIMELINE = [
    {
        "year": 1952,
        "miles": 4,
        "event": "Fjögurra mílna landhelgi",
        "description": "Ísland færir grunnlínu og stækkar fiskveiðilögsögu úr 3 í 4 sjómílur. Bretar beita löndunarbanni á íslenskan fisk.",
        "outcome": "Ísland finnur nýja markaði í Bandaríkjunum og Sovétríkjunum.",
    },
    {
        "year": 1958,
        "miles": 12,
        "event": "Fyrsta þorskastríðið (12 mílur)",
        "description": "Landhelgin færð út í 12 sjómílur. Bresk herskip send á Íslandsmið til að vernda breska togara.",
        "outcome": "Bretar viðurkenna 12 mílna mörkin árið 1961.",
    },
    {
        "year": 1972,
        "miles": 50,
        "event": "Annað þorskastríðið (50 mílur)",
        "description": "Landhelgin færð í 50 sjómílur. Landhelgisgæslan beitir togaraklippum í fyrsta sinn til að klippa á vörpur breskra togara.",
        "outcome": "Sigur Íslands; Bretar semja um tímabundnar takmarkaðar veiðar 1973.",
    },
    {
        "year": 1975,
        "miles": 200,
        "event": "Þriðja þorskastríðið (200 mílur)",
        "description": "200 sjómílna efnahagslögsaga lýst yfir. Siglt á varðskip og bresk herskip (frigate) sigla á íslensk varðskip. Stjórnmálasambandi slitið.",
        "outcome": "Fullur sigur Íslands 1976; 200 sjómílna efnahagslögsaga varð alþjóðlegur staðall í hafréttarsáttmála SÞ.",
    },
]

# Sögulegur þorskafli Íslendinga (þúsund tonn hvert ár 1920-2026 úr SOG04010)
COD_CATCH_HISTORICAL = [
    (1920, 115), (1925, 170), (1930, 250), (1935, 160), (1940, 145),
    (1945, 220), (1950, 240), (1955, 290), (1960, 260), (1965, 245),
    (1970, 310), (1975, 270), (1980, 430), (1985, 320), (1990, 335),
    (1995, 170), (2000, 235), (2005, 215), (2010, 170), (2015, 215),
    (2020, 270), (2024, 210), (2026, 215),
]

# Sögulegur síldarafli (þúsund tonn - sýnir síldarævintýrið og hrunið)
HERRING_CATCH_HISTORICAL = [
    (1930, 65), (1938, 120), (1944, 220), (1950, 60), (1955, 55),
    (1960, 135), (1962, 480), (1965, 760), (1966, 770), (1968, 140),
    (1970, 20), (1972, 0), (1980, 50), (1990, 95), (2000, 150),
    (2010, 180), (2020, 110), (2026, 125),
]


def generate_fisheries_svg(width: int = 760, height: int = 400) -> str:
    """Býr til SVG-línurit yfir sögu þorsk- og síldveiða á Íslandi."""
    p_left, p_right, p_top, p_bottom = 60, 35, 45, 50
    g_w = width - p_left - p_right
    g_h = height - p_top - p_bottom

    min_yr, max_yr = 1920, 2026
    max_catch = 850.0

    def xs(yr: int) -> float:
        return p_left + ((yr - min_yr) / (max_yr - min_yr)) * g_w

    def ys(val: float) -> float:
        return p_top + g_h - (val / max_catch) * g_h

    cod_pts = [f"{xs(y):.1f},{ys(v):.1f}" for y, v in COD_CATCH_HISTORICAL]
    herring_pts = [f"{xs(y):.1f},{ys(v):.1f}" for y, v in HERRING_CATCH_HISTORICAL]

    svg = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: #1A2E40; border: 2px solid #C5A059; border-radius: 4px; width: 100%; height: auto;">',
        '<text x="25" y="30" font-family="Cinzel, Georgia, serif" font-size="13" font-weight="700" fill="#C5A059" letter-spacing="2">ÞORSKAFLI OG SÍLDARÆVINTÝRIÐ (1920–2026)</text>',
        '<text x="25" y="44" font-family="Lora, serif" font-size="10" fill="#8FA5BC" font-style="italic">Tafla SOG04010 &middot; Afli í þúsundum tonna á ári</text>',
    ]

    # Gridlines
    for tick in [200, 400, 600, 800]:
        yp = ys(tick)
        svg.append(f'<line x1="{p_left}" y1="{yp:.1f}" x2="{width - p_right}" y2="{yp:.1f}" stroke="#2A445E" stroke-width="1" stroke-dasharray="2,3" />')
        svg.append(f'<text x="{p_left - 8}" y="{yp + 3:.1f}" text-anchor="end" font-family="JetBrains Mono, monospace" font-size="9" fill="#8FA5BC">{tick}k</text>')

    for yr in range(1920, 2030, 20):
        xp = xs(yr)
        svg.append(f'<line x1="{xp:.1f}" y1="{p_top}" x2="{xp:.1f}" y2="{p_top + g_h}" stroke="#2A445E" stroke-width="1" stroke-dasharray="2,3" />')
        svg.append(f'<text x="{xp:.1f}" y="{p_top + g_h + 16}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="10" fill="#EAE3D6">{yr}</text>')

    # Síldarævintýrið merkt (Toppur 1966)
    s_x, s_y = xs(1966), ys(770)
    svg.extend([
        f'<circle cx="{s_x:.1f}" cy="{s_y:.1f}" r="5" fill="#4ECDC4" stroke="#FFFFFF" stroke-width="1" />',
        f'<text x="{s_x:.1f}" y="{s_y - 10:.1f}" text-anchor="middle" font-family="Lora, serif" font-size="9" fill="#4ECDC4" font-weight="700">1966: Síldartoppur (770k t)</text>',
    ])

    # Síldarlína (blágræn)
    svg.append(f'<path d="M {" L ".join(herring_pts)}" fill="none" stroke="#4ECDC4" stroke-width="2.5" />')

    # Þorsklína (Gull)
    svg.append(f'<path d="M {" L ".join(cod_pts)}" fill="none" stroke="#FFD700" stroke-width="2.8" />')

    # Skýringar
    svg.extend([
        f'<circle cx="{width - 200}" cy="30" r="5" fill="#FFD700" />',
        f'<text x="{width - 190}" y="34" font-family="Cinzel, serif" font-size="10" fill="#FFD700">Þorskur (Gadus morhua)</text>',
        f'<circle cx="{width - 70}" cy="30" r="5" fill="#4ECDC4" />',
        f'<text x="{width - 60}" y="34" font-family="Cinzel, serif" font-size="10" fill="#4ECDC4">Síld</text>',
    ])

    svg.append('</svg>')
    return "\n".join(svg)
