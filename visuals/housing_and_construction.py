"""Historical Housing, Construction and Real Estate Economics.

Analyzes Iceland's housing stock evolution from 1900 turf houses to 2026 modern structures,
real estate price indices, homeownership dynamics, and mortgage mathematics.
Pure-Python vector SVG generation with classical Roman institutional styling.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple


# Historical building materials breakdown in Iceland (approximate % of total residential stock)
# Based on Hagstofa Íslands historical censuses (1901, 1920, 1940, 1960, 1980, 2000, 2024)
HOUSING_MATERIALS_HISTORY: List[Dict[str, any]] = [
    {"year": 1901, "turf": 62.4, "timber": 33.1, "concrete": 3.8, "other": 0.7, "total_dwellings": 13400},
    {"year": 1910, "turf": 45.2, "timber": 42.6, "concrete": 11.2, "other": 1.0, "total_dwellings": 16200},
    {"year": 1920, "turf": 28.5, "timber": 48.1, "concrete": 22.4, "other": 1.0, "total_dwellings": 19800},
    {"year": 1930, "turf": 14.1, "timber": 41.5, "concrete": 43.6, "other": 0.8, "total_dwellings": 24500},
    {"year": 1940, "turf": 5.8,  "timber": 32.2, "concrete": 61.2, "other": 0.8, "total_dwellings": 29800},
    {"year": 1950, "turf": 1.9,  "timber": 23.4, "concrete": 74.1, "other": 0.6, "total_dwellings": 36700},
    {"year": 1960, "turf": 0.5,  "timber": 17.5, "concrete": 81.4, "other": 0.6, "total_dwellings": 46200},
    {"year": 1970, "turf": 0.1,  "timber": 13.8, "concrete": 85.6, "other": 0.5, "total_dwellings": 58300},
    {"year": 1980, "turf": 0.0,  "timber": 11.2, "concrete": 88.2, "other": 0.6, "total_dwellings": 74900},
    {"year": 1990, "turf": 0.0,  "timber": 9.4,  "concrete": 89.8, "other": 0.8, "total_dwellings": 96100},
    {"year": 2000, "turf": 0.0,  "timber": 8.7,  "concrete": 90.1, "other": 1.2, "total_dwellings": 115200},
    {"year": 2010, "turf": 0.0,  "timber": 9.2,  "concrete": 88.9, "other": 1.9, "total_dwellings": 131800},
    {"year": 2020, "turf": 0.0,  "timber": 11.5, "concrete": 85.8, "other": 2.7, "total_dwellings": 148500},
    {"year": 2026, "turf": 0.0,  "timber": 13.2, "concrete": 83.1, "other": 3.7, "total_dwellings": 164200},
]

# Historical Greater Reykjavík real estate price index (Base 100 = Jan 2000)
# Deflated by Consumer Price Index (CPI) to reflect real purchasing power
REAL_HOUSING_PRICE_SERIES: List[Tuple[int, float, float]] = [
    # Year, Nominal Index, Real Index (inflation adjusted)
    (1994, 61.2, 79.5),
    (1996, 64.8, 81.2),
    (1998, 76.5, 92.4),
    (2000, 100.0, 100.0),
    (2002, 114.2, 103.1),
    (2004, 148.5, 127.4),
    (2005, 192.4, 158.2),
    (2006, 224.8, 172.5),
    (2007, 252.1, 183.9),  # Pre-crash peak
    (2008, 258.4, 166.1),
    (2009, 233.1, 133.8),
    (2010, 226.4, 122.9),  # Post-crash trough in real terms
    (2012, 245.8, 123.5),
    (2014, 276.2, 133.4),
    (2016, 335.6, 156.9),
    (2018, 421.3, 186.2),
    (2020, 468.9, 197.8),
    (2021, 545.2, 219.4),
    (2022, 665.4, 244.6),  # Post-pandemic real estate surge
    (2023, 715.8, 241.2),
    (2024, 782.3, 248.5),
    (2025, 845.0, 254.1),
    (2026, 898.5, 259.8),
]

# Homeownership rates across historical decades (%)
HOMEOWNERSHIP_DYNAMICS: List[Dict[str, any]] = [
    {"decade": "1960", "rate": 81.5, "context": "Uppbygging verkamannabústaða og sjálfseignarstefna"},
    {"decade": "1970", "rate": 83.2, "context": "Hröð verðbólga ýtti fólki í fasteignakaup"},
    {"decade": "1980", "rate": 82.0, "context": "Húsnæðisstofnun ríkisins og verðtrygging lánsforma"},
    {"decade": "1990", "rate": 80.5, "context": "Stöðugleikatímabil Þjóðarsáttar"},
    {"decade": "2000", "rate": 82.8, "context": "Íbúðalánasjóður og bankalán 90-100% veðsetning"},
    {"decade": "2010", "rate": 74.2, "context": "Eftirmálar fjármálahruns, fjölgun leigjenda"},
    {"decade": "2020", "rate": 72.8, "context": "Hár inngönguþröskuldur ungs fólks, hlutdeildarlán kynnt"},
    {"decade": "2026", "rate": 74.1, "context": "Aukin uppbygging og stuðningsúrræði fyrstu kaupenda"},
]


def calculate_mortgage_schedule(
    principal_isk: float,
    annual_interest_rate_pct: float,
    years: int,
    is_annuity: bool = True,
    expected_annual_inflation_pct: float = 0.0,
) -> Dict[str, any]:
    """Calculate detailed loan repayment schedule under Icelandic mortgage conventions."""
    months = years * 12
    monthly_nominal_rate = (annual_interest_rate_pct / 100.0) / 12.0
    monthly_inflation = (expected_annual_inflation_pct / 100.0) / 12.0
    
    current_principal = principal_isk
    total_paid = 0.0
    total_interest_paid = 0.0
    total_indexation_paid = 0.0
    
    first_month_payment = 0.0
    last_month_payment = 0.0
    
    if is_annuity:
        if monthly_nominal_rate > 0:
            base_annuity_factor = (monthly_nominal_rate * (1 + monthly_nominal_rate)**months) / (
                (1 + monthly_nominal_rate)**months - 1
            )
        else:
            base_annuity_factor = 1.0 / months
            
    for m in range(1, months + 1):
        # Indexation addition if indexed
        if expected_annual_inflation_pct > 0:
            indexation_step = current_principal * monthly_inflation
            current_principal += indexation_step
            total_indexation_paid += indexation_step
            
        interest_step = current_principal * monthly_nominal_rate
        
        if is_annuity:
            remaining_months = months - m + 1
            if monthly_nominal_rate > 0:
                annuity_factor = (monthly_nominal_rate * (1 + monthly_nominal_rate)**remaining_months) / (
                    (1 + monthly_nominal_rate)**remaining_months - 1
                )
                payment = current_principal * annuity_factor
            else:
                payment = current_principal / remaining_months
            principal_step = payment - interest_step
        else:
            principal_step = current_principal / (months - m + 1)
            payment = principal_step + interest_step
            
        current_principal -= principal_step
        if current_principal < 0:
            current_principal = 0.0
            
        total_paid += payment
        total_interest_paid += interest_step
        
        if m == 1:
            first_month_payment = payment
        if m == months:
            last_month_payment = payment
            
    return {
        "principal": principal_isk,
        "years": years,
        "interest_rate": annual_interest_rate_pct,
        "inflation_rate": expected_annual_inflation_pct,
        "is_annuity": is_annuity,
        "first_month_payment": round(first_month_payment),
        "last_month_payment": round(last_month_payment),
        "total_paid": round(total_paid),
        "total_interest_paid": round(total_interest_paid),
        "total_indexation_paid": round(total_indexation_paid),
    }


def generate_housing_materials_svg(width: int = 760, height: int = 380) -> str:
    """Generate 100% stacked area/bar vector chart showing building material transformation (1901-2026)."""
    margin_left = 60
    margin_right = 40
    margin_top = 50
    margin_bottom = 45
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    
    n_points = len(HOUSING_MATERIALS_HISTORY)
    step_x = plot_w / (n_points - 1)
    
    # Coordinates builder for stacked areas
    # Order: Turf (bottom), Timber, Concrete, Other (top)
    turf_pts = []
    timber_pts = []
    concrete_pts = []
    other_pts = []
    
    for i, item in enumerate(HOUSING_MATERIALS_HISTORY):
        x = margin_left + i * step_x
        # 100% height scale
        y_turf = margin_top + plot_h - (item["turf"] / 100.0) * plot_h
        y_timber = y_turf - (item["timber"] / 100.0) * plot_h
        y_concrete = y_timber - (item["concrete"] / 100.0) * plot_h
        y_other = margin_top  # exactly 100%
        
        turf_pts.append((x, y_turf))
        timber_pts.append((x, y_timber))
        concrete_pts.append((x, y_concrete))
        other_pts.append((x, y_other))
        
    bottom_y = margin_top + plot_h
    
    # Polygon path strings
    # Turf
    poly_turf = f"M {turf_pts[0][0]},{bottom_y} " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in turf_pts) + f" L {turf_pts[-1][0]},{bottom_y} Z"
    
    # Timber (between turf and timber)
    poly_timber = (
        f"M {turf_pts[0][0]},{turf_pts[0][1]} " +
        " ".join(f"L {x:.1f},{y:.1f}" for x, y in timber_pts) +
        " " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in reversed(turf_pts)) + " Z"
    )
    
    # Concrete (between timber and concrete)
    poly_concrete = (
        f"M {timber_pts[0][0]},{timber_pts[0][1]} " +
        " ".join(f"L {x:.1f},{y:.1f}" for x, y in concrete_pts) +
        " " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in reversed(timber_pts)) + " Z"
    )
    
    # Other (between concrete and other)
    poly_other = (
        f"M {concrete_pts[0][0]},{concrete_pts[0][1]} " +
        " ".join(f"L {x:.1f},{y:.1f}" for x, y in other_pts) +
        " " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in reversed(concrete_pts)) + " Z"
    )

    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        '  <defs>',
        '    <linearGradient id="turfGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '      <stop offset="0%" stop-color="#4a6338"/><stop offset="100%" stop-color="#2d3d22"/>',
        '    </linearGradient>',
        '    <linearGradient id="timberGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '      <stop offset="0%" stop-color="#b88344"/><stop offset="100%" stop-color="#7a5426"/>',
        '    </linearGradient>',
        '    <linearGradient id="concreteGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '      <stop offset="0%" stop-color="#718096"/><stop offset="100%" stop-color="#4a5568"/>',
        '    </linearGradient>',
        '    <linearGradient id="otherGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '      <stop offset="0%" stop-color="#c5a059"/><stop offset="100%" stop-color="#8a6d32"/>',
        '    </linearGradient>',
        '  </defs>',
        f'  <rect width="{width}" height="{height}" rx="10" fill="#0d1527" stroke="#2c3954" stroke-width="1"/>',
        f'  <text x="{width/2}" y="28" text-anchor="middle" fill="#d4af37" font-family="Cinzel, serif" font-size="14" font-weight="bold">ÞRÓUN BYGGINGAREFNA Í ÍSLENSKUM HÚSAKOSTI (1901–2026)</text>',
        f'  <text x="{width/2}" y="44" text-anchor="middle" fill="#8c9cb8" font-family="system-ui, sans-serif" font-size="10">Hlutfall íbúða eftir aðalbyggingarefni samkvæmt manntölum og fasteignaskrá</text>',
    ]
    
    # Render areas
    svg.append(f'  <path d="{poly_turf}" fill="url(#turfGrad)" opacity="0.95"/>')
    svg.append(f'  <path d="{poly_timber}" fill="url(#timberGrad)" opacity="0.95"/>')
    svg.append(f'  <path d="{poly_concrete}" fill="url(#concreteGrad)" opacity="0.95"/>')
    svg.append(f'  <path d="{poly_other}" fill="url(#otherGrad)" opacity="0.95"/>')
    
    # Y-axis percentage markers
    for pct in [0, 25, 50, 75, 100]:
        y_pos = margin_top + plot_h - (pct / 100.0) * plot_h
        svg.append(f'  <line x1="{margin_left}" y1="{y_pos:.1f}" x2="{width - margin_right}" y2="{y_pos:.1f}" stroke="#2a354d" stroke-width="0.8" stroke-dasharray="2,3"/>')
        svg.append(f'  <text x="{margin_left - 8}" y="{y_pos + 3:.1f}" text-anchor="end" fill="#8c9cb8" font-family="Consolas, monospace" font-size="10">{pct}%</text>')
        
    # X-axis year markers
    for i, item in enumerate(HOUSING_MATERIALS_HISTORY):
        x = margin_left + i * step_x
        if item["year"] in [1901, 1920, 1940, 1960, 1980, 2000, 2026]:
            svg.append(f'  <line x1="{x:.1f}" y1="{bottom_y}" x2="{x:.1f}" y2="{bottom_y + 5}" stroke="#8c9cb8" stroke-width="1"/>')
            svg.append(f'  <text x="{x:.1f}" y="{bottom_y + 18}" text-anchor="middle" fill="#c5a059" font-family="Consolas, monospace" font-size="10">{item["year"]}</text>')
            
    # Legend
    leg_y = height - 12
    svg.append(f'  <rect x="{margin_left + 20}" y="{leg_y - 8}" width="12" height="8" rx="2" fill="#4a6338"/>')
    svg.append(f'  <text x="{margin_left + 36}" y="{leg_y}" fill="#d4af37" font-family="system-ui, sans-serif" font-size="9">Torfbæir</text>')
    
    svg.append(f'  <rect x="{margin_left + 120}" y="{leg_y - 8}" width="12" height="8" rx="2" fill="#b88344"/>')
    svg.append(f'  <text x="{margin_left + 136}" y="{leg_y}" fill="#d4af37" font-family="system-ui, sans-serif" font-size="9">Timburhús</text>')
    
    svg.append(f'  <rect x="{margin_left + 230}" y="{leg_y - 8}" width="12" height="8" rx="2" fill="#718096"/>')
    svg.append(f'  <text x="{margin_left + 246}" y="{leg_y}" fill="#d4af37" font-family="system-ui, sans-serif" font-size="9">Steinsteypa</text>')
    
    svg.append(f'  <rect x="{margin_left + 350}" y="{leg_y - 8}" width="12" height="8" rx="2" fill="#c5a059"/>')
    svg.append(f'  <text x="{margin_left + 366}" y="{leg_y}" fill="#d4af37" font-family="system-ui, sans-serif" font-size="9">Stál / Krosslím / Annað</text>')
    
    svg.append('</svg>')
    return "\n".join(svg)


def generate_real_housing_price_chart_svg(width: int = 760, height: int = 340) -> str:
    """Generate line chart of Real vs Nominal Housing Price Index (1994-2026)."""
    margin_left = 65
    margin_right = 45
    margin_top = 45
    margin_bottom = 40
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    
    max_val = max(x[1] for x in REAL_HOUSING_PRICE_SERIES) * 1.05
    n_pts = len(REAL_HOUSING_PRICE_SERIES)
    step_x = plot_w / (n_pts - 1)
    
    def val_to_y(v: float) -> float:
        return margin_top + plot_h - (v / max_val) * plot_h
        
    pts_nom = []
    pts_real = []
    for i, (yr, nom, real) in enumerate(REAL_HOUSING_PRICE_SERIES):
        x = margin_left + i * step_x
        pts_nom.append((x, val_to_y(nom)))
        pts_real.append((x, val_to_y(real)))
        
    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect width="{width}" height="{height}" rx="10" fill="#0b1323" stroke="#223048" stroke-width="1"/>',
        f'  <text x="{width/2}" y="24" text-anchor="middle" fill="#d4af37" font-family="Cinzel, serif" font-size="13" font-weight="bold">VÍSITALA ÍBÚÐAVERÐS Á HÖFUÐBORGARSVÆÐINU (1994–2026)</text>',
        f'  <text x="{width/2}" y="38" text-anchor="middle" fill="#8c9cb8" font-family="system-ui, sans-serif" font-size="10">Nafnverð (gull) vs. Raunverð leiðrétt fyrir vísitölu neysluverðs (blátt) • Grunnur Jan 2000 = 100</text>',
    ]
    
    # Horizontal grid lines
    for grid_v in [0, 200, 400, 600, 800]:
        y = val_to_y(grid_v)
        svg.append(f'  <line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="#1e2a3f" stroke-width="0.8"/>')
        svg.append(f'  <text x="{margin_left - 8}" y="{y + 3:.1f}" text-anchor="end" fill="#6a7b98" font-family="Consolas, monospace" font-size="9">{grid_v}</text>')
        
    # Polylines
    path_nom = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_nom)
    path_real = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_real)
    
    svg.append(f'  <path d="{path_nom}" fill="none" stroke="#d4af37" stroke-width="2.5" stroke-linecap="round"/>')
    svg.append(f'  <path d="{path_real}" fill="none" stroke="#3498db" stroke-width="2.2" stroke-linecap="round"/>')
    
    # Markers & labels on selected years
    for i, (yr, nom, real) in enumerate(REAL_HOUSING_PRICE_SERIES):
        x, y_n = pts_nom[i]
        _, y_r = pts_real[i]
        
        if yr in [1994, 2000, 2007, 2010, 2018, 2022, 2026]:
            svg.append(f'  <circle cx="{x:.1f}" cy="{y_n:.1f}" r="3.5" fill="#d4af37" stroke="#ffffff" stroke-width="1"/>')
            svg.append(f'  <circle cx="{x:.1f}" cy="{y_r:.1f}" r="3.5" fill="#3498db" stroke="#ffffff" stroke-width="1"/>')
            svg.append(f'  <text x="{x:.1f}" y="{margin_top + plot_h + 16}" text-anchor="middle" fill="#8c9cb8" font-family="Consolas, monospace" font-size="9">{yr}</text>')
            
    # Legend
    svg.append(f'  <line x1="{width - 240}" y1="20" x2="{width - 215}" y2="20" stroke="#d4af37" stroke-width="2.5"/>')
    svg.append(f'  <text x="{width - 208}" y="24" fill="#d4af37" font-family="system-ui, sans-serif" font-size="10">Nafnverð</text>')
    svg.append(f'  <line x1="{width - 130}" y1="20" x2="{width - 105}" y2="20" stroke="#3498db" stroke-width="2.5"/>')
    svg.append(f'  <text x="{width - 98}" y="24" fill="#3498db" font-family="system-ui, sans-serif" font-size="10">Raunverð</text>')
    
    svg.append('</svg>')
    return "\n".join(svg)


def render_housing_analytics_ui(st_module) -> None:
    """Streamlit interactive UI for housing and mortgage analytics."""
    st = st_module
    st.markdown("### 🏛️ Húsnæðisþróun, Byggingarefni & Veðlánamat")
    st.markdown(
        "Söguleg þróun húsakosts á Íslandi frá torfbæjum 1900 til nútíma steinsteypu- og krosslímsíbúða 2026, "
        "ásamt raunverðsvísitölum fasteigna og keisaralegum veðlánareikni."
    )
    
    tab1, tab2, tab3 = st.tabs(["🏗️ Byggingarefni & Húsakostur", "📈 Íbúðaverðsvísitala", "💰 Veðlánareiknir (Lánadómur)"])
    
    with tab1:
        st.markdown(generate_housing_materials_svg(760, 380), unsafe_allow_html=True)
        st.info(
            "**Sögulegt stökk:** Árið 1901 bjuggu yfir 62% landsmanna í torfbæjum. Á aðeins fjórum áratugum "
            "gerbyltist byggingartækni Íslendinga með tilkomu steinsteypunnar, sem reyndist einstaklega vel "
            "gegn íslenskum veðrunaráhrifum og eldsvoðum sem herjuðu á gamla timburbæi."
        )
        
        st.markdown("#### Eignarhald á íbúðarhúsnæði í gegnum áratugina")
        cols = st.columns(4)
        for idx, row in enumerate(HOMEOWNERSHIP_DYNAMICS):
            with cols[idx % 4]:
                st.metric(f"Áratugur {row['decade']}", f"{row['rate']}%", help=row['context'])
                
    with tab2:
        st.markdown(generate_real_housing_price_chart_svg(760, 340), unsafe_allow_html=True)
        st.markdown(
            "> [!NOTE]\n"
            "> **Raunverð vs Nafnverð:** Þótt nafnverð fasteigna hafi nær níufaldast frá aldamótum 2000 (úr 100 í ~898 stig), "
            "> hefur raunverð (leiðrétt fyrir almennri verðbólgu) hækkað um u.þ.b. 160% á sama tímabili."
        )
        
    with tab3:
        st.markdown("#### ⚖️ Keisaralegur Veðlánareiknir (*Calculus Hypothecae*)")
        st.caption("Reiknaðu mánaðarlega greiðslubyrði, verðbætur og heildarvaxtagjöld.")
        
        c1, c2 = st.columns(2)
        with c1:
            principal = st.number_input("Lánsfjárhæð (kr.):", min_value=1_000_000, max_value=250_000_000, value=45_000_000, step=1_000_000)
            years = st.slider("Lánstími (ár):", min_value=5, max_value=40, value=25, step=5)
            loan_type = st.radio("Tegund láns:", ["Jafnar greiðslur (Annuity)", "Jafnar afborganir (Linear)"])
        with c2:
            is_indexed = st.checkbox("Verðtryggt lán (Vísitala neysluverðs)", value=True)
            if is_indexed:
                rate = st.slider("Fastir eða breytilegir raunvextir (%):", min_value=1.0, max_value=8.0, value=3.8, step=0.1)
                expected_inf = st.slider("Áætluð ársverðbólga (%):", min_value=1.0, max_value=12.0, value=4.0, step=0.5)
            else:
                rate = st.slider("Óverðtryggðir nafnvextir (%):", min_value=3.0, max_value=15.0, value=8.75, step=0.25)
                expected_inf = 0.0
                
        is_annuity = (loan_type == "Jafnar greiðslur (Annuity)")
        res = calculate_mortgage_schedule(principal, rate, years, is_annuity, expected_inf)
        
        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Fyrsta mánaðargreiðsla", f"{res['first_month_payment']:,} kr.")
        with m2:
            st.metric("Síðasta mánaðargreiðsla", f"{res['last_month_payment']:,} kr.")
        with m3:
            st.metric("Heildarvextir greiddir", f"{res['total_interest_paid']:,} kr.")
        with m4:
            st.metric("Heildargreiðsla láns", f"{res['total_paid']:,} kr.")
            
        if is_indexed and res['total_indexation_paid'] > 0:
            st.warning(f"Áætlaðar verðbætur sem bætast við höfuðstól yfir lánstímann: **{res['total_indexation_paid']:,} kr.**")
