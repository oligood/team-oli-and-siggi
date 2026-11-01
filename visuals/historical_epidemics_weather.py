"""
visuals/historical_epidemics_weather.py - Áföll, Náttúruhamfarir og Lýðfræðileg Áhrif

Inniheldur ítarleg söguleg gögn Hagstofu Íslands um meiriháttar náttúruhamfarir,
eldgos, hafísár, farsóttir og áhrif þeirra á mannfjölda og búfénað frá 1700 til 2026.
"""

from typing import Dict, List, Optional, Tuple

DISASTERS_AND_CRISES_DB = [
    {
        "year": 1707,
        "name": "Stórabóla",
        "type": "Farsótt (Bólusótt)",
        "casualties": "~18.000 manns (um þriðjungur þjóðarinnar)",
        "demographic_impact": "Mannfjöldi hrundi úr 50.358 niður í um 34.500.",
        "description": "Geisaði um allt land 1707-1709. Barst með fötum af manni sem andaðist á leið til landsins.",
        "icon": "💀",
        "color": "#E63946",
    },
    {
        "year": 1783,
        "name": "Skaftáreldar og Móðuharðindin",
        "type": "Eldgos og eiturgufur",
        "casualties": "~10.000 manns (um 20-25% þjóðarinnar)",
        "demographic_impact": "Mannfjöldi fór niður í 38.363 árið 1786. Um 80% sauðfjár og 50% nautgripa féllu.",
        "description": "Lakagígar gausu í 8 mánuði. Flúor- og brennisteinsmóða olli hungursneyð og beinkröm.",
        "icon": "🌋",
        "color": "#D62828",
    },
    {
        "year": 1882,
        "name": "Hafísárið mikla",
        "type": "Veðrátta og hafís",
        "casualties": "Aukin ungbarnadauði og fólksflótti",
        "demographic_impact": "Flýtti mjög fyrir Vesturferðum Íslendinga til Kanada og Bandaríkjanna.",
        "description": "Hafís lá við landið allt fram á sumar. Grasvöxtur brást og mikil harðindi herjuðu á sveitir.",
        "icon": "🧊",
        "color": "#457B9D",
    },
    {
        "year": 1918,
        "name": "Frostaveturinn mikli & Spænska veikin & Kötlugos",
        "type": "Náttúruhamfarir og farsótt",
        "casualties": "Um 500 manns létust úr spænsku veikinni (þar af ~250 í Reykjavík)",
        "demographic_impact": "Hæging á vexti þrátt fyrir fullveldisárið.",
        "description": "Frost fór niður í -38°C á Grímsstöðum. Kötlugos hófst í október og spænska veikin herjaði samtímis.",
        "icon": "❄️",
        "color": "#1D3557",
    },
    {
        "year": 1973,
        "name": "Heimaeyjargosið",
        "type": "Eldgos í byggð",
        "casualties": "1 maður (vegna gass)",
        "demographic_impact": "Öllum 5.300 íbúum Heimaeyjar var bjargað á land á örfáum klukkustundum.",
        "description": "Gos hófst án fyrirvara að næturlagi 23. janúar. Hraun og aska eyðilögðu um 400 hús.",
        "icon": "🌋",
        "color": "#F77F00",
    },
    {
        "year": 1995,
        "name": "Snjóflóðin á Súðavík og Flateyri",
        "type": "Náttúruvá",
        "casualties": "34 manns létust (14 á Súðavík, 20 á Flateyri)",
        "demographic_impact": "Súðavík var flutt og endurbyggð á öruggara svæði; varnargarðar reistir um land allt.",
        "description": "Stærstu snjóflóðaslys í nútímasögu landsins. Leiddu til byltingar í snjóflóðavörnum.",
        "icon": "🌨️",
        "color": "#2A9D8F",
    },
    {
        "year": 2010,
        "name": "Eyjafjallajökull",
        "type": "Eldgos og flugbann",
        "casualties": "Engin mannslát",
        "demographic_impact": "Upphaf hinnar miklu ferðamannasprengingar á Íslandi (fjölgun úr 480k í 2.3m).",
        "description": "Gos í toppgíg jökulsins olli víðtæku flugbanni í Evrópu í margar vikur.",
        "icon": "✈️",
        "color": "#E76F51",
    },
    {
        "year": 2020,
        "name": "COVID-19 Heimsfaraldurinn",
        "type": "Heimsfaraldur",
        "casualties": "~280 andlát skráð á Íslandi",
        "demographic_impact": "Atvinnuleysi fór tímabundið í 8-10%, ferðamennska hrundi tímabundið um 75%.",
        "description": "Víðtækar samkomutakmarkanir og sóttkvíarráðstafanir árin 2020-2022.",
        "icon": "🦠",
        "color": "#F4A261",
    },
    {
        "year": 2023,
        "name": "Jarðhræringar á Reykjanesskaga (Grindavík)",
        "type": "Eldgosahrina og kvikugangar",
        "casualties": "Engin bein mannslát af völdum hraunrennslis",
        "demographic_impact": "Rýming alls Grindavíkurbæjar (~3.800 manns) og endurdreifing íbúa um landið.",
        "description": "Sundhnúkagígar og Svartsengi gusu margítrekað á árunum 2023-2026.",
        "icon": "🔥",
        "color": "#E63946",
    },
]


def generate_crisis_timeline_svg(width: int = 760, height: int = 420) -> str:
    """Teiknar sögulegan áfallatímaás Íslands í SVG."""
    p_left, p_right, p_top, p_bottom = 50, 40, 50, 50
    g_w = width - p_left - p_right
    g_h = height - p_top - p_bottom

    min_yr, max_yr = 1700, 2026

    def xs(yr: int) -> float:
        return p_left + ((yr - min_yr) / (max_yr - min_yr)) * g_w

    svg = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: #1A2E40; border: 2px solid #C5A059; border-radius: 4px; width: 100%; height: auto;">',
        '<text x="25" y="30" font-family="Cinzel, Georgia, serif" font-size="13" font-weight="700" fill="#C5A059" letter-spacing="2">ÁFÖLL OG NÁTTÚRUHAMFARIR Í SÖGU ÍSLANDS (1700–2026)</text>',
        '<text x="25" y="44" font-family="Lora, serif" font-size="10" fill="#8FA5BC" font-style="italic">Lýðfræðileg áhrif meiriháttar farsótta, eldosa og harðinda</text>',
        # Meginás
        f'<line x1="{p_left}" y1="{height/2}" x2="{width - p_right}" y2="{height/2}" stroke="#C5A059" stroke-width="2" />',
    ]

    for yr in [1700, 1750, 1800, 1850, 1900, 1950, 2000, 2026]:
        xp = xs(yr)
        svg.append(f'<line x1="{xp:.1f}" y1="{height/2 - 8}" x2="{xp:.1f}" y2="{height/2 + 8}" stroke="#C5A059" stroke-width="1.5" />')
        svg.append(f'<text x="{xp:.1f}" y="{height/2 + 24}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="10" fill="#EAE3D6">{yr}</text>')

    for idx, c in enumerate(DISASTERS_AND_CRISES_DB):
        xp = xs(c["year"])
        is_above = (idx % 2 == 0)
        yp_node = (height/2 - 50) if is_above else (height/2 + 65)
        line_target = (height/2 - 6) if is_above else (height/2 + 6)

        col = c["color"]

        svg.append(f'<line x1="{xp:.1f}" y1="{line_target}" x2="{xp:.1f}" y2="{yp_node}" stroke="{col}" stroke-width="1.2" stroke-dasharray="2,2" />')
        svg.append(f'<circle cx="{xp:.1f}" cy="{yp_node}" r="5" fill="{col}" stroke="#FFFFFF" stroke-width="1" />')
        svg.append(
            f'<text x="{xp:.1f}" y="{yp_node + (-8 if is_above else 16)}" text-anchor="middle" '
            f'font-family="Lora, serif" font-size="9" font-weight="700" fill="{col}">'
            f'{c["year"]}: {c["name"][:16]}'
            f'</text>'
        )

    svg.append('</svg>')
    return "\n".join(svg)
