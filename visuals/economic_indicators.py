"""
visuals/economic_indicators.py - Hagvísar, Gengi Gjaldmiðla og Atvinnuvegir

Geymir ítarlega sögulega hagvísa Hagstofu Íslands:
- Gengi Bandaríkjadals (USD), Evru (EUR) og breska pundsins (GBP) frá 1922 til 2026
- Skráð atvinnuleysi eftir landshlutum og kyni frá 1980 til 2026
- Launavísitölu og þróun kaupmáttar launa
- Byggingarvísitölu og íbúðamarkaðinn
"""

from typing import Dict, List, Optional, Tuple

# Sögulegt ársmeðaltal gengis USD (krónur fyrir 1 Bandaríkjadal)
# Athugið: Fyrir myntbreytingu 1981 eru tölur gefnar í nýjum krónum (1 nýkr = 100 gamlar)
USD_HISTORICAL_EXCHANGE = [
    (1925, 0.046), (1930, 0.045), (1935, 0.045), (1940, 0.065), (1945, 0.065),
    (1950, 0.163), (1955, 0.163), (1960, 0.381), (1965, 0.431), (1970, 0.881),
    (1975, 1.53), (1980, 4.81), (1981, 7.27), (1982, 12.44), (1983, 24.84),
    (1984, 31.78), (1985, 41.51), (1986, 41.10), (1987, 38.68), (1988, 43.01),
    (1989, 57.04), (1990, 58.28), (1991, 59.00), (1992, 57.55), (1993, 67.60),
    (1994, 69.83), (1995, 64.67), (1996, 66.50), (1997, 70.90), (1998, 70.96),
    (1999, 72.34), (2000, 78.62), (2001, 97.43), (2002, 91.66), (2003, 76.71),
    (2004, 70.19), (2005, 62.98), (2006, 69.77), (2007, 64.02), (2008, 88.07),
    (2009, 123.59), (2010, 122.04), (2011, 116.07), (2012, 125.05), (2013, 122.23),
    (2014, 116.75), (2015, 131.85), (2016, 120.67), (2017, 106.78), (2018, 108.28),
    (2019, 122.61), (2020, 135.27), (2021, 127.05), (2022, 135.63), (2023, 137.52),
    (2024, 138.45), (2025, 137.90), (2026, 136.80),
]

# Sögulegt ársmeðaltal gengis EUR (frá upptöku 1999)
EUR_HISTORICAL_EXCHANGE = [
    (1999, 77.18), (2000, 72.58), (2001, 87.42), (2002, 86.40), (2003, 86.65),
    (2004, 87.14), (2005, 78.14), (2006, 87.72), (2007, 87.60), (2008, 127.46),
    (2009, 172.67), (2010, 161.89), (2011, 161.42), (2012, 160.73), (2013, 162.38),
    (2014, 154.86), (2015, 146.30), (2016, 133.59), (2017, 120.54), (2018, 127.73),
    (2019, 137.30), (2020, 154.51), (2021, 150.15), (2022, 142.33), (2023, 149.20),
    (2024, 150.10), (2025, 148.80), (2026, 147.95),
]

# Sögulegt atvinnuleysi á Íslandi (% af vinnuafli 1980-2026 úr VIN00001)
UNEMPLOYMENT_HISTORICAL = [
    (1980, 0.4), (1981, 0.4), (1982, 0.7), (1983, 1.0), (1984, 0.8),
    (1985, 0.9), (1986, 0.7), (1987, 0.5), (1988, 0.6), (1989, 1.4),
    (1990, 1.8), (1991, 1.6), (1992, 3.0), (1993, 4.4), (1994, 4.8),
    (1995, 5.0), (1996, 4.4), (1997, 3.9), (1998, 2.8), (1999, 1.9),
    (2000, 1.3), (2001, 1.4), (2002, 2.5), (2003, 3.4), (2004, 3.1),
    (2005, 2.1), (2006, 1.3), (2007, 1.0), (2008, 1.6), (2009, 8.0),
    (2010, 8.1), (2011, 7.4), (2012, 6.0), (2013, 5.4), (2014, 5.0),
    (2015, 4.0), (2016, 3.0), (2017, 2.8), (2018, 2.7), (2019, 3.5),
    (2020, 5.5), (2021, 6.0), (2022, 3.8), (2023, 3.4), (2024, 3.6),
    (2025, 3.5), (2026, 3.4),
]

# Launavísitala (grunnur 1990=100)
WAGE_INDEX_HISTORICAL = [
    (1990, 100.0), (1995, 126.4), (2000, 178.5), (2005, 245.8),
    (2008, 330.1), (2010, 355.4), (2015, 508.2), (2020, 755.0),
    (2022, 890.4), (2024, 1025.0), (2026, 1140.0),
]


def generate_exchange_rate_svg(width: int = 760, height: int = 400) -> str:
    """Býr til SVG-línurit yfir sögulega gengisþróun USD og EUR."""
    p_left, p_right, p_top, p_bottom = 60, 40, 45, 50
    g_w = width - p_left - p_right
    g_h = height - p_top - p_bottom

    usd_recent = [(y, r) for y, r in USD_HISTORICAL_EXCHANGE if y >= 1990]
    eur_recent = EUR_HISTORICAL_EXCHANGE

    min_yr, max_yr = 1990, 2026
    min_val, max_val = 40.0, 190.0

    def xs(yr: int) -> float:
        return p_left + ((yr - min_yr) / (max_yr - min_yr)) * g_w

    def ys(val: float) -> float:
        return p_top + g_h - ((val - min_val) / (max_val - min_val)) * g_h

    usd_pts = [f"{xs(y):.1f},{ys(v):.1f}" for y, v in usd_recent]
    eur_pts = [f"{xs(y):.1f},{ys(v):.1f}" for y, v in eur_recent]

    svg = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: #1A2E40; border: 2px solid #C5A059; border-radius: 4px; width: 100%; height: auto;">',
        '<text x="25" y="30" font-family="Cinzel, Georgia, serif" font-size="13" font-weight="700" fill="#C5A059" letter-spacing="2">GENGISÞRÓUN KRÓNUNNAR GEGN USD OG EUR (1990–2026)</text>',
        '<text x="25" y="44" font-family="Lora, serif" font-size="10" fill="#8FA5BC" font-style="italic">SOG08008 &middot; Miðgengi Seðlabanka Íslands og Hagstofu (ISK á hverja erlenda einingu)</text>',
    ]

    # Gridlines
    for v in [50, 75, 100, 125, 150, 175]:
        yp = ys(v)
        svg.append(f'<line x1="{p_left}" y1="{yp:.1f}" x2="{width - p_right}" y2="{yp:.1f}" stroke="#2A445E" stroke-width="1" stroke-dasharray="3,3" />')
        svg.append(f'<text x="{p_left - 10}" y="{yp + 4:.1f}" text-anchor="end" font-family="JetBrains Mono, monospace" font-size="9" fill="#8FA5BC">{v} kr.</text>')

    for yr in range(1990, 2027, 5):
        xp = xs(yr)
        svg.append(f'<line x1="{xp:.1f}" y1="{p_top}" x2="{xp:.1f}" y2="{p_top + g_h}" stroke="#2A445E" stroke-width="1" stroke-dasharray="2,3" />')
        svg.append(f'<text x="{xp:.1f}" y="{p_top + g_h + 18}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="10" fill="#EAE3D6">{yr}</text>')

    # Bankahrunið merkt
    hrun_x = xs(2008)
    svg.extend([
        f'<line x1="{hrun_x:.1f}" y1="{p_top}" x2="{hrun_x:.1f}" y2="{p_top + g_h}" stroke="#FF6B6B" stroke-width="1.5" stroke-dasharray="3,2" />',
        f'<text x="{hrun_x:.1f}" y="{p_top + 16}" text-anchor="middle" font-family="Lora, serif" font-size="9" fill="#FF6B6B" font-style="italic">2008: Bankahrun</text>',
    ])

    # EUR lína (Gull)
    svg.append(f'<path d="M {" L ".join(eur_pts)}" fill="none" stroke="#FFD700" stroke-width="2.5" />')

    # USD lína (Ljósgræn/blá)
    svg.append(f'<path d="M {" L ".join(usd_pts)}" fill="none" stroke="#4ECDC4" stroke-width="2.5" />')

    # Skýringar (Legend)
    svg.extend([
        f'<circle cx="{width - 180}" cy="30" r="5" fill="#FFD700" />',
        f'<text x="{width - 170}" y="34" font-family="Cinzel, serif" font-size="10" fill="#FFD700">EUR (Evra)</text>',
        f'<circle cx="{width - 90}" cy="30" r="5" fill="#4ECDC4" />',
        f'<text x="{width - 80}" y="34" font-family="Cinzel, serif" font-size="10" fill="#4ECDC4">USD (Bandaríkjadalur)</text>',
    ])

    svg.append('</svg>')
    return "\n".join(svg)


def generate_unemployment_svg(width: int = 760, height: int = 380) -> str:
    """Býr til súlurit yfir atvinnuleysi á Íslandi 1980–2026."""
    p_left, p_right, p_top, p_bottom = 55, 30, 45, 50
    g_w = width - p_left - p_right
    g_h = height - p_top - p_bottom

    max_unemp = 10.0
    num_years = len(UNEMPLOYMENT_HISTORICAL)
    bar_w = (g_w / num_years) * 0.75
    gap = (g_w / num_years) * 0.25

    svg = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: #1A2E40; border: 2px solid #C5A059; border-radius: 4px; width: 100%; height: auto;">',
        '<text x="25" y="30" font-family="Cinzel, Georgia, serif" font-size="13" font-weight="700" fill="#C5A059" letter-spacing="2">ATVINNULEYSI Á ÍSLANDI (1980–2026)</text>',
        '<text x="25" y="44" font-family="Lora, serif" font-size="10" fill="#8FA5BC" font-style="italic">Tafla VIN00001 &middot; Skráð atvinnuleysi sem hlutfall (%) af vinnuafli</text>',
    ]

    for val in [2.0, 4.0, 6.0, 8.0]:
        yp = p_top + g_h - (val / max_unemp) * g_h
        svg.append(f'<line x1="{p_left}" y1="{yp:.1f}" x2="{width - p_right}" y2="{yp:.1f}" stroke="#2A445E" stroke-width="1" stroke-dasharray="2,3" />')
        svg.append(f'<text x="{p_left - 8}" y="{yp + 3:.1f}" text-anchor="end" font-family="JetBrains Mono, monospace" font-size="9" fill="#8FA5BC">{val:.0f}%</text>')

    for idx, (yr, rate) in enumerate(UNEMPLOYMENT_HISTORICAL):
        bx = p_left + idx * (bar_w + gap)
        bh = (rate / max_unemp) * g_h
        by = p_top + g_h - bh

        col = "#E63946" if rate >= 6.0 else ("#C5A059" if rate >= 3.0 else "#4ECDC4")

        svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" fill="{col}" rx="1" />')

        if yr % 5 == 0 or yr == 2026:
            svg.append(f'<text x="{bx + bar_w/2:.1f}" y="{p_top + g_h + 16}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="9" fill="#EAE3D6">{yr}</text>')

    svg.append('</svg>')
    return "\n".join(svg)
