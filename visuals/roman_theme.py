"""
visuals/roman_theme.py - Rómverskt Þema, Rómverskar Tölur og Keisaralegar Tilskipanir

Inniheldur rómverska tölubreytara, latneskar áletranir, keisaraleg innsigli
og tilskipanir á pappaformi (parchment decrees) með vaxinnsigli.
"""

from typing import Dict, List, Optional, Tuple

ROMAN_NUMERAL_TABLE = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
]

LATIN_MOTTOES = [
    {"latin": "VERITAS PER NUMEROS", "is": "Sannleikur í gegnum tölur"},
    {"latin": "SENATUS POPULUSQUE ISLANDIAE", "is": "Öldungaráð og lýður Íslands"},
    {"latin": "NUMERI NON MENTIUNTUR", "is": "Tölurnar ljúga ekki"},
    {"latin": "CIVITAS IN LIBRIS DESCRIPTA", "is": "Borgarsamfélagið skráð í bókum"},
    {"latin": "STATISTICA PUBLICA INVIOLABILIS", "is": "Opinber tölfræði er friðhelg"},
]

THEME_PALETTES = {
    "classic_navy": {
        "name": "Imperium Classicum (Klassískt Navy & Gull)",
        "bg_main": "#243C54",
        "bg_header": "linear-gradient(160deg, #2A445E 0%, #1A2E40 100%)",
        "primary_gold": "#C5A059",
        "accent_gold": "#FFD700",
        "text_light": "#F5F4F0",
        "msg_bg": "#EAE3D6",
        "border_color": "#C5A059",
    },
    "tyrian_purple": {
        "name": "Purpura Imperialis (Keisaralegur Purpuri)",
        "bg_main": "#2C1B2E",
        "bg_header": "linear-gradient(160deg, #4A1E42 0%, #220F24 100%)",
        "primary_gold": "#E5B95C",
        "accent_gold": "#FFE27A",
        "text_light": "#FDF8F0",
        "msg_bg": "#EFE6DA",
        "border_color": "#E5B95C",
    },
    "marmor_carrara": {
        "name": "Marmor Carrara (Ljóst Marmaraþema)",
        "bg_main": "#E8E2D8",
        "bg_header": "linear-gradient(160deg, #F4EFE6 0%, #DFD7C7 100%)",
        "primary_gold": "#8B6914",
        "accent_gold": "#A07828",
        "text_light": "#1A2530",
        "msg_bg": "#FFFFFF",
        "border_color": "#8B6914",
    },
    "aeneas_bronze": {
        "name": "Aeneas Bronze (Dökkt Eir & Patína)",
        "bg_main": "#1E2522",
        "bg_header": "linear-gradient(160deg, #2D3A34 0%, #17201C 100%)",
        "primary_gold": "#CD7F32",
        "accent_gold": "#E3A857",
        "text_light": "#EFEFE8",
        "msg_bg": "#E2DCD2",
        "border_color": "#CD7F32",
    },
}


def to_roman_numerals(n: int) -> str:
    """Breytir heiltölu í rómverskar tölur (t.d. 2026 -> MMXXVI)."""
    if not (0 < n < 4000):
        return str(n)
    result = []
    for val, numeral in ROMAN_NUMERAL_TABLE:
        while n >= val:
            result.append(numeral)
            n -= val
    return "".join(result)


def from_roman_numerals(roman: str) -> int:
    """Breytir rómverskri tölu í heiltölu."""
    roman = roman.upper().strip()
    roman_map = {"M": 1000, "D": 500, "C": 100, "L": 50, "X": 10, "V": 5, "I": 1}
    total = 0
    prev_val = 0
    for char in reversed(roman):
        val = roman_map.get(char, 0)
        if val >= prev_val:
            total += val
        else:
            total -= val
        prev_val = val
    return total


def generate_wax_seal_svg(size: int = 110) -> str:
    """Býr til ítarlegt rómverskt vaxinnsigli í SVG með áletrun Hagstofu."""
    return f"""
<svg width="{size}" height="{size}" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="waxGrad" cx="35%" cy="35%" r="70%">
      <stop offset="0%" stop-color="#C53030" />
      <stop offset="60%" stop-color="#821818" />
      <stop offset="100%" stop-color="#4A0E0E" />
    </radialGradient>
    <filter id="sealShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="2" dy="4" stdDeviation="3" flood-color="#000000" flood-opacity="0.5" />
    </filter>
  </defs>
  <circle cx="60" cy="60" r="54" fill="url(#waxGrad)" filter="url(#sealShadow)" stroke="#4A0E0E" stroke-width="1.5" />
  <circle cx="60" cy="60" r="46" fill="none" stroke="#D48888" stroke-width="1" stroke-dasharray="2,3" opacity="0.6" />
  <circle cx="60" cy="60" r="39" fill="none" stroke="#661010" stroke-width="1" />
  <!-- Rómverskur örn eða tákn -->
  <path d="M 60 36 L 68 50 L 60 48 L 52 50 Z" fill="#D48888" opacity="0.85" />
  <text x="60" y="67" text-anchor="middle" font-family="'Cinzel', serif" font-size="11" font-weight="700" fill="#F8D7DA" letter-spacing="1">HÍ</text>
  <text x="60" y="80" text-anchor="middle" font-family="'Cinzel', serif" font-size="7" fill="#E2A8A8" letter-spacing="1.5">MMXXVI</text>
  <path id="sealTextPath" d="M 24 60 A 36 36 0 1 1 96 60" fill="none" />
  <text font-family="'Cinzel', serif" font-size="6" fill="#F8D7DA" letter-spacing="2">
    <textPath href="#sealTextPath" startOffset="50%" text-anchor="middle">
      HAGSTOFA ISLANDIAE
    </textPath>
  </text>
</svg>
"""


def generate_imperial_decree_html(
    title: str,
    body_text: str,
    source_table: str,
    date_str: str = "Anno Domini MMXXVI",
) -> str:
    """Býr til prenthæfa keisaralega tilskipun á vönduðu pergamenti."""
    seal_svg = generate_wax_seal_svg(95)
    return f"""
<div style="background-color: #F4EFE6;
            background-image: radial-gradient(#E8DFC8 15%, transparent 16%);
            background-size: 20px 20px;
            border: 3px double #8B6914; border-radius: 6px;
            padding: 3rem 2.5rem 2.5rem 2.5rem;
            color: #1A2530; box-shadow: 0 8px 30px rgba(0,0,0,0.35);
            max-width: 740px; margin: 2rem auto; position: relative;">
    
    <!-- Skrautrammi -->
    <div style="border: 1px solid #C5A059; padding: 2rem; position: relative;">
        <div style="text-align: center; font-family: 'Cinzel', Georgia, serif;">
            <div style="font-size: 0.75rem; letter-spacing: 0.4em; color: #8B6914; text-transform: uppercase;">
                SENATUS POPULUSQUE ISLANDIAE
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #1A2530; margin: 0.6rem 0; letter-spacing: 0.1em;">
                SENATUS CONSULTUM
            </div>
            <div style="font-size: 0.95rem; color: #5A4A32; font-style: italic; font-family: 'Lora', serif;">
                Opinber vitnisburður Hagstofu Íslands
            </div>
            <div style="width: 80px; height: 1.5px; background: #8B6914; margin: 1rem auto;"></div>
        </div>

        <div style="font-family: 'Lora', Georgia, serif; font-size: 1.05rem; line-height: 1.85; color: #1A2530; margin: 2rem 0; text-align: justify;">
            <p style="font-weight: 700; font-size: 1.15rem; color: #8B6914; margin-bottom: 0.8rem;">
                {title}
            </p>
            <p>
                {body_text}
            </p>
            <p style="font-size: 0.9rem; color: #5A4A32; font-style: italic; margin-top: 1.5rem;">
                Gögn sótt beint í opinberan gagnagrunn Hagstofu Íslands samkvæmt gildandi lögum um hagtölur.
                Upprunatafla: <b>{source_table}</b>.
            </p>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 2.5rem; border-top: 1px solid rgba(139,105,20,0.3); padding-top: 1.5rem;">
            <div>
                <div style="font-family: 'Cinzel', serif; font-size: 0.75rem; letter-spacing: 0.2em; color: #8B6914;">
                    GEFIÐ ÚT ÞANN
                </div>
                <div style="font-family: 'Lora', serif; font-size: 0.95rem; font-style: italic;">
                    {date_str}
                </div>
            </div>
            <div style="margin-right: 1.5rem;">
                {seal_svg}
            </div>
        </div>
    </div>
</div>
"""
