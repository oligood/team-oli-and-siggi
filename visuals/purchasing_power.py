"""
visuals/purchasing_power.py - Tímavél Krónunnar og Kaupmáttarreiknivél

Reiknar raunverulegt virði íslensku krónunnar á milli hvaða tveggja ára sem er
frá 1939 til 2026 byggt á vísitölu neysluverðs Hagstofu Íslands (VIS01002).
"""

from typing import Dict, List, Optional, Tuple

# Full vísitöluröð Hagstofu Íslands (1939–2026) miðað við grunn 1988=100
CPI_SERIES_FULL: Dict[int, float] = {
    1939: 0.0000047, 1940: 0.0000063, 1941: 0.0000091, 1942: 0.0000140,
    1943: 0.0000161, 1944: 0.0000167, 1945: 0.0000177, 1946: 0.0000189,
    1947: 0.0000196, 1948: 0.0000204, 1949: 0.0000213, 1950: 0.0000257,
    1951: 0.0000336, 1952: 0.0000373, 1953: 0.0000378, 1954: 0.0000385,
    1955: 0.0000412, 1956: 0.0000445, 1957: 0.0000465, 1958: 0.0000488,
    1959: 0.0000521, 1960: 0.0000554, 1961: 0.0000588, 1962: 0.0000672,
    1963: 0.0000756, 1964: 0.0000882, 1965: 0.0000966, 1966: 0.000108,
    1967: 0.000112, 1968: 0.000125, 1969: 0.000155, 1970: 0.000176,
    1971: 0.000195, 1972: 0.000224, 1973: 0.000282, 1974: 0.000403,
    1975: 0.000600, 1976: 0.000788, 1977: 0.00110, 1978: 0.00160,
    1979: 0.00249, 1980: 0.00450, 1981: 0.00680, 1982: 0.0104,
    1983: 0.0193, 1984: 0.0250, 1985: 0.0331, 1986: 0.0402,
    1987: 0.0477, 1988: 0.0598, 1989: 0.0724, 1990: 0.0831,
    1991: 0.0887, 1992: 0.0920, 1993: 0.0958, 1994: 0.0973,
    1995: 0.0989, 1996: 0.1012, 1997: 0.1030, 1998: 0.1053,
    1999: 0.1072, 2000: 0.1126, 2001: 0.1169, 2002: 0.1279,
    2003: 0.1306, 2004: 0.1337, 2005: 0.1391, 2006: 0.1452,
    2007: 0.1552, 2008: 0.1642, 2009: 0.1947, 2010: 0.2075,
    2011: 0.2112, 2012: 0.2248, 2013: 0.2342, 2014: 0.2415,
    2015: 0.2434, 2016: 0.2485, 2017: 0.2532, 2018: 0.2590,
    2019: 0.2678, 2020: 0.2724, 2021: 0.2841, 2022: 0.3004,
    2023: 0.3299, 2024: 0.3521, 2025: 0.3710, 2026: 0.3865,
}

# Sögulegir hlutir og áætluð verðlagssamanburður
BASKET_EXAMPLES = [
    {
        "item": "Líter af nýmjólk",
        "icon": "🥛",
        "price_1980": "6,50 gkr (0,065 kr)",
        "price_2000": "72 kr",
        "price_2026": "245 kr",
        "note": "Mjólk hefur haldist nokkuð nálægt almennri verðlagsþróun.",
    },
    {
        "item": "Bíómiði í Regnbogann / Laugarásbíó",
        "icon": "🎟️",
        "price_1980": "35 gkr (0,35 kr)",
        "price_2000": "650 kr",
        "price_2026": "2.190 kr",
        "note": "Miðaverð hefur hækkað umfram almenna verðbólgu vegna tæknibreytinga.",
    },
    {
        "item": "Meðal fermetraverð íbúðar í Reykjavík",
        "icon": "🏠",
        "price_1980": "3.200 gkr (32 kr)",
        "price_2000": "98.000 kr",
        "price_2026": "780.000 kr",
        "note": "Húsnæðisverð hefur hækkað margfalt hraðar en almennt vísitöluverðlag.",
    },
    {
        "item": "Almennur kaffibolli á kaffihúsi",
        "icon": "☕",
        "price_1980": "12 gkr (0,12 kr)",
        "price_2000": "220 kr",
        "price_2026": "750 kr",
        "note": "Kaffihúsamenning óx gríðarlega eftir 1990.",
    },
]


def calculate_purchasing_power(
    amount: float,
    start_year: int,
    target_year: int = 2026,
) -> Dict:
    """
    Reiknar jafngildi upphæðar á milli tveggja ára.
    Gagnlegt fyrir spurningar eins og 'hvað jafngilda 1000 kr frá 1990 í dag?'
    """
    if start_year not in CPI_SERIES_FULL or target_year not in CPI_SERIES_FULL:
        return {"error": "Ár verður að vera á bilinu 1939 til 2026"}

    cpi_start = CPI_SERIES_FULL[start_year]
    cpi_target = CPI_SERIES_FULL[target_year]

    ratio = cpi_target / cpi_start
    target_amount = amount * ratio

    years_diff = abs(target_year - start_year)
    annual_rate = 0.0
    if years_diff > 0:
        annual_rate = ((ratio ** (1.0 / years_diff)) - 1.0) * 100.0

    return {
        "start_year": start_year,
        "target_year": target_year,
        "start_amount": amount,
        "target_amount": target_amount,
        "ratio": ratio,
        "percent_change": (ratio - 1.0) * 100.0,
        "annual_compound_rate": annual_rate,
        "cpi_start": cpi_start,
        "cpi_target": cpi_target,
    }


def render_purchasing_power_html(res: Dict) -> str:
    """Skilar glæsilegu HTML-korti með útreikningi kaupmáttar."""
    start_y = res["start_year"]
    target_y = res["target_year"]
    amt_in = f"{res['start_amount']:,.0f}"
    amt_out = f"{res['target_amount']:,.0f}"
    pct = f"{res['percent_change']:+,.1f}%"
    ann = f"{res['annual_compound_rate']:.2f}%"

    return f"""
<div style="background: linear-gradient(145deg, #1A2E40 0%, #243C54 100%);
            border: 2px solid #C5A059; border-radius: 4px; padding: 2rem;
            color: #F5F4F0; box-shadow: 0 4px 16px rgba(0,0,0,0.35); margin: 1.5rem 0;">
    <div style="font-family: 'Cinzel', serif; font-size: 0.75rem; letter-spacing: 0.3em;
                color: #C5A059; text-transform: uppercase; margin-bottom: 0.5rem;">
        KAUPMÁTTARREIKNIVÉL &middot; AEQUALITAS PECUNIAE
    </div>
    <div style="font-family: 'Lora', Georgia, serif; font-size: 1.15rem; line-height: 1.6; margin-bottom: 1.5rem;">
        <span style="font-weight: 700; color: #FFFFFF;">{amt_in} kr.</span> árið 
        <span style="color: #C5A059; font-weight: 700;">{start_y}</span> 
        jafngilda um það bil:
    </div>
    <div style="font-family: 'Cinzel', serif; font-size: 2.5rem; font-weight: 700;
                color: #FFD700; letter-spacing: 0.05em; margin-bottom: 1.2rem; text-shadow: 0 2px 8px rgba(0,0,0,0.5);">
        {amt_out} kr.
    </div>
    <div style="font-family: 'Lora', serif; font-size: 0.92rem; color: #8FA5BC;
                border-top: 1px solid rgba(197,160,89,0.3); padding-top: 1rem;">
        Heildarverðbólga tímabilsins: <b style="color: #F5F4F0;">{pct}</b> &nbsp;&middot;&nbsp; 
        Meðaltal á ári: <b style="color: #F5F4F0;">{ann}</b>
    </div>
</div>
"""
