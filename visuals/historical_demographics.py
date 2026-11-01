"""
visuals/historical_demographics.py - Söguleg Lýðfræði Íslands (1703–2026)

Geymir heildstæða lýðfræðisögu Íslands frá fyrsta heildstæða manntali heims (1703)
til dagsins í dag, ásamt áhrifum farsótta, Móðuharðinda, Vesturferða og lýðveldisstofnunar.
"""

from typing import Dict, List, Optional, Tuple

# Heildarmannfjöldi Íslands frá 1703 til 2026 (valin söguleg tímamót úr töflu MAN00000)
CENSUS_HISTORICAL = [
    (1703, 50358, "Manntalið 1703 (Árni Magnússon & Páll Vídalín - fyrsta heildstæða manntal sögunnar)"),
    (1709, 34500, "Stórabóla (farsótt sem felldi um þriðjung þjóðarinnar)"),
    (1734, 43000, "Jafn vöxtur eftir bólusótt"),
    (1769, 46200, "Fólki fjölgar hægt vegna harðinda"),
    (1786, 38363, "Móðuharðindin (Skaftáreldar 1783-1785; hungursneyð og flúorforgiftun)"),
    (1801, 47240, "Manntalið 1801"),
    (1820, 48500, "Kyrrstaða í fólksfjölda"),
    (1840, 57079, "Bætt lýðheilsa og fólksfjölgun hefst"),
    (1860, 66987, "Þilskipaöld hefst og þéttbýlismyndun við sjávarsíðuna"),
    (1880, 72445, "Upphaf Vesturferðanna (1870-1914 fluttu um 15.000-20.000 til Norður-Ameríku)"),
    (1890, 70927, "Fólksfækkun vegna mikilla vesturferða og harðindavetra"),
    (1901, 78470, "Fyrsta manntal 20. aldar"),
    (1910, 85183, "Vélbátaútgerð og togarar hefja innreið sína"),
    (1918, 91800, "Fullveldi Íslands & Spænska veikin & Kötlugos"),
    (1920, 94690, "Endurreisn eftir fyrri heimsstyrjöld"),
    (1930, 108861, "Íbúar fara yfir 100.000 í fyrsta sinn"),
    (1940, 121474, "Hernám Íslands í seinni heimsstyrjöld"),
    (1944, 127770, "Lýðveldisstofnun á Þingvöllum 17. júní"),
    (1950, 143973, "Eftirstríðsárin og Marshall-aðstoðin"),
    (1960, 175680, "Mikil fólksfjölgun og nýbyggingahverfi í Reykjavík"),
    (1970, 204578, "Íbúafjöldi fer yfir 200.000"),
    (1980, 226948, "Áratugur mikillar verðbólgu en stöðugrar fólksfjölgunar"),
    (1990, 253785, "Þjóðarsáttarsamningurinn og ný efnahagsstefna"),
    (2000, 279049, "Aldamótaárið - upphaf aukins aðflutnings erlendra ríkisborgara"),
    (2010, 317630, "Áhrif bankahrunsins 2008 og tímabundinn brottflutningur"),
    (2020, 364134, "Fjölgun vegna atvinnutækifæra og ferðaþjónustu"),
    (2024, 383726, "Metfjölgun íbúa á einu ári"),
    (2026, 394324, "Nýjasta staðfesta mæling Hagstofu Íslands"),
]

# Lífslíkur við fæðingu (ár á Íslandi)
LIFE_EXPECTANCY_HISTORICAL = [
    (1850, 32.0, 38.0),
    (1880, 36.5, 41.2),
    (1900, 44.4, 51.4),
    (1920, 56.2, 60.3),
    (1940, 66.1, 70.3),
    (1960, 70.7, 75.0),
    (1980, 73.7, 79.7),
    (2000, 77.6, 81.4),
    (2020, 81.7, 84.5),
    (2026, 82.4, 85.1),
]

# Frjósemi (meðalfjöldi barna á konu)
FERTILITY_RATE_HISTORICAL = [
    (1880, 4.8), (1900, 4.3), (1920, 4.1), (1940, 3.2), (1950, 3.9),
    (1960, 4.2), (1970, 2.8), (1980, 2.5), (1990, 2.3), (2000, 2.1),
    (2010, 2.2), (2020, 1.7), (2024, 1.6), (2026, 1.55),
]


def generate_historical_population_svg(width: int = 760, height: int = 420) -> str:
    """Teiknar sögulegan feril mannfjölda Íslands frá 1703 til 2026 í SVG."""
    p_left, p_right, p_top, p_bottom = 65, 35, 45, 55
    g_w = width - p_left - p_right
    g_h = height - p_top - p_bottom

    min_y, max_y = 1703, 2026
    min_pop, max_pop = 25000, 420000

    def x_scale(yr: int) -> float:
        return p_left + ((yr - min_y) / (max_y - min_y)) * g_w

    def y_scale(pop: int) -> float:
        return p_top + g_h - ((pop - min_pop) / (max_pop - min_pop)) * g_h

    points = [f"{x_scale(y):.1f},{y_scale(p):.1f}" for y, p, _ in CENSUS_HISTORICAL]
    line_path = "M " + " L ".join(points)
    area_path = f"{line_path} L {x_scale(max_y):.1f},{y_scale(min_pop):.1f} L {x_scale(min_y):.1f},{y_scale(min_pop):.1f} Z"

    svg = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: #1A2E40; border: 2px solid #C5A059; border-radius: 4px; width: 100%; height: auto;">',
        '<defs>',
        '  <linearGradient id="popHistGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '    <stop offset="0%" stop-color="#FFD700" stop-opacity="0.5" />',
        '    <stop offset="100%" stop-color="#C5A059" stop-opacity="0.05" />',
        '  </linearGradient>',
        '</defs>',
        '<text x="25" y="30" font-family="Cinzel, Georgia, serif" font-size="13" font-weight="700" fill="#C5A059" letter-spacing="2">MANNFJÖLDI ÍSLANDS FRÁ 1703 TIL 2026</text>',
        '<text x="25" y="44" font-family="Lora, serif" font-size="10" fill="#8FA5BC" font-style="italic">Söguleg gögn Hagstofu Íslands frá fyrsta heildstæða manntali heims</text>',
    ]

    # Gridlines
    for tick_pop in [50000, 100000, 200000, 300000, 400000]:
        yp = y_scale(tick_pop)
        svg.append(
            f'<line x1="{p_left}" y1="{yp:.1f}" x2="{width - p_right}" y2="{yp:.1f}" '
            f'stroke="#2A445E" stroke-width="1" stroke-dasharray="2,3" />'
        )
        svg.append(
            f'<text x="{p_left - 10}" y="{yp + 4:.1f}" text-anchor="end" '
            f'font-family="JetBrains Mono, monospace" font-size="10" fill="#8FA5BC">{tick_pop:,}</text>'
        )

    # Year marks
    for yr in [1703, 1750, 1800, 1850, 1900, 1950, 2000, 2026]:
        xp = x_scale(yr)
        svg.append(
            f'<line x1="{xp:.1f}" y1="{p_top}" x2="{xp:.1f}" y2="{p_top + g_h}" '
            f'stroke="#2A445E" stroke-width="1" stroke-dasharray="2,4" />'
        )
        svg.append(
            f'<text x="{xp:.1f}" y="{p_top + g_h + 18}" text-anchor="middle" '
            f'font-family="JetBrains Mono, monospace" font-size="10" fill="#EAE3D6">{yr}</text>'
        )

    # Shaded curve
    svg.append(f'<path d="{area_path}" fill="url(#popHistGrad)" />')
    svg.append(f'<path d="{line_path}" fill="none" stroke="#FFD700" stroke-width="2.5" />')

    # Lykilatburðir á línuriti
    key_events = [
        (1709, "Stórabóla", "#FF6B6B"),
        (1786, "Móðuharðindin", "#E63946"),
        (1918, "Fullveldi", "#4ECDC4"),
        (1944, "Lýðveldið", "#FFE66D"),
        (2026, "394.324", "#FFD700"),
    ]

    for yr, lbl, col in key_events:
        item = next((p for y, p, _ in CENSUS_HISTORICAL if y == yr), None)
        if item:
            cx, cy = x_scale(yr), y_scale(item)
            svg.extend([
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="{col}" stroke="#1A2E40" stroke-width="1.5" />',
                f'<text x="{cx:.1f}" y="{cy - 8:.1f}" text-anchor="middle" '
                f'font-family="Lora, serif" font-size="9" font-weight="600" fill="{col}">{lbl}</text>',
            ])

    svg.append('</svg>')
    return "\n".join(svg)


def render_historical_timeline_html() -> str:
    """Skilar ítarlegum sögulegum tímaás á HTML formi."""
    items_html = ""
    for yr, pop, desc in CENSUS_HISTORICAL:
        items_html += f"""
<div style="display: flex; margin-bottom: 1rem; border-left: 2px solid #C5A059; padding-left: 1rem; position: relative;">
    <div style="width: 10px; height: 10px; background: #FFD700; border-radius: 50%;
                position: absolute; left: -6px; top: 5px; border: 1px solid #1A2E40;"></div>
    <div style="min-width: 60px; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #C5A059;">
        {yr}
    </div>
    <div style="min-width: 90px; font-family: 'JetBrains Mono', monospace; color: #FFD700;">
        {pop:,}
    </div>
    <div style="font-family: 'Lora', serif; font-size: 0.95rem; color: #1A2530;">
        {desc}
    </div>
</div>
"""
    return f"""
<div style="background: #EDE8E1; border: 1px solid #C5A059; border-radius: 4px; padding: 1.5rem; max-height: 480px; overflow-y: auto;">
    <div style="font-family: 'Cinzel', serif; font-size: 0.8rem; font-weight: 700; color: #8B6914; letter-spacing: 0.2em; margin-bottom: 1rem;">
        TÍMAÁS MANNFJÖLDAFRÆÐA ÍSLANDS (1703–2026)
    </div>
    {items_html}
</div>
"""
