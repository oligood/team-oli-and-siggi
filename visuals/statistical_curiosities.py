"""Iconic Statistical Curiosities and Cultural Anomalies of Iceland.

Chronicles unique historical anomalies recorded in Icelandic national statistics:
- Bjórbannið (The Beer Prohibition: 1915–1989)
- Sjónvarpslausir fimmtudagar & júlí-frí (Television-free days: 1966–1987)
- H-dagurinn (The Traffic Inversion: May 26, 1968)
- Gengisbreytingin mikla 1981 (Dropping two zeroes: 100 gamlar krónur = 1 ný króna)
- Nafnahefðir gegnum aldirnar (Jón, Guðrún, and naming trends)
Pure-Python vector SVG generation with classical Roman institutional styling.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


STATISTICAL_CURIOSITIES: List[Dict[str, any]] = [
    {
        "id": "bjorbann",
        "title": "Bjórbannið (1915–1989)",
        "latin": "Prohibitio Cervisiae",
        "dates": "1. janúar 1915 – 1. mars 1989",
        "summary": "Áfengisbann var samþykkt í þjóðaratkvæðagreiðslu 1908 og gekk í gildi 1915. Léttvín og sterkt áfengi voru leyfð á ný á 3. og 4. áratugnum, en bjórbannið stóð í 74 ár.",
        "statistical_fact": "Fyrsta árið eftir afnám bannsins (1989) drukku Íslendingar 11,5 milljónir lítra af bjór. Áfengisneysla jókst samtals mun minna en spáð var þar sem bjór kom að stórum hluta í stað brennivíns.",
        "icon": "🍺",
    },
    {
        "id": "sjonvarpsbann",
        "title": "Sjónvarpslausir fimmtudagar & júlífrí",
        "latin": "Dies Sine Televisione",
        "dates": "1966 – 1987",
        "summary": "Ríkisútvarpið (Sjónvarpið) hóf útsendingar 1966. Til að vernda félagslíf, fjölskyldur og bóklestur voru fimmtudagar alfarið sjónvarpslausir til 1987, auk þess sem engar útsendingar voru allan júlímánuð til 1983.",
        "statistical_fact": "Á fimmtudagskvöldum mældist met-aðsókn í kvikmyndahús landsins og bókasöfn tilkynntu um marktækt meiri útlán en aðra daga vikunnar.",
        "icon": "📺",
    },
    {
        "id": "h_dagurinn",
        "title": "H-dagurinn: Hægri umferð",
        "latin": "Mutatio Dextrae Viae",
        "dates": "Sunnudagur 26. maí 1968, kl. 06:00",
        "summary": "Ísland skipti úr vinstri umferð í hægri umferð á einu augabragði. Öll umferð var stöðvuð klukkan 05:58 og ekið yfir á hægri akrein kl. 06:00.",
        "statistical_fact": "Breytingin kostaði rúmar 65 milljónir króna á þeim tíma. Aðeins eitt alvarlegt slys varð á breytingadaginn þegar drengur á hjóli fótbrotnaði.",
        "icon": "🚗",
    },
    {
        "id": "myntbreyting_1981",
        "title": "Gjaldmiðilsbreytingin 1981: Nýja krónan",
        "latin": "Reformatio Monetae",
        "dates": "1. janúar 1981",
        "summary": "Vegna gríðarlegrar óðaverðbólgu á 8. áratugnum (sem náði yfir 80% á ári) voru tvö núll skorin aftan af íslensku krónunni. 100 gamlar krónur (ISG) urðu 1 ný króna (ISK).",
        "statistical_fact": "Á einni nóttu lækkaði kaffibolli úr 2.500 krónum í 25 krónur. Árið 1983 fór verðbólga engu að síður aftur yfir 100% tímabundið áður en böndum var komið á hana með Þjóðarsátt 1990.",
        "icon": "🪙",
    },
    {
        "id": "nofn_og_hefdir",
        "title": "Nafnahefðir og algengustu nöfn",
        "latin": "Nomina Populi Islandici",
        "dates": "1703 – 2026",
        "summary": "Íslendingar hafa viðhaldið föðurnafnakerfi frá landnámi. Jón og Guðrún hafa trónað á toppi nafnatölfræðinnar frá fyrsta manntalinu 1703.",
        "statistical_fact": "Árið 1703 báru yfir 22% allra karla nafnið Jón, og nær 19% allra kvenna nafnið Guðrún. Árið 2026 er nafnafjölbreytni margföld, en Guðrún er enn algengasta eiginnafn kvenna.",
        "icon": "📜",
    },
]

# Beer sales progression after 1989 (liters of pure alcohol per adult inhabitant)
ALCOHOL_STATISTICS_POST_BAN: List[Tuple[int, float, float, float]] = [
    # Year, Beer, Wine, Spirits (liters pure alcohol)
    (1985, 0.0, 0.8, 3.4),  # Pre-beer legalization (spirits dominant)
    (1989, 1.4, 0.9, 3.1),  # Legalization year (March 1)
    (1995, 2.8, 1.1, 2.3),
    (2000, 3.6, 1.5, 2.1),
    (2010, 4.2, 1.9, 1.7),
    (2020, 4.5, 2.1, 1.5),
    (2025, 4.4, 2.2, 1.4),
]


def generate_beer_transition_chart_svg(width: int = 760, height: int = 320) -> str:
    """Generate SVG chart showing the seismic shift in alcohol consumption patterns (1985–2025)."""
    margin_left = 60
    margin_right = 40
    margin_top = 40
    margin_bottom = 40
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    
    max_val = 5.0
    n_pts = len(ALCOHOL_STATISTICS_POST_BAN)
    step_x = plot_w / (n_pts - 1)
    
    def val_to_y(v: float) -> float:
        return margin_top + plot_h - (v / max_val) * plot_h
        
    pts_beer = []
    pts_wine = []
    pts_spirits = []
    
    for i, (yr, b, w, s) in enumerate(ALCOHOL_STATISTICS_POST_BAN):
        x = margin_left + i * step_x
        pts_beer.append((x, val_to_y(b)))
        pts_wine.append((x, val_to_y(w)))
        pts_spirits.append((x, val_to_y(s)))
        
    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect width="{width}" height="{height}" rx="10" fill="#0d1424" stroke="#25354e" stroke-width="1"/>',
        f'  <text x="{width/2}" y="24" text-anchor="middle" fill="#d4af37" font-family="Cinzel, serif" font-size="13" font-weight="bold">ÁHRIF BJÓRLÖGLEIÐINGARINNAR Á NEYSLUMYNSTUR (1985–2025)</text>',
        f'  <text x="{width/2}" y="38" text-anchor="middle" fill="#8c9cb8" font-family="system-ui, sans-serif" font-size="10">Lítrar af hreinum vínanda á hvern íbúa 15 ára og eldri • Hagstofa Íslands & ÁTVR</text>',
    ]
    
    # Horizontal grid lines
    for grid_v in [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]:
        y = val_to_y(grid_v)
        svg.append(f'  <line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="#1e2d42" stroke-width="0.8"/>')
        svg.append(f'  <text x="{margin_left - 8}" y="{y + 3:.1f}" text-anchor="end" fill="#6d7f9c" font-family="Consolas, monospace" font-size="9">{grid_v:.1f} L</text>')
        
    # Vertical marker for March 1 1989
    x_1989 = pts_beer[1][0]
    svg.append(f'  <line x1="{x_1989:.1f}" y1="{margin_top}" x2="{x_1989:.1f}" y2="{margin_top + plot_h}" stroke="#e74c3c" stroke-width="1.2" stroke-dasharray="3,3"/>')
    svg.append(f'  <text x="{x_1989 + 5:.1f}" y="{margin_top + 18}" fill="#e74c3c" font-family="Cinzel, serif" font-size="9" font-weight="bold">1. mars 1989</text>')
    
    # Render polylines
    path_beer = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_beer)
    path_wine = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_wine)
    path_spirits = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_spirits)
    
    svg.append(f'  <path d="{path_beer}" fill="none" stroke="#f1c40f" stroke-width="2.5" stroke-linecap="round"/>')
    svg.append(f'  <path d="{path_wine}" fill="none" stroke="#e74c3c" stroke-width="2.0" stroke-linecap="round"/>')
    svg.append(f'  <path d="{path_spirits}" fill="none" stroke="#95a5a6" stroke-width="2.0" stroke-linecap="round"/>')
    
    # Points
    for i, (yr, b, w, s) in enumerate(ALCOHOL_STATISTICS_POST_BAN):
        x, y_b = pts_beer[i]
        _, y_w = pts_wine[i]
        _, y_s = pts_spirits[i]
        svg.append(f'  <circle cx="{x:.1f}" cy="{y_b:.1f}" r="3" fill="#f1c40f"/>')
        svg.append(f'  <circle cx="{x:.1f}" cy="{y_w:.1f}" r="3" fill="#e74c3c"/>')
        svg.append(f'  <circle cx="{x:.1f}" cy="{y_s:.1f}" r="3" fill="#95a5a6"/>')
        svg.append(f'  <text x="{x:.1f}" y="{margin_top + plot_h + 16}" text-anchor="middle" fill="#8c9cb8" font-family="Consolas, monospace" font-size="9">{yr}</text>')
        
    # Legend
    svg.append(f'  <line x1="{width - 270}" y1="18" x2="{width - 250}" y2="18" stroke="#f1c40f" stroke-width="2.5"/>')
    svg.append(f'  <text x="{width - 245}" y="22" fill="#f1c40f" font-family="system-ui, sans-serif" font-size="9">Bjór</text>')
    
    svg.append(f'  <line x1="{width - 195}" y1="18" x2="{width - 175}" y2="18" stroke="#e74c3c" stroke-width="2"/>')
    svg.append(f'  <text x="{width - 170}" y="22" fill="#e74c3c" font-family="system-ui, sans-serif" font-size="9">Léttvín</text>')
    
    svg.append(f'  <line x1="{width - 115}" y1="18" x2="{width - 95}" y2="18" stroke="#95a5a6" stroke-width="2"/>')
    svg.append(f'  <text x="{width - 90}" y="22" fill="#95a5a6" font-family="system-ui, sans-serif" font-size="9">Sterkt</text>')
    
    svg.append('</svg>')
    return "\n".join(svg)


def render_curiosities_ui(st_module) -> None:
    """Streamlit interactive UI for cultural and statistical anomalies."""
    st = st_module
    st.markdown("### 📜 Menningarlegar Sérviskur & Tölfræðileg Sérkenni")
    st.markdown(
        "Íslensk hagsaga geymir ýmsar heillandi og sérstæðar vörður sem mótuðu daglegt líf þjóðarinnar. "
        "Hér má skoða nokkur athyglisverðustu dæmin um hvernig stjórnvöld og samfélag mótuðu neyslu og lífshætti."
    )
    
    for c in STATISTICAL_CURIOSITIES:
        with st.expander(f"{c['icon']} {c['title']} ({c['latin']})", expanded=False):
            st.markdown(f"**Tímabil:** {c['dates']}")
            st.write(c['summary'])
            st.info(f"📊 **Tölfræðileg staðreynd:** {c['statistical_fact']}")
            
            if c['id'] == "bjorbann":
                st.markdown("##### Neysluþróun fyrir og eftir 1989")
                st.markdown(generate_beer_transition_chart_svg(740, 310), unsafe_allow_html=True)
