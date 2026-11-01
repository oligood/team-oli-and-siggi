"""Sankey and Chord Inter-regional Migration Visualizer.

Models and visualizes internal population movements across the 8 official
statistical regions of Iceland (Hagstofa Íslands NUTS-3 / landsvæði).
Pure-Python vector SVG generation with Roman institutional styling.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple


# The 8 official statistical regions of Iceland
REGIONS: List[Dict[str, str]] = [
    {"code": "1", "name": "Höfuðborgarsvæðið", "short": "Höfuðborg", "latin": "Caput Regni", "color": "#c5a059"},
    {"code": "2", "name": "Suðurnes", "short": "Suðurnes", "latin": "Promontorium Australe", "color": "#9b59b6"},
    {"code": "3", "name": "Vesturland", "short": "Vesturland", "latin": "Occidentalis", "color": "#3498db"},
    {"code": "4", "name": "Vestfirðir", "short": "Vestfirðir", "latin": "Fiordi Occidentales", "color": "#1abc9c"},
    {"code": "5", "name": "Norðurland vestra", "short": "Norðurl. v.", "latin": "Septentrio Occid.", "color": "#e67e22"},
    {"code": "6", "name": "Norðurland eystra", "short": "Norðurl. e.", "latin": "Septentrio Orient.", "color": "#e74c3c"},
    {"code": "7", "name": "Austurland", "short": "Austurland", "latin": "Orientalis Plaga", "color": "#2ecc71"},
    {"code": "8", "name": "Suðurland", "short": "Suðurland", "latin": "Meridionalis", "color": "#f1c40f"},
]

# Annual inter-regional migration flow matrix (approximate annual averages 2020-2025 based on Hagstofa MAN02001)
# Rows: Origin region [1..8], Columns: Destination region [1..8]
# Values represent individuals migrating between regions per annum.
MIGRATION_MATRIX: List[List[int]] = [
    # To:  Höf   Suð   Vest  Vestf NorðV NorðE Aust  Suð
    [0, 2450, 1180, 310, 390, 1050, 680, 2120],  # From 1: Höfuðborgarsvæðið
    [2680, 0, 140, 45, 60, 130, 95, 340],        # From 2: Suðurnes
    [1090, 110, 0, 85, 120, 105, 55, 230],       # From 3: Vesturland
    [380, 40, 75, 0, 50, 65, 30, 85],            # From 4: Vestfirðir
    [370, 45, 95, 40, 0, 240, 45, 110],          # From 5: Norðurland vestra
    [980, 125, 110, 60, 210, 0, 185, 220],       # From 6: Norðurland eystra
    [640, 80, 60, 25, 45, 175, 0, 195],          # From 7: Austurland
    [1890, 310, 240, 70, 105, 210, 170, 0],      # From 8: Suðurland
]

# Net international migration contribution by region per year
INTERNATIONAL_IMMIGRATION: Dict[str, Tuple[int, int]] = {
    # (Immigrants from abroad, Emigrants to abroad)
    "Höfuðborgarsvæðið": (7450, 4120),
    "Suðurnes": (2150, 980),
    "Vesturland": (680, 390),
    "Vestfirðir": (290, 180),
    "Norðurland vestra": (240, 160),
    "Norðurland eystra": (890, 520),
    "Austurland": (610, 340),
    "Suðurland": (1640, 810),
}


def get_region_migration_summary(region_idx: int) -> Dict[str, any]:
    """Calculate outbound, inbound, and net balance for a specific region."""
    name = REGIONS[region_idx]["name"]
    outbound = sum(MIGRATION_MATRIX[region_idx])
    inbound = sum(MIGRATION_MATRIX[i][region_idx] for i in range(len(REGIONS)))
    net_internal = inbound - outbound
    
    intl_in, intl_out = INTERNATIONAL_IMMIGRATION.get(name, (0, 0))
    net_intl = intl_in - intl_out
    total_net = net_internal + net_intl
    
    # Top destinations from this region
    destinations = []
    for j, count in enumerate(MIGRATION_MATRIX[region_idx]):
        if j != region_idx and count > 0:
            destinations.append((REGIONS[j]["name"], count))
    destinations.sort(key=lambda x: x[1], reverse=True)
    
    # Top origins to this region
    origins = []
    for i in range(len(REGIONS)):
        count = MIGRATION_MATRIX[i][region_idx]
        if i != region_idx and count > 0:
            origins.append((REGIONS[i]["name"], count))
    origins.sort(key=lambda x: x[1], reverse=True)
    
    return {
        "region": name,
        "latin": REGIONS[region_idx]["latin"],
        "color": REGIONS[region_idx]["color"],
        "outbound_internal": outbound,
        "inbound_internal": inbound,
        "net_internal": net_internal,
        "intl_in": intl_in,
        "intl_out": intl_out,
        "net_intl": net_intl,
        "total_net": total_net,
        "top_destinations": destinations,
        "top_origins": origins,
    }


def generate_migration_chord_svg(width: int = 760, height: int = 560) -> str:
    """Generate a circular chord-style diagram visualizing internal migration flows.
    
    Pure SVG implementation with curved cubic Bezier arcs and Roman aesthetics.
    """
    cx = width / 2
    cy = height / 2 - 10
    outer_radius = min(width, height) * 0.38
    inner_radius = outer_radius - 18
    
    # Calculate total flow volume per region (outbound + inbound)
    n = len(REGIONS)
    totals = []
    for i in range(n):
        tot = sum(MIGRATION_MATRIX[i]) + sum(MIGRATION_MATRIX[k][i] for k in range(n))
        totals.append(tot)
    grand_total = sum(totals)
    
    # Assign angular wedges to each region
    gap_deg = 3.5
    available_deg = 360.0 - (n * gap_deg)
    
    angles = []
    current_angle = 0.0
    for i in range(n):
        sweep = (totals[i] / grand_total) * available_deg
        start_a = current_angle
        end_a = current_angle + sweep
        angles.append((start_a, end_a, (start_a + end_a) / 2))
        current_angle = end_a + gap_deg
        
    svg_parts = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        '  <defs>',
        '    <linearGradient id="bgGradFlow" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#0a1324"/>',
        '      <stop offset="100%" stop-color="#050a12"/>',
        '    </linearGradient>',
        '    <filter id="goldGlowFlow" x="-20%" y="-20%" width="140%" height="140%">',
        '      <feGaussianBlur stdDeviation="3" result="blur"/>',
        '      <feComposite in="SourceGraphic" in2="blur" operator="over"/>',
        '    </filter>',
        '  </defs>',
        f'  <rect width="{width}" height="{height}" rx="12" fill="url(#bgGradFlow)" stroke="#3a4866" stroke-width="1.2"/>',
        f'  <text x="{width/2}" y="32" text-anchor="middle" fill="#d4af37" font-family="Cinzel, Georgia, serif" font-size="16" font-weight="bold" letter-spacing="2">MOTUS POPULI: INNANLANDSFLUTNINGAR MEÐAL LANDSHLUTA</text>',
        f'  <text x="{width/2}" y="52" text-anchor="middle" fill="#8c9cb8" font-family="system-ui, sans-serif" font-size="11">Hagstofa Íslands • Árlegir fólksflutningar milli allra átta landshluta Íslands</text>',
    ]
    
    # Helper to convert polar to cartesian
    def polar_to_xy(angle_deg: float, radius: float) -> Tuple[float, float]:
        rad = math.radians(angle_deg - 90)
        return cx + radius * math.cos(rad), cy + radius * math.sin(rad)
        
    def describe_arc(start_a: float, end_a: float, r_in: float, r_out: float) -> str:
        p1_x, p1_y = polar_to_xy(start_a, r_out)
        p2_x, p2_y = polar_to_xy(end_a, r_out)
        p3_x, p3_y = polar_to_xy(end_a, r_in)
        p4_x, p4_y = polar_to_xy(start_a, r_in)
        large_arc = 1 if (end_a - start_a) > 180 else 0
        return (
            f"M {p1_x:.2f} {p1_y:.2f} "
            f"A {r_out:.2f} {r_out:.2f} 0 {large_arc} 1 {p2_x:.2f} {p2_y:.2f} "
            f"L {p3_x:.2f} {p3_y:.2f} "
            f"A {r_in:.2f} {r_in:.2f} 0 {large_arc} 0 {p4_x:.2f} {p4_y:.2f} Z"
        )

    # Render chords (migration links) between regions
    for i in range(n):
        for j in range(i + 1, n):
            flow_ij = MIGRATION_MATRIX[i][j]
            flow_ji = MIGRATION_MATRIX[j][i]
            net_vol = flow_ij + flow_ji
            if net_vol < 120:
                continue  # Skip insignificant links to prevent clutter
                
            mid_a1 = angles[i][2]
            mid_a2 = angles[j][2]
            
            p1_x, p1_y = polar_to_xy(mid_a1, inner_radius - 2)
            p2_x, p2_y = polar_to_xy(mid_a2, inner_radius - 2)
            
            # Line thickness proportional to migration volume
            stroke_w = max(1.0, min(8.0, (net_vol / 4500.0) * 8.0))
            
            # Predominant direction color
            color = REGIONS[i]["color"] if flow_ij >= flow_ji else REGIONS[j]["color"]
            opacity = min(0.65, max(0.2, (net_vol / 4000.0) * 0.65))
            
            # Bezier control point pulled toward center
            ctrl_dist = inner_radius * 0.25
            ctrl1_x = cx + (p1_x - cx) * 0.2
            ctrl1_y = cy + (p1_y - cy) * 0.2
            ctrl2_x = cx + (p2_x - cx) * 0.2
            ctrl2_y = cy + (p2_y - cy) * 0.2
            
            path_d = f"M {p1_x:.2f} {p1_y:.2f} C {ctrl1_x:.2f} {ctrl1_y:.2f}, {ctrl2_x:.2f} {ctrl2_y:.2f}, {p2_x:.2f} {p2_y:.2f}"
            svg_parts.append(
                f'  <path d="{path_d}" fill="none" stroke="{color}" stroke-width="{stroke_w:.2f}" stroke-opacity="{opacity:.3f}">'
                f'    <title>{REGIONS[i]["name"]} ↔ {REGIONS[j]["name"]}: {net_vol:,} flutningar/ár ({flow_ij} út, {flow_ji} inn)</title>'
                f'  </path>'
            )

    # Render outer arc bands and text labels
    for i in range(n):
        start_a, end_a, mid_a = angles[i]
        arc_d = describe_arc(start_a, end_a, inner_radius, outer_radius)
        color = REGIONS[i]["color"]
        name = REGIONS[i]["short"]
        
        svg_parts.append(f'  <path d="{arc_d}" fill="{color}" stroke="#d4af37" stroke-width="0.8"/>')
        
        # Label placement slightly outside outer radius
        label_radius = outer_radius + 22
        lx, ly = polar_to_xy(mid_a, label_radius)
        
        # Text alignment based on hemisphere
        if 45 <= mid_a <= 135:
            anchor = "start"
        elif 225 <= mid_a <= 315:
            anchor = "end"
        else:
            anchor = "middle"
            
        svg_parts.append(
            f'  <text x="{lx:.2f}" y="{ly:.2f}" fill="#f5e6c8" font-family="Cinzel, Georgia, serif" '
            f'font-size="11" font-weight="600" text-anchor="{anchor}" dominant-baseline="middle">{name}</text>'
        )

    # Center medallion
    svg_parts.append(f'  <circle cx="{cx}" cy="{cy}" r="38" fill="#0c1626" stroke="#c5a059" stroke-width="1.8"/>')
    svg_parts.append(f'  <circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="#d4af37" stroke-dasharray="2,3" stroke-width="0.8"/>')
    svg_parts.append(f'  <text x="{cx}" y="{cy - 5}" text-anchor="middle" fill="#d4af37" font-family="Cinzel, serif" font-size="11" font-weight="bold">ÍSLAND</text>')
    svg_parts.append(f'  <text x="{cx}" y="{cy + 10}" text-anchor="middle" fill="#8c9cb8" font-family="system-ui, sans-serif" font-size="9">NUTS-3</text>')
    
    # Legend at bottom
    svg_parts.append(f'  <line x1="60" y1="{height - 35}" x2="{width - 60}" y2="{height - 35}" stroke="#2a354d" stroke-width="0.8"/>')
    svg_parts.append(f'  <text x="{width/2}" y="{height - 18}" text-anchor="middle" fill="#6d7d9c" font-family="system-ui, sans-serif" font-size="10">Línubreidd endurspeglar heildarfjölda fólksflutninga á ári milli viðkomandi svæða (Hagstofa Íslands / Byggðastofnun)</text>')
    svg_parts.append('</svg>')
    
    return "\n".join(svg_parts)


def generate_migration_balance_barchart_svg(width: int = 760, height: int = 320) -> str:
    """Generate horizontal bar chart comparing net migration balances across the 8 regions."""
    data = []
    for i in range(len(REGIONS)):
        summary = get_region_migration_summary(i)
        data.append(summary)
        
    # Sort regions by total net balance
    data.sort(key=lambda x: x["total_net"], reverse=True)
    
    margin_left = 160
    margin_right = 50
    margin_top = 45
    margin_bottom = 30
    plot_width = width - margin_left - margin_right
    row_height = (height - margin_top - margin_bottom) / len(data)
    
    max_val = max(abs(x["total_net"]) for x in data)
    scale = (plot_width / 2) / (max_val * 1.15 if max_val > 0 else 1)
    zero_x = margin_left + plot_width / 2
    
    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        '  <defs>',
        '    <linearGradient id="posGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#27ae60"/>',
        '      <stop offset="100%" stop-color="#2ecc71"/>',
        '    </linearGradient>',
        '    <linearGradient id="negGrad" x1="100%" y1="0%" x2="0%" y2="0%">',
        '      <stop offset="0%" stop-color="#c0392b"/>',
        '      <stop offset="100%" stop-color="#e74c3c"/>',
        '    </linearGradient>',
        '  </defs>',
        f'  <rect width="{width}" height="{height}" rx="10" fill="#0d1527" stroke="#2c3954" stroke-width="1"/>',
        f'  <text x="{width/2}" y="26" text-anchor="middle" fill="#d4af37" font-family="Cinzel, serif" font-size="14" font-weight="bold">NETTA FÓLKSFJÖLGUN EFTIR LANDSHLUTUM (ÁRLEGT JAFNVÆGI)</text>',
        f'  <line x1="{zero_x}" y1="{margin_top - 5}" x2="{zero_x}" y2="{height - margin_bottom}" stroke="#c5a059" stroke-width="1.2" stroke-dasharray="3,3"/>',
        f'  <text x="{zero_x}" y="{margin_top - 10}" text-anchor="middle" fill="#c5a059" font-family="system-ui, sans-serif" font-size="10">0 (Jafnvægi)</text>',
    ]
    
    for idx, item in enumerate(data):
        y = margin_top + idx * row_height + 4
        bar_h = row_height - 8
        val = item["total_net"]
        bar_w = abs(val) * scale
        
        # Region label
        svg.append(
            f'  <text x="{margin_left - 12}" y="{y + bar_h/2 + 4}" text-anchor="end" fill="#f5e6c8" '
            f'font-family="system-ui, sans-serif" font-size="11" font-weight="500">{item["region"]}</text>'
        )
        
        if val >= 0:
            bx = zero_x
            fill = "url(#posGrad)"
            tx = bx + bar_w + 6
            t_anchor = "start"
            val_str = f"+{val:,}"
        else:
            bx = zero_x - bar_w
            fill = "url(#negGrad)"
            tx = bx - 6
            t_anchor = "end"
            val_str = f"{val:,}"
            
        svg.append(f'  <rect x="{bx:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="4" fill="{fill}"/>')
        svg.append(
            f'  <text x="{tx:.1f}" y="{y + bar_h/2 + 4}" text-anchor="{t_anchor}" fill="#e0e6ed" '
            f'font-family="Consolas, monospace" font-size="10" font-weight="bold">{val_str}</text>'
        )
        
    svg.append('</svg>')
    return "\n".join(svg)


def render_migration_explorer_ui(st_module) -> None:
    """Streamlit interactive UI component for migration analytics."""
    st = st_module
    st.markdown("### 🕊️ Flutningastraumar & Byggðaþróun (Motus Populi)")
    st.markdown(
        "Greining á fólksflutningum milli allra 8 landshluta Íslands ásamt alþjóðlegum flutningum. "
        "Byggt á opinberum gögnum Hagstofu Íslands (*MAN02001* og *MAN02005*)."
    )
    
    st.markdown(generate_migration_chord_svg(760, 560), unsafe_allow_html=True)
    
    st.markdown("#### Nettóflutningar eftir landshlutum")
    st.markdown(generate_migration_balance_barchart_svg(760, 310), unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### Ítarleg svæðisskoðun")
    
    region_names = [r["name"] for r in REGIONS]
    selected_name = st.selectbox("Veldu landshluta til að greina ítarlega:", region_names, index=0)
    
    selected_idx = region_names.index(selected_name)
    summary = get_region_migration_summary(selected_idx)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Innanlandsflutningar inn", f"{summary['inbound_internal']:,}")
    with col2:
        st.metric("Innanlandsflutningar út", f"{summary['outbound_internal']:,}")
    with col3:
        st.metric("Innanlands jöfnuður", f"{summary['net_internal']:+,}")
    with col4:
        st.metric("Heildar nettójöfnuður (m. útlöndum)", f"{summary['total_net']:+,}")
        
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown(f"**Helstu áfangastaðir brottfluttra frá {selected_name}:**")
        for dest, cnt in summary["top_destinations"][:4]:
            st.markdown(f"- **{dest}**: {cnt:,} manns á ári")
    with c_right:
        st.markdown(f"**Helstu upprunasvæði aðfluttra til {selected_name}:**")
        for orig, cnt in summary["top_origins"][:4]:
            st.markdown(f"- **{orig}**: {cnt:,} manns á ári")
