"""
visuals - Gagnvirkt Sjónrænt Kerfispakki Hagstofu Íslands

Flytur út lykileiningar fyrir:
- Íslandskort og svæðisgreiningu (geo_iceland)
- Línuritakerfi og tímaraðir (charts_engine)
- Kaupmáttarreiknivél og tímavél (purchasing_power)
- Sveitarfélagaatlas Íslands (municipalities_atlas)
- Sögulegt manntal og lífslíkur (historical_demographics)
- Efnahagsvísa og gengi (economic_indicators)
- Flutningastrauma og chord-vigurrit (sankey_migration)
- Húsnæði, byggingarefni og veðlánamat (housing_and_construction)
- Orkubyltingu og loftslagsmet (energy_and_climate)
- Menningarlegar og tölfræðilegar sérviskur (statistical_curiosities)
- Tölfræðipróf og spurningaleik (interactive_quiz)
- Tölfræðialfræði og hugtök (statistical_glossary_encyclopedia)
- Rómverskt stofnanaþema og tilskipanir (roman_theme)
- Gagnasafns- og lýsigagnaskoðara (catalog_navigator)
- Stofnanaskýrslugerð (report_exporter)
- Aðalstjórnborð (dashboard)
"""

from .geo_iceland import (
    generate_iceland_svg,
    generate_reykjavik_districts_svg,
    get_regional_summary_table,
    REGIONS_DATA,
    REYKJAVIK_DISTRICTS,
    MIGRATION_FLOWS_2024,
)
from .charts_engine import (
    generate_cpi_svg_chart,
    generate_population_pyramid_svg,
    generate_tourist_arrivals_chart,
    CPI_HISTORICAL_ANNUAL,
    HISTORICAL_MILESTONES,
    POPULATION_PYRAMID_2026,
    TOURIST_ARRIVALS,
)
from .purchasing_power import (
    calculate_purchasing_power,
    render_purchasing_power_html,
    BASKET_EXAMPLES,
    CPI_SERIES_FULL,
)
from .municipalities_atlas import (
    get_all_municipalities_list,
    get_municipality_by_name,
    MUNICIPALITIES_FULL_DB,
)
from .historical_demographics import (
    generate_historical_population_svg,
    render_historical_timeline_html,
    CENSUS_HISTORICAL,
    LIFE_EXPECTANCY_HISTORICAL,
)
from .economic_indicators import (
    generate_exchange_rate_svg,
    generate_unemployment_svg,
    USD_HISTORICAL_EXCHANGE,
    EUR_HISTORICAL_EXCHANGE,
    UNEMPLOYMENT_HISTORICAL,
)
from .sankey_migration import (
    generate_migration_chord_svg,
    generate_migration_balance_barchart_svg,
    get_region_migration_summary,
    render_migration_explorer_ui,
    REGIONS,
    MIGRATION_MATRIX,
)
from .housing_and_construction import (
    generate_housing_materials_svg,
    generate_real_housing_price_chart_svg,
    calculate_mortgage_schedule,
    render_housing_analytics_ui,
    HOUSING_MATERIALS_HISTORY,
    REAL_HOUSING_PRICE_SERIES,
)
from .energy_and_climate import (
    generate_energy_transition_chart_svg,
    generate_climate_deviations_svg,
    render_energy_climate_ui,
    ENERGY_CONSUMPTION_SERIES,
    STYKKISHOLMUR_TEMPERATURE_SERIES,
)
from .statistical_curiosities import (
    generate_beer_transition_chart_svg,
    render_curiosities_ui,
    STATISTICAL_CURIOSITIES,
)
from .interactive_quiz import (
    render_interactive_quiz_ui,
    QUIZ_QUESTIONS,
)
from .statistical_glossary_encyclopedia import (
    render_glossary_encyclopedia_ui,
    STATISTICAL_TERMS_DB,
)
from .roman_theme import (
    to_roman_numerals,
    from_roman_numerals,
    generate_wax_seal_svg,
    generate_imperial_decree_html,
    LATIN_MOTTOES,
    THEME_PALETTES,
)
from .catalog_navigator import (
    load_full_catalog,
    search_catalog,
    render_catalog_card_html,
    CATEGORY_ICONS,
)
from .report_exporter import (
    build_full_html_report,
    get_downloadable_report_b64,
)
from .dashboard import (
    render_interactive_dashboard,
)
