"""
visuals/report_exporter.py - Stofnanamat og Skýrslugerð Hagstofu Íslands

Býr til fullbúin, prenthæf tölfræðiskjöl (Executive Statistical Dossier) á HTML-formi
með opinberu útliti, gagnafylkjum, vottunarmerkjum og niðurhalsvirkni.
"""

import base64
import html
import time
from typing import Dict, List, Optional


def build_full_html_report(
    query: str,
    answer: str,
    table_id: str,
    table_title: str,
    source_url: str,
    facts: List[str],
    structured_data: Optional[List[Dict]] = None,
    action: str = "FETCH_LATEST",
    latency: float = 0.15,
) -> str:
    """Býr til fullkomið prenthæft HTML-skjal sem hægt er að vista sem PDF eða prenta."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    safe_query = html.escape(query)
    safe_answer = html.escape(answer).replace("\n", "<br>")

    facts_html = ""
    for f in facts:
        facts_html += f"<li style='margin-bottom: 0.4rem;'><code>{html.escape(f)}</code></li>"

    table_rows_html = ""
    if structured_data:
        for row in structured_data:
            table_rows_html += "<tr>"
            for k, v in row.items():
                table_rows_html += f"<td style='padding: 8px 12px; border: 1px solid #CFC4B2;'>{html.escape(str(v))}</td>"
            table_rows_html += "</tr>"

    return f"""<!DOCTYPE html>
<html lang="is">
<head>
    <meta charset="UTF-8">
    <title>Tölfræðiskýrsla &middot; Hagstofa Íslands &middot; {table_id}</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Lora:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        @media print {{
            body {{ background: #FFFFFF !important; color: #000000 !important; font-size: 11pt; }}
            .no-print {{ display: none !important; }}
            .report-card {{ box-shadow: none !important; border: 1px solid #888888 !important; }}
        }}
        body {{
            background-color: #F4EFE6;
            font-family: 'Lora', Georgia, serif;
            color: #1A2530;
            margin: 0;
            padding: 2.5rem 1rem;
            line-height: 1.6;
        }}
        .report-card {{
            max-width: 820px;
            margin: 0 auto;
            background: #FFFFFF;
            border: 2px solid #C5A059;
            border-radius: 4px;
            padding: 3rem;
            box-shadow: 0 6px 24px rgba(0,0,0,0.15);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #C5A059;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}
        .institution {{
            font-family: 'Cinzel', serif;
            font-size: 0.8rem;
            letter-spacing: 0.3em;
            color: #8B6914;
            text-transform: uppercase;
        }}
        .title {{
            font-family: 'Cinzel', serif;
            font-size: 2rem;
            font-weight: 700;
            color: #1A2E40;
            margin: 0.5rem 0;
            letter-spacing: 0.05em;
        }}
        .badge {{
            display: inline-block;
            font-family: 'Cinzel', serif;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.15em;
            padding: 0.25rem 0.75rem;
            border-radius: 2px;
            text-transform: uppercase;
            background: #EDE8E1;
            color: #1A2E40;
            border: 1px solid #C5A059;
        }}
        .query-box {{
            background: #FAF8F5;
            border-left: 4px solid #C5A059;
            padding: 1.2rem 1.5rem;
            margin: 1.5rem 0;
            border-radius: 2px;
        }}
        .answer-box {{
            background: #F4EFE6;
            border: 1px solid #DDD8D0;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 2px;
            font-size: 1.05rem;
            line-height: 1.8;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            font-size: 0.95rem;
        }}
        th {{
            font-family: 'Cinzel', serif;
            background: #1A2E40;
            color: #F5F4F0;
            text-align: left;
            padding: 10px 12px;
            font-size: 0.8rem;
            letter-spacing: 0.1em;
        }}
        code {{
            font-family: 'JetBrains Mono', monospace;
            background: #EAE6DF;
            padding: 2px 6px;
            border-radius: 2px;
            font-size: 0.9em;
        }}
        .footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid #DDD8D0;
            font-size: 0.85rem;
            color: #6C7A89;
            display: flex;
            justify-content: space-between;
        }}
    </style>
</head>
<body>
    <div class="report-card">
        <div class="header">
            <div class="institution">HAGSTOFA ÍSLANDS &middot; STATISTICS ICELAND</div>
            <div class="title">TÖLFRÆÐISKÝRSLA</div>
            <div style="font-style: italic; color: #5A4A32;">Opinber gagnasókn og greining fyrirspurnar</div>
            <div style="margin-top: 0.9rem;">
                <span class="badge">TAFLA: {table_id}</span> &nbsp;
                <span class="badge">AÐGERÐ: {action}</span> &nbsp;
                <span class="badge">VINNSLA: {latency:.2f}S</span>
            </div>
        </div>

        <div class="query-box">
            <div style="font-family: 'Cinzel', serif; font-size: 0.7rem; font-weight: 700; color: #8B6914; letter-spacing: 0.2em; text-transform: uppercase;">
                FYRIRSPURN NOTANDA
            </div>
            <div style="font-size: 1.15rem; font-weight: 600; color: #1A2530; margin-top: 0.3rem;">
                "{safe_query}"
            </div>
        </div>

        <div class="answer-box">
            <div style="font-family: 'Cinzel', serif; font-size: 0.7rem; font-weight: 700; color: #8B6914; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 0.6rem;">
                STAÐFEST NIÐURSTAÐA (ZERO HALLUCINATION)
            </div>
            {safe_answer}
        </div>

        <div style="margin: 2rem 0;">
            <h4 style="font-family: 'Cinzel', serif; color: #1A2E40; letter-spacing: 0.1em; margin-bottom: 0.6rem;">
                UPPRUNALÝSING OG GÖGN
            </h4>
            <p style="margin: 0.2rem 0;"><b>Gagnatafla:</b> {table_title} (<code>{table_id}</code>)</p>
            <p style="margin: 0.2rem 0;"><b>Vefslóð:</b> <a href="{source_url}" target="_blank" style="color: #8B6914;">{source_url}</a></p>
        </div>

        <div>
            <h4 style="font-family: 'Cinzel', serif; color: #1A2E40; letter-spacing: 0.1em; margin-bottom: 0.6rem;">
                SÓTTAR MÆLINGAR ÚR PX-WEB API
            </h4>
            <ul>
                {facts_html}
            </ul>
        </div>

        <div class="footer">
            <div>Gagnasvarari Hagstofu Íslands &middot; Kerfisútgáfa 2026.1</div>
            <div>Skjalið var útbúið: {timestamp}</div>
        </div>
    </div>
</body>
</html>"""


def get_downloadable_report_b64(html_content: str) -> str:
    """Umbreytir HTML skjali í base64 streng fyrir hlekk/hnapp."""
    return base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
