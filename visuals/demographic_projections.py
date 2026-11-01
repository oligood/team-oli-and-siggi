"""
visuals/demographic_projections.py - Mannfjöldaspá Hagstofu Íslands (2026–2075)

Geymir opinbera mannfjöldaspá Hagstofu Íslands (Tafla MAN09010 og MAN09012)
með lágspá, miðspá og háspá, öldrun þjóðarinnar og áætlaðri þróun vinnuafls.
"""

from typing import Dict, List, Optional, Tuple

# Opinber mannfjöldaspá Hagstofu Íslands (2026–2075) - Heildaríbúafjöldi í þúsundum
PROJECTIONS_DATA = [
    {"year": 2026, "low": 390.5, "medium": 394.3, "high": 398.2, "elderly_pct": 15.6, "working_pct": 65.2},
    {"year": 2030, "low": 402.1, "medium": 412.5, "high": 423.8, "elderly_pct": 17.1, "working_pct": 64.0},
    {"year": 2035, "low": 414.2, "medium": 432.8, "high": 453.4, "elderly_pct": 19.2, "working_pct": 62.4},
    {"year": 2040, "low": 423.8, "medium": 451.2, "high": 481.9, "elderly_pct": 21.4, "working_pct": 60.8},
    {"year": 2045, "low": 430.5, "medium": 467.4, "high": 508.6, "elderly_pct": 23.0, "working_pct": 59.5},
    {"year": 2050, "low": 434.9, "medium": 481.6, "high": 533.8, "elderly_pct": 24.2, "working_pct": 58.6},
    {"year": 2055, "low": 437.2, "medium": 494.0, "high": 557.9, "elderly_pct": 25.0, "working_pct": 58.0},
    {"year": 2060, "low": 437.8, "medium": 504.8, "high": 580.4, "elderly_pct": 25.5, "working_pct": 57.6},
    {"year": 2065, "low": 437.0, "medium": 514.2, "high": 601.5, "elderly_pct": 25.8, "working_pct": 57.4},
    {"year": 2070, "low": 435.1, "medium": 522.4, "high": 621.8, "elderly_pct": 26.1, "working_pct": 57.2},
    {"year": 2075, "low": 432.4, "medium": 529.5, "high": 641.2, "elderly_pct": 26.5, "working_pct": 57.0},
]

# Lykildrifkraftar mannfjöldaspárinnar
PROJECTION_DRIVERS = [
    {
        "factor": "Frjósemi kvenna (TFR)",
        "low_scenario": "Lækkar í 1.40 börn",
        "medium_scenario": "Helst um 1.60 börn",
        "high_scenario": "Hækkar í 1.80 börn",
        "impact": "Ræður miklu um stærð yngri aldurshópa og fjölda í skólakerfinu.",
    },
    {
        "factor": "Aðflutningur erlendra ríkisborgara",
        "low_scenario": "+1.500 á ári",
        "medium_scenario": "+3.000 á ári",
        "high_scenario": "+5.000 á ári",
        "impact": "Meginástæða þess að Íslandi vex hraðar en flestum öðrum Evrópuríkjum.",
    },
    {
        "factor": "Lífslíkur við fæðingu (2075)",
        "low_scenario": "86.0 ár (k) / 88.5 ár (k)",
        "medium_scenario": "88.2 ár (k) / 90.8 ár (k)",
        "high_scenario": "90.5 ár (k) / 93.0 ár (k)",
        "impact": "Fjölgar þeim sem ná 80 ára og eldri um meira en helming.",
    },
]


def generate_projections_svg(width: int = 760, height: int = 420) -> str:
    """Teiknar SVG-línurit yfir mannfjöldaspá Íslands 2026–2075 (Lág-, Mið- og Háspá)."""
    p_left, p_right, p_top, p_bottom = 60, 40, 45, 50
    g_w = width - p_left - p_right
    g_h = height - p_top - p_bottom

    min_yr, max_yr = 2026, 2075
    min_pop, max_pop = 350.0, 680.0

    def xs(yr: int) -> float:
        return p_left + ((yr - min_yr) / (max_yr - min_yr)) * g_w

    def ys(val: float) -> float:
        return p_top + g_h - ((val - min_pop) / (max_pop - min_pop)) * g_h

    pts_high = [f"{xs(d['year']):.1f},{ys(d['high']):.1f}" for d in PROJECTIONS_DATA]
    pts_med = [f"{xs(d['year']):.1f},{ys(d['medium']):.1f}" for d in PROJECTIONS_DATA]
    pts_low = [f"{xs(d['year']):.1f},{ys(d['low']):.1f}" for d in PROJECTIONS_DATA]

    # Shaded band milli lág- og háspár
    band_path = (
        f"M {pts_high[0]} " +
        " ".join([f"L {p}" for p in pts_high[1:]]) +
        " " +
        " ".join([f"L {p}" for p in reversed(pts_low)]) +
        " Z"
    )

    svg = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: #1A2E40; border: 2px solid #C5A059; border-radius: 4px; width: 100%; height: auto;">',
        '<defs>',
        '  <linearGradient id="projBand" x1="0%" y1="0%" x2="0%" y2="100%">',
        '    <stop offset="0%" stop-color="#C5A059" stop-opacity="0.35" />',
        '    <stop offset="100%" stop-color="#C5A059" stop-opacity="0.1" />',
        '  </linearGradient>',
        '</defs>',
        '<text x="25" y="30" font-family="Cinzel, Georgia, serif" font-size="13" font-weight="700" fill="#C5A059" letter-spacing="2">MANNFJÖLDASPÁ HAGSTOFU ÍSLANDS (2026–2075)</text>',
        '<text x="25" y="44" font-family="Lora, serif" font-size="10" fill="#8FA5BC" font-style="italic">Tafla MAN09010 &middot; Spá um fólksfjölda eftir lágspá, miðspá og háspá</text>',
    ]

    # Gridlines
    for p_val in [400, 450, 500, 550, 600, 650]:
        yp = ys(p_val)
        svg.append(f'<line x1="{p_left}" y1="{yp:.1f}" x2="{width - p_right}" y2="{yp:.1f}" stroke="#2A445E" stroke-width="1" stroke-dasharray="2,3" />')
        svg.append(f'<text x="{p_left - 8}" y="{yp + 3:.1f}" text-anchor="end" font-family="JetBrains Mono, monospace" font-size="9" fill="#8FA5BC">{p_val}k</text>')

    for yr in range(2030, 2080, 10):
        xp = xs(yr)
        svg.append(f'<line x1="{xp:.1f}" y1="{p_top}" x2="{xp:.1f}" y2="{p_top + g_h}" stroke="#2A445E" stroke-width="1" stroke-dasharray="2,3" />')
        svg.append(f'<text x="{xp:.1f}" y="{p_top + g_h + 16}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="10" fill="#EAE3D6">{yr}</text>')

    # Shaded band
    svg.append(f'<path d="{band_path}" fill="url(#projBand)" />')

    # Háspá (grænleit/ljós)
    svg.append(f'<path d="M {" L ".join(pts_high)}" fill="none" stroke="#4ECDC4" stroke-width="2" stroke-dasharray="4,3" />')

    # Lágspá (rauðleit/dökk)
    svg.append(f'<path d="M {" L ".join(pts_low)}" fill="none" stroke="#FF6B6B" stroke-width="2" stroke-dasharray="4,3" />')

    # Miðspá (Gull)
    svg.append(f'<path d="M {" L ".join(pts_med)}" fill="none" stroke="#FFD700" stroke-width="3" />')

    # Skýringar
    svg.extend([
        f'<circle cx="{width - 240}" cy="30" r="5" fill="#4ECDC4" />',
        f'<text x="{width - 230}" y="34" font-family="Cinzel, serif" font-size="9" fill="#4ECDC4">Háspá (641k)</text>',
        f'<circle cx="{width - 150}" cy="30" r="5" fill="#FFD700" />',
        f'<text x="{width - 140}" y="34" font-family="Cinzel, serif" font-size="9" fill="#FFD700">Miðspá (530k)</text>',
        f'<circle cx="{width - 65}" cy="30" r="5" fill="#FF6B6B" />',
        f'<text x="{width - 55}" y="34" font-family="Cinzel, serif" font-size="9" fill="#FF6B6B">Lágspá (432k)</text>',
    ])

    svg.append('</svg>')
    return "\n".join(svg)
