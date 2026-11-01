"""Aðalstjórnandi fyrir Gagnvirkt Sjónrænt Stofnanaviðmót Hagstofu Íslands.

Tengir saman öll sjónræn kerfi í eitt glæsilegt stofnanaviðmót með flipum (tabs)
eða hliðarstýringu, án þess að hrófla við grunnvirkni gagnasvararans.
"""

from __future__ import annotations

import streamlit as st
from typing import Dict, List, Optional

from visuals.geo_iceland import (
    generate_iceland_svg,
    generate_reykjavik_districts_svg,
    get_regional_summary_table,
    REGIONS_DATA,
    MIGRATION_FLOWS_2024,
)
from visuals.charts_engine import (
    generate_cpi_svg_chart,
    generate_population_pyramid_svg,
    generate_tourist_arrivals_chart,
    CPI_HISTORICAL_ANNUAL,
    POPULATION_PYRAMID_2026,
)
from visuals.purchasing_power import (
    calculate_purchasing_power,
    render_purchasing_power_html,
    BASKET_EXAMPLES,
)
from visuals.municipalities_atlas import (
    get_all_municipalities_list,
    get_municipality_by_name,
    MUNICIPALITIES_FULL_DB,
)
from visuals.historical_demographics import (
    generate_historical_population_svg,
    render_historical_timeline_html,
    CENSUS_HISTORICAL,
    LIFE_EXPECTANCY_HISTORICAL,
)
from visuals.economic_indicators import (
    generate_exchange_rate_svg,
    generate_unemployment_svg,
    USD_HISTORICAL_EXCHANGE,
    EUR_HISTORICAL_EXCHANGE,
    UNEMPLOYMENT_HISTORICAL,
)
from visuals.sankey_migration import (
    generate_migration_chord_svg,
    generate_migration_balance_barchart_svg,
    render_migration_explorer_ui,
)
from visuals.housing_and_construction import (
    generate_housing_materials_svg,
    generate_real_housing_price_chart_svg,
    render_housing_analytics_ui,
)
from visuals.energy_and_climate import (
    generate_energy_transition_chart_svg,
    generate_climate_deviations_svg,
    render_energy_climate_ui,
)
from visuals.statistical_curiosities import (
    generate_beer_transition_chart_svg,
    render_curiosities_ui,
    STATISTICAL_CURIOSITIES,
)
from visuals.interactive_quiz import (
    render_interactive_quiz_ui,
)
from visuals.statistical_glossary_encyclopedia import (
    render_glossary_encyclopedia_ui,
)
from visuals.catalog_navigator import (
    load_full_catalog,
    search_catalog,
    render_catalog_card_html,
)
from visuals.roman_theme import (
    to_roman_numerals,
    generate_wax_seal_svg,
    generate_imperial_decree_html,
    LATIN_MOTTOES,
    THEME_PALETTES,
)
from visuals.imperial_styling import (
    render_glossary_grid_html,
    generate_laurel_wreath_svg,
)
from visuals.report_exporter import (
    build_full_html_report,
    get_downloadable_report_b64,
)


def render_map_tab() -> None:
    """Birtir Íslandskortið og búferlaflutningagreiningu."""
    st.markdown("### 🗺️ TABULA ISLANDIAE &middot; Íslandskort og Svæðagreining")
    st.caption("Gagnvirkt vigurkort yfir 8 landshluta Íslands og helstu búferlaflutninga (Tafla MAN01002)")

    col1, col2 = st.columns([2, 1])
    with col2:
        selected_region = st.selectbox(
            "Veldu landshluta til að skoða:",
            options=["Allt landið"] + [f"{r['name']} ({r['id']})" for r in REGIONS_DATA.values()]
        )
        show_flows = st.checkbox("Sýna búferlaflutningaörvar (2024)", value=True)
        color_scheme = st.radio("Litun landshluta:", ["density", "distinct"], format_func=lambda x: "Þéttleiki íbúa" if x == "density" else "Sérstakir litir")

    reg_id = None
    if selected_region != "Allt landið":
        reg_id = selected_region.split("(")[-1].replace(")", "").strip()

    with col1:
        svg_code = generate_iceland_svg(selected_region_id=reg_id, show_migration=show_flows, color_mode=color_scheme)
        st.markdown(svg_code, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🏘️ Hverfaskipting Reykjavíkurborgar (Tafla MAN03270)")
    dist_svg = generate_reykjavik_districts_svg()
    st.markdown(dist_svg, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📊 Yfirlitstöflur Landshluta")
    table_data = get_regional_summary_table()
    st.dataframe(table_data, use_container_width=True)


def render_economic_tab() -> None:
    """Birtir efnahags- og verðbólgugreiningu."""
    st.markdown("### 📈 EFNAHAGS- OG VERÐBÓLGUGREINING")
    st.caption("Rauntímagreining á vísitölu neysluverðs, gengi krónunnar og atvinnuleysi (Töflur VIS01002, SOG08008, VIN00001)")

    st.markdown("#### 1. Vísitala Neysluverðs 1980–2026")
    cpi_svg = generate_cpi_svg_chart()
    st.markdown(cpi_svg, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 2. Gengisþróun (USD / EUR)")
        fx_svg = generate_exchange_rate_svg(width=520, height=340)
        st.markdown(fx_svg, unsafe_allow_html=True)
    with col2:
        st.markdown("#### 3. Skráð Atvinnuleysi (% af vinnuafli)")
        unemp_svg = generate_unemployment_svg(width=520, height=340)
        st.markdown(unemp_svg, unsafe_allow_html=True)


def render_demographics_tab() -> None:
    """Birtir mannfjöldapýramídann og kynjaskiptingu."""
    st.markdown("### 👥 MANNFJÖLDAPÝRAMÍDI ÍSLANDS (2026)")
    st.caption("Aldurs- og kynjaskipting íbúa Íslands byggð á opinberri töflu MAN00000 hjá Hagstofu Íslands")

    pyr_svg = generate_population_pyramid_svg()
    st.markdown(pyr_svg, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ✈️ Erlendum ferðamönnum um Keflavíkurflugvöll (SAM02001)")
    tourist_svg = generate_tourist_arrivals_chart()
    st.markdown(tourist_svg, unsafe_allow_html=True)


def render_purchasing_power_tab() -> None:
    """Birtir gagnvirka kaupmáttarreiknivél krónunnar."""
    st.markdown("### ⏳ TÍMAVÉL KRÓNUNNAR &middot; AEQUALITAS PECUNIAE")
    st.caption("Reiknaðu raunvirði íslensku krónunnar á milli hvaða tveggja ára sem er frá 1939 til 2026 samkvæmt töflu VIS01002.")

    col1, col2, col3 = st.columns(3)
    with col1:
        amount = st.number_input("Upphæð í krónum:", min_value=1.0, value=1000.0, step=100.0)
    with col2:
        start_year = st.slider("Upphafsár:", min_value=1939, max_value=2026, value=1990)
    with col3:
        target_year = st.slider("Markár:", min_value=1939, max_value=2026, value=2026)

    res = calculate_purchasing_power(amount, start_year, target_year)
    if "error" not in res:
        st.markdown(render_purchasing_power_html(res), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🛒 Söguleg Vörukarfa og Samanburður")
    for ex in BASKET_EXAMPLES:
        with st.expander(f"{ex['icon']} {ex['item']}"):
            st.write(f"**Verð árið 1980:** {ex['price_1980']}")
            st.write(f"**Verð árið 2000:** {ex['price_2000']}")
            st.write(f"**Verð árið 2026:** {ex['price_2026']}")
            st.info(ex["note"])


def render_municipalities_tab() -> None:
    """Birtir sveitarfélagaatlasinn."""
    st.markdown("### 🏛️ SVEITARFÉLAGAATLAS ÍSLANDS")
    st.caption("Allar upplýsingar um 64 sveitarfélög samkvæmt nýjustu sveitarfélagaskipan (Tafla MAN02005)")

    all_munis = get_all_municipalities_list()

    col_search, col_filter = st.columns([2, 1])
    with col_search:
        m_query = st.text_input("Leitaðu að sveitarfélagi eða kennileiti (t.d. Kópavogur, Dynjandi, Gullfoss):", "")
    with col_filter:
        region_filter = st.selectbox("Sía eftir landshluta:", ["Allir landshlutar"] + sorted(list({m["region"] for m in all_munis})))

    filtered = all_munis
    if region_filter != "Allir landshlutar":
        filtered = [m for m in filtered if m["region"] == region_filter]
    if m_query.strip():
        q_l = m_query.lower().strip()
        filtered = [
            m for m in filtered
            if q_l in m["name"].lower() or any(q_l in lm.lower() for lm in m["notable_landmarks"])
        ]

    st.write(f"Fann **{len(filtered)}** sveitarfélög:")

    for m in filtered[:12]:
        with st.expander(f"🏛️ {m['name']} — {m['pop_2026']:,} íbúar ({m['region']})"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Stjórnsýslusetur:** {m['seat']}")
                st.write(f"**Einkunnarorð:** *{m['motto']}*")
                st.write(f"**Skjaldarmerki:** {m['emblem']}")
                st.write(f"**Flatarmál:** {m['area_km2']:,} km²")
            with c2:
                st.write(f"**Íbúar 2000:** {m['pop_2000']:,}")
                st.write(f"**Íbúar 2010:** {m['pop_2010']:,}")
                st.write(f"**Íbúar 2020:** {m['pop_2020']:,}")
                st.write(f"**Íbúar 2026:** {m['pop_2026']:,}")
            st.info(f"**Sameiningasaga:** {m['merger_history']}")
            st.caption(f"Helstu kennileiti: {', '.join(m['notable_landmarks'])}")


def render_history_tab() -> None:
    """Birtir sögulega manntalið 1703–2026."""
    st.markdown("### 📜 MANNTALASAGA ÍSLANDS FRÁ 1703")
    st.caption("Fyrsta heildstæða manntal sögunnar til nútímans (Tafla MAN00000)")

    hist_svg = generate_historical_population_svg()
    st.markdown(hist_svg, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ⏳ Sögulegur Tímaás og Áföll Þjóðarinnar")
    st.markdown(render_historical_timeline_html(), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🩺 Þróun Lífslíkna við Fæðingu (1850–2026)")
    life_data = [
        {"Ár": yr, "Lífslíkur karla (ár)": m, "Lífslíkur kvenna (ár)": f, "Munur": f"{f-m:+.1f} ár"}
        for yr, m, f in LIFE_EXPECTANCY_HISTORICAL
    ]
    st.table(life_data)


def render_catalog_tab() -> None:
    """Birtir töflusafnið og lýsigagnaleitina."""
    st.markdown("### 📚 TÖFLUSAFN HAGSTOFU ÍSLANDS")
    st.caption("Yfirlit yfir yfir 100 tölfræðitöflur með beinum tengingum við PX-Web API")

    catalog = load_full_catalog()

    c1, c2 = st.columns([2, 1])
    with c1:
        cat_search = st.text_input("Leitaðu í töflusafni (heiti, kóði eða efni):", "")
    with c2:
        categories = ["Allir flokkar"] + sorted(list({t.get("category", "General") for t in catalog}))
        sel_cat = st.selectbox("Flokkur:", categories)

    results = search_catalog(catalog, cat_search, sel_cat)
    st.write(f"Sýni **{len(results)}** töflur:")

    for t in results[:20]:
        st.markdown(render_catalog_card_html(t), unsafe_allow_html=True)


def render_decree_tab(last_admin_debug: Optional[Dict] = None) -> None:
    """Birtir keisaralega tilskipun og skýrslugerð."""
    st.markdown("### 🦅 KEISARALEG TILSKIPUN &middot; SENATUS CONSULTUM")
    st.caption("Búðu til formlegt, prenthæft vottorð á pergamenti með vaxinnsigli byggt á nýjustu mælingu.")

    motto_dict = LATIN_MOTTOES[0]
    st.markdown(f"*{motto_dict['latin']}* — **{motto_dict['is']}**")

    # Innsigli og dæmi
    sample_text = (
        "Samkvæmt opinberum skrám Hagstofu Íslands búa 139.804 manns í Reykjavíkurborg þann 1. janúar 2026. "
        "Þessi tala hefur verið sannreynd gagnvart opinberu gagnagrunnstöflunni MAN02005 án nokkurra frávika."
    )
    decree_html = generate_imperial_decree_html(
        title="INCLITA CIVITAS REYKIAVIKENSIS",
        body_text=sample_text,
        source_table="MAN02005 - Mannfjöldi eftir sveitarfélögum",
        date_str="Anno Domini MMXXVI",
    )
    st.markdown(decree_html, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🏛️ Latneskt Orðasafn Hagstærða")
    st.markdown(render_glossary_grid_html(), unsafe_allow_html=True)

    # Prenthæf HTML skýrsla
    st.markdown("---")
    st.markdown("#### 🖨️ Sækja Fullbúna Tölfræðiskýrslu á HTML-formi")
    html_rep = build_full_html_report(
        query="Hvað búa margir í Reykjavík árið 2026?",
        answer="Samkvæmt mannfjöldatölum Hagstofu Íslands (tafla MAN02005) bjuggu 139.804 manns í Reykjavíkurborg þann 1. janúar 2026.",
        table_id="MAN02005",
        table_title="Mannfjöldi eftir kyni, aldri og sveitarfélögum 1998-2026",
        source_url="https://px.hagstofa.is/pxis/api/v1/is/Ibuar/mannfjoldi/2_byggdir/sveitarfelog/MAN02005.px",
        facts=["Sveitarfélag: Reykjavíkurborg, Aldur: Alls, Ár: 2026, Kyn: Alls = 139804"],
        latency=0.08,
    )
    st.download_button(
        label="📜 Sækja Opinbera Skýrslu (HTML)",
        data=html_rep,
        file_name="Hagstofa_Skyrsla_MAN02005.html",
        mime="text/html",
    )


def render_interactive_dashboard(last_admin_debug: Optional[Dict] = None) -> None:
    """Birtir alla heildstæðu keisaralegu stjórnborðssvítuna í vönduðu viðmóti."""
    tabs = st.tabs([
        "🗺️ Íslandskort",
        "🕊️ Flutningar (Chord)",
        "📈 Efnahagur & Verðbólga",
        "👥 Mannfjöldapýramídi",
        "⏳ Tímavél Krónunnar",
        "🏛️ Sveitarfélagaatlas",
        "🏗️ Húsnæði & Veðlán",
        "⚡ Orka & Loftslag",
        "📜 Manntalasaga 1703",
        "🍷 Sérviskur & Menning",
        "🧩 Tölfræðipróf",
        "📖 Tölfræðialfræði",
        "📚 Töflusafn",
        "🦅 Keisaraleg Tilskipun",
    ])

    with tabs[0]:
        render_map_tab()
    with tabs[1]:
        render_migration_explorer_ui(st)
    with tabs[2]:
        render_economic_tab()
    with tabs[3]:
        render_demographics_tab()
    with tabs[4]:
        render_purchasing_power_tab()
    with tabs[5]:
        render_municipalities_tab()
    with tabs[6]:
        render_housing_analytics_ui(st)
    with tabs[7]:
        render_energy_climate_ui(st)
    with tabs[8]:
        render_history_tab()
    with tabs[9]:
        render_curiosities_ui(st)
    with tabs[10]:
        render_interactive_quiz_ui(st)
    with tabs[11]:
        render_glossary_encyclopedia_ui(st)
    with tabs[12]:
        render_catalog_tab()
    with tabs[13]:
        render_decree_tab(last_admin_debug)
