"""
visuals/charts_engine.py - Rómverskt Línuritakerfi og Tölfræðigreining

Byggir sérsniðin gagnvirk SVG-línurit með rómverskum stofnanastíl,
gullskreytingum og nákvæmum tímaraðagögnum frá Hagstofu Íslands.
"""

import math
from typing import Dict, List, Optional, Tuple

# Söguleg vísitala neysluverðs (janúar hvert ár 1980-2026, grunnur vísitölu = 100 árið 1988)
CPI_HISTORICAL_ANNUAL = [
    (1980, 0.45), (1981, 0.68), (1982, 1.04), (1983, 1.93), (1984, 2.50),
    (1985, 3.31), (1986, 4.02), (1987, 4.77), (1988, 5.98), (1989, 7.24),
    (1990, 8.31), (1991, 8.87), (1992, 9.20), (1993, 9.58), (1994, 9.73),
    (1995, 9.89), (1996, 10.12), (1997, 10.30), (1998, 10.53), (1999, 10.72),
    (2000, 11.26), (2001, 11.69), (2002, 12.79), (2003, 13.06), (2004, 13.37),
    (2005, 13.91), (2006, 14.52), (2007, 15.52), (2008, 16.42), (2009, 19.47),
    (2010, 20.75), (2011, 21.12), (2012, 22.48), (2013, 23.42), (2014, 24.15),
    (2015, 24.34), (2016, 24.85), (2017, 25.32), (2018, 25.90), (2019, 26.78),
    (2020, 27.24), (2021, 28.41), (2022, 30.04), (2023, 32.99), (2024, 35.21),
    (2025, 37.10), (2026, 38.65)
]

# Lykilatburðir í efnahagssögu Íslands
HISTORICAL_MILESTONES = [
    (1983, "Óðaverðbólga (~84%)", "#FF6B6B"),
    (1990, "Þjóðarsáttin", "#4ECDC4"),
    (1994, "EES-samningurinn", "#FFE66D"),
    (2001, "Verðbólgumarkmið", "#A8DADC"),
    (2008, "Bankahrunið", "#E63946"),
    (2020, "COVID-faraldurinn", "#F4A261"),
    (2022, "Verðbólguskot (9.9%)", "#E76F51"),
]

# Mannfjöldapýramídi 2026 (aldursbil, karlar, konur í þúsundum)
POPULATION_PYRAMID_2026 = [
    ("80+", 6.2, 8.4),
    ("75-79", 5.8, 6.3),
    ("70-74", 8.4, 8.8),
    ("65-69", 10.9, 10.8),
    ("60-64", 12.2, 12.0),
    ("55-59", 12.6, 12.3),
    ("50-54", 13.5, 13.1),
    ("45-49", 14.2, 13.8),
    ("40-44", 15.6, 14.9),
    ("35-39", 16.8, 15.7),
    ("30-34", 17.5, 16.2),
    ("25-29", 16.9, 15.4),
    ("20-24", 14.8, 13.9),
    ("15-19", 13.7, 13.0),
    ("10-14", 13.5, 12.8),
    ("5-9", 13.2, 12.4),
    ("0-4", 12.6, 11.9),
]

# Ferðamannastraumur um Keflavíkurflugvöll (árleg heild 2010-2025 í þúsundum)
TOURIST_ARRIVALS = [
    (2010, 488), (2011, 565), (2012, 672), (2013, 807), (2014, 997),
    (2015, 1289), (2016, 1792), (2017, 2224), (2018, 2344), (2019, 2013),
    (2020, 486), (2021, 688), (2022, 1696), (2023, 2224), (2024, 2310),
    (2025, 2380)
]


def generate_cpi_svg_chart(width: int = 760, height: int = 420) -> str:
    """Býr til ítarlegt SVG-línurit yfir vísitölu neysluverðs 1980-2026 með sögulegum atburðum."""
    padding_left = 65
    padding_right = 35
    padding_top = 45
    padding_bottom = 55

    graph_w = width - padding_left - padding_right
    graph_h = height - padding_top - padding_bottom

    years = [y for y, _ in CPI_HISTORICAL_ANNUAL]
    values = [v for _, v in CPI_HISTORICAL_ANNUAL]

    min_y, max_y = min(years), max(years)
    min_v, max_v = 0.0, max(values) * 1.05

    def x_scale(yr: int) -> float:
        return padding_left + ((yr - min_y) / (max_y - min_y)) * graph_w

    def y_scale(val: float) -> float:
        return padding_top + graph_h - ((val - min_v) / (max_v - min_v)) * graph_h

    # Reikna línuhnita-path
    points = [f"{x_scale(y):.1f},{y_scale(v):.1f}" for y, v in CPI_HISTORICAL_ANNUAL]
    line_path = "M " + " L ".join(points)
    area_path = f"{line_path} L {x_scale(max_y):.1f},{y_scale(0):.1f} L {x_scale(min_y):.1f},{y_scale(0):.1f} Z"

    svg_lines = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: #1A2E40; border: 2px solid #C5A059; border-radius: 4px; box-shadow: 0 4px 18px rgba(0,0,0,0.45); width: 100%; height: auto;">',
        '<defs>',
        '  <linearGradient id="cpiGoldGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '    <stop offset="0%" stop-color="#C5A059" stop-opacity="0.55" />',
        '    <stop offset="100%" stop-color="#C5A059" stop-opacity="0.02" />',
        '  </linearGradient>',
        '</defs>',
        # Rammi og titill
        f'<rect x="8" y="8" width="{width-16}" height="{height-16}" fill="none" stroke="#C5A059" stroke-width="1" stroke-dasharray="6,3" opacity="0.4" />',
        '<text x="25" y="30" font-family="Cinzel, Georgia, serif" font-size="13" font-weight="700" fill="#C5A059" letter-spacing="2">VÍSITALA NEYSLUVERÐS (1980–2026)</text>',
        '<text x="25" y="44" font-family="Lora, serif" font-size="10" fill="#8FA5BC" font-style="italic">Hagstofa Íslands &middot; Tafla VIS01002 (Verðlagsþróun)</text>',
    ]

    # Láréttar ristarlínur (Gridlines)
    grid_ticks = [0, 10, 20, 30, 40]
    for gt in grid_ticks:
        if gt <= max_v:
            y_pos = y_scale(gt)
            svg_lines.append(
                f'<line x1="{padding_left}" y1="{y_pos:.1f}" x2="{width - padding_right}" y2="{y_pos:.1f}" '
                f'stroke="#2A445E" stroke-width="1" stroke-dasharray="3,3" />'
            )
            svg_lines.append(
                f'<text x="{padding_left - 10}" y="{y_pos + 4:.1f}" text-anchor="end" '
                f'font-family="JetBrains Mono, monospace" font-size="10" fill="#8FA5BC">{gt}x</text>'
            )

    # Lóðréttar árstalslínur
    for yr in range(1980, 2027, 5):
        x_pos = x_scale(yr)
        svg_lines.append(
            f'<line x1="{x_pos:.1f}" y1="{padding_top}" x2="{x_pos:.1f}" y2="{padding_top + graph_h}" '
            f'stroke="#2A445E" stroke-width="1" stroke-dasharray="2,4" />'
        )
        svg_lines.append(
            f'<text x="{x_pos:.1f}" y="{padding_top + graph_h + 20}" text-anchor="middle" '
            f'font-family="JetBrains Mono, monospace" font-size="10" fill="#EAE3D6">{yr}</text>'
        )

    # Skyggt svæði og meginferill
    svg_lines.append(f'<path d="{area_path}" fill="url(#cpiGoldGrad)" />')
    svg_lines.append(
        f'<path d="{line_path}" fill="none" stroke="#FFD700" stroke-width="2.8" '
        f'stroke-linecap="round" stroke-linejoin="round" />'
    )

    # Sögulegir atburðir merktir inn
    for yr, event_label, col in HISTORICAL_MILESTONES:
        if min_y <= yr <= max_y:
            ex = x_scale(yr)
            val = next((v for y, v in CPI_HISTORICAL_ANNUAL if y == yr), 10.0)
            ey = y_scale(val)
            svg_lines.extend([
                f'<line x1="{ex:.1f}" y1="{padding_top}" x2="{ex:.1f}" y2="{padding_top + graph_h}" '
                f'stroke="{col}" stroke-width="1.2" stroke-dasharray="3,2" opacity="0.75" />',
                f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{col}" stroke="#FFFFFF" stroke-width="1" />',
                f'<text x="{ex:.1f}" y="{padding_top + 18}" text-anchor="middle" '
                f'font-family="Lora, serif" font-size="9" font-style="italic" fill="{col}">'
                f'{yr}: {event_label}'
                f'</text>',
            ])

    # Endapunktur (2026)
    last_x = x_scale(2026)
    last_y = y_scale(CPI_HISTORICAL_ANNUAL[-1][1])
    svg_lines.extend([
        f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="5.5" fill="#FFD700" stroke="#1A2E40" stroke-width="2" />',
        f'<text x="{last_x - 10:.1f}" y="{last_y - 12:.1f}" text-anchor="end" '
        f'font-family="JetBrains Mono, monospace" font-size="11" font-weight="700" fill="#FFD700">'
        f'2026: {CPI_HISTORICAL_ANNUAL[-1][1]:.1f}x'
        f'</text>',
    ])

    svg_lines.append('</svg>')
    return "\n".join(svg_lines)


def generate_population_pyramid_svg(width: int = 760, height: int = 460) -> str:
    """Býr til fullkominn mannfjöldapýramída fyrir Ísland (2026)."""
    padding_left = 60
    padding_right = 60
    padding_top = 50
    padding_bottom = 40

    center_x = width / 2
    max_bar_width = (width - padding_left - padding_right) / 2 - 40
    num_brackets = len(POPULATION_PYRAMID_2026)
    row_height = (height - padding_top - padding_bottom) / num_brackets

    max_count = 20.0  # Max þúsund í einum aldursflokki

    svg = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: #1A2E40; border: 2px solid #C5A059; border-radius: 4px; width: 100%; height: auto;">',
        '<text x="25" y="30" font-family="Cinzel, Georgia, serif" font-size="13" font-weight="700" fill="#C5A059" letter-spacing="2">MANNFJÖLDAPÝRAMÍDI ÍSLANDS 2026</text>',
        '<text x="25" y="44" font-family="Lora, serif" font-size="10" fill="#8FA5BC" font-style="italic">Tafla MAN00000 &middot; Aldurs- og kynjaskipting í þúsundum</text>',
        # Titlar á dálkum
        f'<text x="{center_x - 80}" y="65" text-anchor="end" font-family="Cinzel, serif" font-size="11" font-weight="700" fill="#8FA5BC">KARLAR (VIRES)</text>',
        f'<text x="{center_x + 80}" y="65" text-anchor="start" font-family="Cinzel, serif" font-size="11" font-weight="700" fill="#C5A059">KONUR (FEMINAE)</text>',
        f'<line x1="{center_x}" y1="70" x2="{center_x}" y2="{height - padding_bottom}" stroke="#C5A059" stroke-width="1.5" />',
    ]

    for idx, (bracket, males, females) in enumerate(POPULATION_PYRAMID_2026):
        y_pos = 75 + idx * row_height

        m_width = (males / max_count) * max_bar_width
        f_width = (females / max_count) * max_bar_width

        # Karlar (vinstra megin, blágrár)
        svg.append(
            f'<rect x="{center_x - 30 - m_width:.1f}" y="{y_pos:.1f}" width="{m_width:.1f}" '
            f'height="{row_height - 3:.1f}" fill="#4A6572" rx="1" />'
        )
        svg.append(
            f'<text x="{center_x - 35 - m_width:.1f}" y="{y_pos + row_height - 6:.1f}" text-anchor="end" '
            f'font-family="JetBrains Mono, monospace" font-size="9" fill="#8FA5BC">{males:.1f}k</text>'
        )

        # Aldursflokkur (miðja)
        svg.append(
            f'<text x="{center_x}" y="{y_pos + row_height - 6:.1f}" text-anchor="middle" '
            f'font-family="Lora, serif" font-size="10" font-weight="600" fill="#EAE3D6">{bracket}</text>'
        )

        # Konur (hægra megin, gullgult)
        svg.append(
            f'<rect x="{center_x + 30:.1f}" y="{y_pos:.1f}" width="{f_width:.1f}" '
            f'height="{row_height - 3:.1f}" fill="#C5A059" rx="1" />'
        )
        svg.append(
            f'<text x="{center_x + 35 + f_width:.1f}" y="{y_pos + row_height - 6:.1f}" text-anchor="start" '
            f'font-family="JetBrains Mono, monospace" font-size="9" fill="#FFD700">{females:.1f}k</text>'
        )

    svg.append('</svg>')
    return "\n".join(svg)


def generate_tourist_arrivals_chart(width: int = 760, height: int = 380) -> str:
    """Súlurit yfir erlenda ferðamenn um Keflavíkurflugvöll (2010-2025)."""
    padding_l, padding_r, padding_t, padding_b = 60, 30, 45, 55
    g_w = width - padding_l - padding_r
    g_h = height - padding_t - padding_b

    max_t = 2600.0  # Max 2.6 milljónir
    num_years = len(TOURIST_ARRIVALS)
    bar_width = (g_w / num_years) * 0.75
    gap = (g_w / num_years) * 0.25

    svg = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: #1A2E40; border: 2px solid #C5A059; border-radius: 4px; width: 100%; height: auto;">',
        '<text x="25" y="30" font-family="Cinzel, Georgia, serif" font-size="13" font-weight="700" fill="#C5A059" letter-spacing="2">ERLENDIR FERÐAMENN UM KEFLAVÍKURFLUGVÖLL</text>',
        '<text x="25" y="44" font-family="Lora, serif" font-size="10" fill="#8FA5BC" font-style="italic">Tafla SAM02001 &middot; Fjöldi í þúsundum á ári</text>',
    ]

    for idx, (yr, arrivals) in enumerate(TOURIST_ARRIVALS):
        bx = padding_l + idx * (bar_width + gap)
        bh = (arrivals / max_t) * g_h
        by = padding_t + g_h - bh

        # Litur eftir tímabili (lágt á Covid)
        col = "#E63946" if yr in (2020, 2021) else "#C5A059"
        if yr >= 2024:
            col = "#FFD700"

        svg.append(
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_width:.1f}" height="{bh:.1f}" '
            f'fill="{col}" rx="2" stroke="#1A2E40" />'
        )
        svg.append(
            f'<text x="{bx + bar_width/2:.1f}" y="{by - 6:.1f}" text-anchor="middle" '
            f'font-family="JetBrains Mono, monospace" font-size="8" fill="#FFFFFF">{arrivals}</text>'
        )
        svg.append(
            f'<text x="{bx + bar_width/2:.1f}" y="{padding_t + g_h + 18:.1f}" text-anchor="middle" '
            f'font-family="JetBrains Mono, monospace" font-size="9" fill="#EAE3D6" transform="rotate(-30 {bx+bar_width/2} {padding_t+g_h+18})">'
            f'{str(yr)[-2:]}\''
            f'</text>'
        )

    svg.append('</svg>')
    return "\n".join(svg)
