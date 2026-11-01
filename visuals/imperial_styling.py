"""
visuals/imperial_styling.py - Keisaralegt Myndmál, Hljóðáhrif og Latneskt Tölfræðiorðasafn

Inniheldur latnesk hugtök fyrir allar hagstærðir, lárviðarsveiga (Corona Triumphalis),
súluskreytingar í SVG og hljóðbylgjur fyrir rómverska lúðra og hörpuhljóma.
"""

import base64
import math
import struct
from typing import Dict, List, Optional

STATISTICAL_LATIN_GLOSSARY = {
    "mannfjoldi": {"latin": "NUMERUS INCOLARUM", "desc": "Mannfjöldi og íbúafjöldi"},
    "verdbolga": {"latin": "INFLATIO MONETARIA", "desc": "Verðbólga og rýrnun peningamagns"},
    "buferlaflutningar": {"latin": "MIGRATIO DOMESTICA", "desc": "Búferlaflutningar milli héraða"},
    "sveitarfelag": {"latin": "MUNICIPIUM", "desc": "Sveitarfélag og staðbundin stjórnsýsla"},
    "visitala": {"latin": "INDEX VALORIS", "desc": "Vísitala og mælistika"},
    "laun": {"latin": "MERCES ET REMUNERATIO", "desc": "Laun og endurgjald fyrir vinnu"},
    "atvinnuleysi": {"latin": "VACATIO LABORIS", "desc": "Atvinnuleysi og hlutfall án vinnu"},
    "ibuar": {"latin": "CIVES ET HABITATORES", "desc": "Íbúar og ríkisborgarar"},
    "faeddir": {"latin": "NATI VIVENTES", "desc": "Lifandi fædd börn"},
    "danir": {"latin": "MORTUI ET DECEDENTES", "desc": "Dánir og dánartíðni"},
    "ferdamenn": {"latin": "PEREGRINI ET HOSPES", "desc": "Erlendir ferðamenn og gestir"},
    "reykjavik": {"latin": "CIVITAS REYKIAVIKENSIS", "desc": "Höfuðborgin Reykjavík"},
    "hagstofa": {"latin": "OFFICIUM STATISTICUM", "desc": "Hagstofa og tölfræðistofnun"},
    "timabil": {"latin": "AETAS ET TEMPORA", "desc": "Tímabil og árabil"},
}


def generate_chime_wav_b64(frequency: float = 523.25, duration: float = 0.55) -> str:
    """Býr til hreinan WAV-hljóm (harp / lyre chime) í base64 án ytri hljóðskráa."""
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    wav_data = bytearray()

    for i in range(num_samples):
        t = float(i) / sample_rate
        # Hljómur með harmónískum yfirtónum (hörpulíkt)
        decay = math.exp(-4.5 * t)
        sample = (
            0.6 * math.sin(2.0 * math.pi * frequency * t) +
            0.25 * math.sin(2.0 * math.pi * (frequency * 2.0) * t) +
            0.15 * math.sin(2.0 * math.pi * (frequency * 3.0) * t)
        ) * decay
        val = int(sample * 32767.0 * 0.4)
        val = max(-32768, min(32767, val))
        wav_data.extend(struct.pack("<h", val))

    # WAV haus
    byte_rate = sample_rate * 2
    block_align = 2
    subchunk2_size = num_samples * 2
    chunk_size = 36 + subchunk2_size

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", chunk_size, b"WAVE",
        b"fmt ", 16, 1, 1, sample_rate, byte_rate, block_align, 16,
        b"data", subchunk2_size
    )

    full_wav = header + wav_data
    return base64.b64encode(full_wav).decode("ascii")


def generate_laurel_wreath_svg(width: int = 120, height: int = 70) -> str:
    """Býr til gullinn lárviðarsveig (Corona Triumphalis) í SVG."""
    return f"""
<svg width="{width}" height="{height}" viewBox="0 0 140 80" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="laurelGold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFE082" />
      <stop offset="50%" stop-color="#C5A059" />
      <stop offset="100%" stop-color="#8B6914" />
    </linearGradient>
  </defs>
  <!-- Vinstri grein -->
  <g fill="url(#laurelGold)" stroke="#664D03" stroke-width="0.5">
    <path d="M 65 72 C 45 70 25 55 22 35 C 20 22 28 12 36 6 C 35 15 40 25 48 32 C 55 38 62 40 68 45 Z" opacity="0.85" />
    <path d="M 45 65 C 32 60 20 48 18 36 C 26 38 34 44 40 52 Z" />
    <path d="M 32 45 C 22 38 14 26 15 15 C 22 19 28 26 32 35 Z" />
    <path d="M 28 25 C 22 18 18 10 24 2 C 28 7 31 14 32 22 Z" />
  </g>
  <!-- Hægri grein (spegluð) -->
  <g fill="url(#laurelGold)" stroke="#664D03" stroke-width="0.5" transform="translate(140, 0) scale(-1, 1)">
    <path d="M 65 72 C 45 70 25 55 22 35 C 20 22 28 12 36 6 C 35 15 40 25 48 32 C 55 38 62 40 68 45 Z" opacity="0.85" />
    <path d="M 45 65 C 32 60 20 48 18 36 C 26 38 34 44 40 52 Z" />
    <path d="M 32 45 C 22 38 14 26 15 15 C 22 19 28 26 32 35 Z" />
    <path d="M 28 25 C 22 18 18 10 24 2 C 28 7 31 14 32 22 Z" />
  </g>
  <!-- Borði neðst -->
  <path d="M 58 72 L 70 68 L 82 72 L 75 78 L 70 75 L 65 78 Z" fill="#8B6914" />
</svg>
"""


def render_roman_column_svg(height: int = 380) -> str:
    """Býr til rómverska súlu (Columna Dorica) í SVG til að ramma inn efni."""
    return f"""
<svg width="24" height="{height}" viewBox="0 0 24 {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="colGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#C5A059" stop-opacity="0.8" />
      <stop offset="30%" stop-color="#F5E6CC" stop-opacity="0.9" />
      <stop offset="70%" stop-color="#C5A059" stop-opacity="0.8" />
      <stop offset="100%" stop-color="#8B6914" stop-opacity="0.9" />
    </linearGradient>
  </defs>
  <!-- Höfuð (Capital) -->
  <rect x="1" y="2" width="22" height="6" fill="#8B6914" rx="1" />
  <rect x="3" y="8" width="18" height="4" fill="#C5A059" />
  <!-- Súlubolur (Shaft) -->
  <rect x="5" y="12" width="14" height="{height - 24}" fill="url(#colGrad)" />
  <line x1="8" y1="12" x2="8" y2="{height - 12}" stroke="#8B6914" stroke-width="0.75" opacity="0.6" />
  <line x1="12" y1="12" x2="12" y2="{height - 12}" stroke="#8B6914" stroke-width="0.75" opacity="0.6" />
  <line x1="16" y1="12" x2="16" y2="{height - 12}" stroke="#8B6914" stroke-width="0.75" opacity="0.6" />
  <!-- Fótur (Base) -->
  <rect x="3" y="{height - 12}" width="18" height="4" fill="#C5A059" />
  <rect x="1" y="{height - 8}" width="22" height="6" fill="#8B6914" rx="1" />
</svg>
"""


def render_glossary_grid_html() -> str:
    """Býr til orðasafn yfir helstu latnesku heitin á hagstærðum."""
    cards_html = ""
    for k, v in STATISTICAL_LATIN_GLOSSARY.items():
        cards_html += f"""
<div style="background: #EDE8E1; border: 1px solid #C5A059; border-radius: 2px;
            padding: 0.8rem 1rem; margin-bottom: 0.6rem;">
    <div style="font-family: 'Cinzel', serif; font-size: 0.75rem; font-weight: 700;
                color: #8B6914; letter-spacing: 0.15em;">
        {v['latin']}
    </div>
    <div style="font-family: 'Lora', serif; font-size: 0.95rem; color: #1A2530; margin-top: 0.2rem;">
        {v['desc']}
    </div>
</div>
"""
    return f"""
<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 0.75rem;">
    {cards_html}
</div>
"""
