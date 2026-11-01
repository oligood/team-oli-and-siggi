"""Energy Transformation and Climate Historical Series.

Chronicles Iceland's monumental shift from coal, peat, and imported oil to geothermal
and hydroelectric dominance (1900–2026), alongside the historic Stykkishólmur
temperature series (1845–2026) — Iceland's longest continuous climate record.
Pure-Python vector SVG generation with classical Roman institutional styling.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple


# Primary Energy Consumption in Iceland (Petajoules, PJ)
# Source: Orkustofnun & Hagstofa Íslands historical energy accounts
ENERGY_CONSUMPTION_SERIES: List[Dict[str, any]] = [
    # Year, Geothermal, Hydro, Oil/Fossil, Coal/Peat, Total PJ
    {"year": 1940, "geothermal": 0.8,  "hydro": 0.5,  "oil": 4.2,  "coal": 3.8,  "total": 9.3},
    {"year": 1950, "geothermal": 2.1,  "hydro": 1.2,  "oil": 8.5,  "coal": 2.4,  "total": 14.2},
    {"year": 1960, "geothermal": 4.5,  "hydro": 2.8,  "oil": 14.1, "coal": 0.6,  "total": 22.0},
    {"year": 1970, "geothermal": 9.2,  "hydro": 5.4,  "oil": 23.8, "coal": 0.1,  "total": 38.5},
    {"year": 1980, "geothermal": 22.4, "hydro": 12.1, "oil": 27.2, "coal": 1.9,  "total": 63.6},
    {"year": 1990, "geothermal": 34.8, "hydro": 16.2, "oil": 28.5, "coal": 2.8,  "total": 82.3},
    {"year": 2000, "geothermal": 54.2, "hydro": 25.8, "oil": 32.1, "coal": 3.4,  "total": 115.5},
    {"year": 2010, "geothermal": 138.4,"hydro": 44.2, "oil": 29.8, "coal": 4.1,  "total": 216.5},
    {"year": 2020, "geothermal": 178.2,"hydro": 49.5, "oil": 26.4, "coal": 3.2,  "total": 257.3},
    {"year": 2026, "geothermal": 198.5,"hydro": 52.8, "oil": 24.1, "coal": 2.8,  "total": 278.2},
]

# Historical Hitaveita (District Heating) Expansion Milestones
DISTRICT_HEATING_MILESTONES: List[Dict[str, any]] = [
    {"year": 1908, "event": "Fyrsta hitaveitan", "details": "Stefán B. Jónsson leiðir heitt vatn úr Suðurreykjum í Mosfellssveit."},
    {"year": 1930, "event": "Hitaveita Reykjavíkur stofnuð", "details": "Vatn leitt úr Þvottalaugunum í Austurbæjarskóla, Sundhöllina og 60 hús."},
    {"year": 1943, "event": "Reykjalögnin tekin í gagnið", "details": "17 km lögn frá Reykjum í Mosfellssveit tengir meirihluta Reykjavíkur."},
    {"year": 1973, "event": "Olíukreppan mikla", "details": "Ríkisstjórnin ákveður allsherjar hitaveituvæðingu allra þéttbýlisstaða landsins."},
    {"year": 1990, "event": "Nesjavallavirkjun gangsett", "details": "Háhitavatn og raforka leidd til höfuðborgarsvæðisins frá Hengli."},
    {"year": 2006, "event": "Hellisheiðarvirkjun vígð", "details": "Ein stærsta jarðvarmavirkjun heims tekur til starfa."},
    {"year": 2026, "event": "90%+ jarðvarmahúshitun", "details": "Ísland hefur hæsta hlutfall endurnýjanlegrar húshitunar á heimsvísu."},
]

# Stykkishólmur continuous annual mean temperature series (°C, select historical anchors 1845–2026)
# Baseline 1961-1990 average for Stykkishólmur is approximately 3.5°C
STYKKISHOLMUR_TEMPERATURE_SERIES: List[Tuple[int, float]] = [
    (1846, 3.8),
    (1850, 3.2),
    (1859, 1.8),  # Extremely cold year
    (1866, 1.4),  # Fimbulvetur
    (1875, 2.7),  # Askja eruption year
    (1881, 1.1),  # One of coldest years on record (hafísár)
    (1890, 2.9),
    (1900, 3.1),
    (1910, 3.4),
    (1918, 1.9),  # Frostaveturinn mikli
    (1925, 4.2),
    (1930, 4.4),
    (1939, 4.9),  # Warm period pre-WWII
    (1945, 4.5),
    (1953, 5.1),  # Peak mid-century warm year
    (1960, 4.2),
    (1968, 2.3),  # Hafísárin / The Sea Ice Years
    (1975, 2.9),
    (1979, 2.4),  # Cold anomaly
    (1985, 3.5),
    (1990, 4.1),
    (1995, 3.3),
    (2000, 4.5),
    (2003, 5.2),
    (2010, 5.4),  # Modern warm peak
    (2014, 5.6),  # Warmest in 150 years
    (2018, 4.8),
    (2021, 4.9),
    (2024, 5.3),
    (2026, 5.2),
]


def generate_energy_transition_chart_svg(width: int = 760, height: int = 360) -> str:
    """Generate stacked area chart illustrating Iceland's transition from fossil to renewable energy."""
    margin_left = 60
    margin_right = 40
    margin_top = 45
    margin_bottom = 45
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    
    max_pj = 300.0  # Cap at 300 PJ for scaling
    n_pts = len(ENERGY_CONSUMPTION_SERIES)
    step_x = plot_w / (n_pts - 1)
    
    def pj_to_y(pj: float) -> float:
        return margin_top + plot_h - (pj / max_pj) * plot_h
        
    pts_geo = []
    pts_hydro = []
    pts_oil = []
    pts_coal = []
    
    for i, row in enumerate(ENERGY_CONSUMPTION_SERIES):
        x = margin_left + i * step_x
        # Stack: Geothermal -> Hydro -> Oil -> Coal
        c_geo = row["geothermal"]
        c_hydro = c_geo + row["hydro"]
        c_oil = c_hydro + row["oil"]
        c_coal = c_oil + row["coal"]
        
        pts_geo.append((x, pj_to_y(c_geo)))
        pts_hydro.append((x, pj_to_y(c_hydro)))
        pts_oil.append((x, pj_to_y(c_oil)))
        pts_coal.append((x, pj_to_y(c_coal)))
        
    bottom_y = margin_top + plot_h
    
    poly_geo = f"M {pts_geo[0][0]},{bottom_y} " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in pts_geo) + f" L {pts_geo[-1][0]},{bottom_y} Z"
    poly_hydro = (
        f"M {pts_geo[0][0]},{pts_geo[0][1]} " +
        " ".join(f"L {x:.1f},{y:.1f}" for x, y in pts_hydro) +
        " " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in reversed(pts_geo)) + " Z"
    )
    poly_oil = (
        f"M {pts_hydro[0][0]},{pts_hydro[0][1]} " +
        " ".join(f"L {x:.1f},{y:.1f}" for x, y in pts_oil) +
        " " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in reversed(pts_hydro)) + " Z"
    )
    poly_coal = (
        f"M {pts_oil[0][0]},{pts_oil[0][1]} " +
        " ".join(f"L {x:.1f},{y:.1f}" for x, y in pts_coal) +
        " " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in reversed(pts_oil)) + " Z"
    )

    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        '  <defs>',
        '    <linearGradient id="geoGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '      <stop offset="0%" stop-color="#e67e22"/><stop offset="100%" stop-color="#d35400"/>',
        '    </linearGradient>',
        '    <linearGradient id="hydroGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '      <stop offset="0%" stop-color="#3498db"/><stop offset="100%" stop-color="#2980b9"/>',
        '    </linearGradient>',
        '    <linearGradient id="oilGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '      <stop offset="0%" stop-color="#7f8c8d"/><stop offset="100%" stop-color="#566573"/>',
        '    </linearGradient>',
        '    <linearGradient id="coalGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '      <stop offset="0%" stop-color="#2c3e50"/><stop offset="100%" stop-color="#1a252f"/>',
        '    </linearGradient>',
        '  </defs>',
        f'  <rect width="{width}" height="{height}" rx="10" fill="#0c1424" stroke="#2a3854" stroke-width="1"/>',
        f'  <text x="{width/2}" y="25" text-anchor="middle" fill="#d4af37" font-family="Cinzel, serif" font-size="14" font-weight="bold">ORKUBYLTINGIN Á ÍSLANDI (1940–2026)</text>',
        f'  <text x="{width/2}" y="40" text-anchor="middle" fill="#8c9cb8" font-family="system-ui, sans-serif" font-size="10">Frumorkunotkun í Petajúlum (PJ) eftir orkugjöfum • Orkustofnun & Hagstofa Íslands</text>',
    ]
    
    # Grid lines
    for pj_val in [0, 50, 100, 150, 200, 250, 300]:
        y = pj_to_y(pj_val)
        svg.append(f'  <line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="#1e2c44" stroke-width="0.8"/>')
        svg.append(f'  <text x="{margin_left - 8}" y="{y + 3:.1f}" text-anchor="end" fill="#7182a0" font-family="Consolas, monospace" font-size="9">{pj_val} PJ</text>')
        
    # Render polygons
    svg.append(f'  <path d="{poly_geo}" fill="url(#geoGrad)" opacity="0.9"/>')
    svg.append(f'  <path d="{poly_hydro}" fill="url(#hydroGrad)" opacity="0.9"/>')
    svg.append(f'  <path d="{poly_oil}" fill="url(#oilGrad)" opacity="0.9"/>')
    svg.append(f'  <path d="{poly_coal}" fill="url(#coalGrad)" opacity="0.9"/>')
    
    # Year labels
    for i, row in enumerate(ENERGY_CONSUMPTION_SERIES):
        x = margin_left + i * step_x
        svg.append(f'  <line x1="{x:.1f}" y1="{bottom_y}" x2="{x:.1f}" y2="{bottom_y + 4}" stroke="#7182a0" stroke-width="1"/>')
        svg.append(f'  <text x="{x:.1f}" y="{bottom_y + 16}" text-anchor="middle" fill="#c5a059" font-family="Consolas, monospace" font-size="9">{row["year"]}</text>')
        
    # Legend
    leg_y = height - 12
    svg.append(f'  <rect x="{margin_left + 40}" y="{leg_y - 8}" width="12" height="8" rx="2" fill="#e67e22"/>')
    svg.append(f'  <text x="{margin_left + 56}" y="{leg_y}" fill="#d4af37" font-family="system-ui, sans-serif" font-size="9">Jarðvarmi (Geothermal)</text>')
    
    svg.append(f'  <rect x="{margin_left + 220}" y="{leg_y - 8}" width="12" height="8" rx="2" fill="#3498db"/>')
    svg.append(f'  <text x="{margin_left + 236}" y="{leg_y}" fill="#d4af37" font-family="system-ui, sans-serif" font-size="9">Vatnsafl (Hydro)</text>')
    
    svg.append(f'  <rect x="{margin_left + 380}" y="{leg_y - 8}" width="12" height="8" rx="2" fill="#7f8c8d"/>')
    svg.append(f'  <text x="{margin_left + 396}" y="{leg_y}" fill="#d4af37" font-family="system-ui, sans-serif" font-size="9">Jarðefnaeldsneyti / Olía</text>')
    
    svg.append(f'  <rect x="{margin_left + 540}" y="{leg_y - 8}" width="12" height="8" rx="2" fill="#2c3e50"/>')
    svg.append(f'  <text x="{margin_left + 556}" y="{leg_y}" fill="#d4af37" font-family="system-ui, sans-serif" font-size="9">Kol / Mór</text>')
    
    svg.append('</svg>')
    return "\n".join(svg)


def generate_climate_deviations_svg(width: int = 760, height: int = 340) -> str:
    """Generate bar chart of temperature anomalies relative to the 1961-1990 baseline (3.5°C) at Stykkishólmur."""
    margin_left = 60
    margin_right = 40
    margin_top = 45
    margin_bottom = 40
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    
    baseline = 3.5
    anomalies = [(yr, temp - baseline) for yr, temp in STYKKISHOLMUR_TEMPERATURE_SERIES]
    
    max_anom = 2.5
    min_anom = -2.5
    zero_y = margin_top + plot_h / 2
    scale_y = (plot_h / 2) / 2.5
    
    n_pts = len(anomalies)
    bar_width = (plot_w / n_pts) * 0.75
    
    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        '  <defs>',
        '    <linearGradient id="warmGrad" x1="0%" y1="100%" x2="0%" y2="0%">',
        '      <stop offset="0%" stop-color="#e67e22"/><stop offset="100%" stop-color="#e74c3c"/>',
        '    </linearGradient>',
        '    <linearGradient id="coldGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '      <stop offset="0%" stop-color="#3498db"/><stop offset="100%" stop-color="#2980b9"/>',
        '    </linearGradient>',
        '  </defs>',
        f'  <rect width="{width}" height="{height}" rx="10" fill="#0d1526" stroke="#25354e" stroke-width="1"/>',
        f'  <text x="{width/2}" y="24" text-anchor="middle" fill="#d4af37" font-family="Cinzel, serif" font-size="13" font-weight="bold">HITAFRÁVIK Í STYKKISHÓLMI (1846–2026)</text>',
        f'  <text x="{width/2}" y="38" text-anchor="middle" fill="#8c9cb8" font-family="system-ui, sans-serif" font-size="10">Frávik ársmeðalhita frá viðmiðunartímabilinu 1961–1990 (3,5°C) • Lengsta samfellda veðurathugunarröð Íslands</text>',
        f'  <line x1="{margin_left}" y1="{zero_y}" x2="{width - margin_right}" y2="{zero_y}" stroke="#c5a059" stroke-width="1.2"/>',
        f'  <text x="{margin_left - 8}" y="{zero_y + 3}" text-anchor="end" fill="#c5a059" font-family="Consolas, monospace" font-size="9">0,0°C</text>',
    ]
    
    # Grid lines for +1, +2, -1, -2
    for offset_deg in [1.0, 2.0, -1.0, -2.0]:
        y = zero_y - (offset_deg * scale_y)
        svg.append(f'  <line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="#1e2c42" stroke-width="0.8" stroke-dasharray="2,3"/>')
        prefix = "+" if offset_deg > 0 else ""
        svg.append(f'  <text x="{margin_left - 8}" y="{y + 3:.1f}" text-anchor="end" fill="#6d7f9c" font-family="Consolas, monospace" font-size="9">{prefix}{offset_deg:.1f}°C</text>')
        
    step_x = plot_w / n_pts
    for i, (yr, anom) in enumerate(anomalies):
        cx = margin_left + i * step_x + (step_x / 2)
        bx = cx - bar_width / 2
        
        if anom >= 0:
            by = zero_y - (anom * scale_y)
            bh = anom * scale_y
            fill = "url(#warmGrad)"
        else:
            by = zero_y
            bh = abs(anom) * scale_y
            fill = "url(#coldGrad)"
            
        svg.append(f'  <rect x="{bx:.1f}" y="{by:.1f}" width="{bar_width:.1f}" height="{max(1.0, bh):.1f}" rx="2" fill="{fill}"/>')
        
        # Periodic year tags
        if yr in [1850, 1881, 1918, 1939, 1968, 1990, 2014, 2026]:
            svg.append(f'  <line x1="{cx:.1f}" y1="{margin_top + plot_h}" x2="{cx:.1f}" y2="{margin_top + plot_h + 4}" stroke="#8c9cb8" stroke-width="1"/>')
            svg.append(f'  <text x="{cx:.1f}" y="{margin_top + plot_h + 16}" text-anchor="middle" fill="#c5a059" font-family="Consolas, monospace" font-size="9">{yr}</text>')
            
    svg.append('</svg>')
    return "\n".join(svg)


def render_energy_climate_ui(st_module) -> None:
    """Streamlit interactive UI for energy transformation and climate series."""
    st = st_module
    st.markdown("### ⚡ Orkubyltingin & Loftslagsmet (1845–2026)")
    st.markdown(
        "Frá mó- og kolanotkun 19. aldar til fremstu orkubyltingar heims. "
        "Ísland framleiðir nú um 100% alls rafmagns og húshitunar úr vatnsafli og jarðvarma."
    )
    
    st.markdown(generate_energy_transition_chart_svg(760, 360), unsafe_allow_html=True)
    
    st.markdown("#### Tímalína hitaveituvæðingar á Íslandi")
    cols = st.columns(len(DISTRICT_HEATING_MILESTONES))
    for idx, m in enumerate(DISTRICT_HEATING_MILESTONES):
        with cols[idx]:
            st.caption(f"**{m['year']}**")
            st.markdown(f"*{m['event']}*")
            
    st.markdown("---")
    st.markdown("#### Söguleg veðurathugunarröð Stykkishólms")
    st.markdown(generate_climate_deviations_svg(760, 340), unsafe_allow_html=True)
    st.info(
        "**Stykkishólmur (1845–2026):** Árni Thorlacius hóf reglulegar hitamælingar í Stykkishólmi í nóvember 1845. "
        "Röðin sýnir greinilega 'frostaveturinn mikla' 1918 (-1,6°C frávik), 'hafísárin' 1965–1971, "
        "og fordæmalausa samfellda hlýnun 21. aldarinnar þar sem ársmeðalhiti hefur reglulega farið yfir 5,0°C."
    )
