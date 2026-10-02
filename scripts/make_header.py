"""Generate the animated profile header (assets/header-dark.svg, assets/header-light.svg).

Same palette as the portfolio (manvith1604.github.io/portfolio): navy, Airflow blue + teal,
Airflow task-state colours. The mini DAG on the right replays a run on a loop: each task
goes queued -> running -> success and the edges carry flowing "data".

Edit METRICS / TEXT below and run:  python3 scripts/make_header.py
"""
from pathlib import Path

W, H = 900, 300

TEXT = {
    "status": "OPEN TO DATA ENGINEERING ROLES · PHOENIX, AZ",
    "name": "Manvith Belame Yogesh",
    "role": "Data Engineer at Walnutech AI",
    "sub": "M.S. Data Analytics Engineering, Northeastern · GPA 3.9 · 5+ years in data",
}

METRICS = [
    ("76%→&lt;1%", "extraction failures"),
    ("2.3h→10m", "monthly crawl"),
    ("−77%", "pipeline runtime"),
    ("300M+", "rows processed"),
    ("−80%", "cloud compute"),
    ("50+", "data-quality rules"),
]

# career DAG: (id, label, column, row) — row 0 = branch, row 1 = main line
NODES = [
    ("jss", "jss", 0, 1),
    ("nue", "nuetech", 1, 0),
    ("acn", "disney", 2, 1),
    ("neu", "neu_ms", 3, 1),
    ("prc", "plymouth", 4, 0),
    ("cdf", "cdf", 5, 1),
    ("wal", "walnut", 6, 1),
]
EDGES = [("jss", "nue"), ("jss", "acn"), ("nue", "acn"), ("acn", "neu"),
         ("neu", "prc"), ("neu", "cdf"), ("prc", "cdf"), ("cdf", "wal")]

THEMES = {
    "dark": dict(bg1="#0b1120", bg2="#111b30", border="#22314f", text="#e6edf7", muted="#94a3bd",
                 faint="#5d6c88", accent="#3d9bff", teal="#00c7d4", ok="#22c55e", running="#a3e635",
                 queued="#475569", node="#111b30", glow_op=".22", grid="#1a2742"),
    "light": dict(bg1="#f5f8fc", bg2="#e9f0f9", border="#d9e1ec", text="#0f1b2d", muted="#4a5a72",
                  faint="#8a98ad", accent="#017cee", teal="#0891b2", ok="#16a34a", running="#65a30d",
                  queued="#94a3b8", node="#ffffff", glow_op=".14", grid="#dde6f2"),
}

# DAG geometry
DX0, DY0, COLW, ROWH, NW, NH = 536, 70, 46, 50, 40, 22
CYCLE, STEP = 9.0, 0.55  # seconds per loop, stagger between tasks


def node_xy(col, row):
    return DX0 + col * COLW, DY0 + row * ROWH


def build(theme):
    c = THEMES[theme]
    pos = {n[0]: node_xy(n[2], n[3]) for n in NODES}
    run_pct = 100 * 0.45 / CYCLE        # time spent "running"
    reset_pct = 100 * (CYCLE - 0.9) / CYCLE

    out = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{TEXT['name']}. {TEXT['role']}. {TEXT['sub']}. Open to data engineering roles, Phoenix AZ, open to relocation. ''' +
           ". ".join(f"{v} {k}" for v, k in METRICS) + '''.">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/>
    </linearGradient>
    <radialGradient id="glow" cx="82%" cy="10%" r="60%">
      <stop offset="0" stop-color="{accent}" stop-opacity="{glow_op}"/>
      <stop offset="1" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="dots" width="14" height="14" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="1" fill="{grid}"/>
    </pattern>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 1 L9 5 L0 9 Z" fill="{accent}"/></marker>
    <style>
      .n {{ font: 700 40px -apple-system, "Segoe UI", Inter, sans-serif; letter-spacing: -1.4px; fill: {text} }}
      .r {{ font: 500 18px -apple-system, "Segoe UI", Inter, sans-serif; fill: {text} }}
      .s {{ font: 400 13.5px -apple-system, "Segoe UI", Inter, sans-serif; fill: {muted} }}
      .k {{ font: 700 18px ui-monospace, SFMono-Regular, Menlo, monospace; fill: {accent} }}
      .l {{ font: 400 11px -apple-system, "Segoe UI", Inter, sans-serif; fill: {muted} }}
      .e {{ font: 600 10.5px ui-monospace, SFMono-Regular, Menlo, monospace; fill: {teal}; letter-spacing: 1.6px }}
      .t {{ font: 600 8px ui-monospace, SFMono-Regular, Menlo, monospace; fill: {muted} }}
      .dag {{ font: 500 9px ui-monospace, SFMono-Regular, Menlo, monospace; fill: {faint} }}
      .edge {{ fill: none; stroke: {accent}; stroke-width: 1.4; stroke-dasharray: 4 4; opacity: .85;
               animation: flow .8s linear infinite }}
      .task {{ fill: {node}; stroke: {queued}; stroke-width: 2; animation: state {CYCLE}s linear infinite both }}
      .pulse {{ animation: pulse 2s ease-out infinite; transform-origin: 48px 46px }}
      @keyframes flow {{ to {{ stroke-dashoffset: -8 }} }}
      @keyframes state {{
        0% {{ stroke: {running} }}
        {run_pct:.2f}% {{ stroke: {running} }}
        {run2:.2f}% {{ stroke: {ok} }}
        {reset_pct:.2f}% {{ stroke: {ok} }}
        {reset2:.2f}% {{ stroke: {queued} }}
        100% {{ stroke: {queued} }}
      }}
      @keyframes pulse {{ 0% {{ opacity: .9; transform: scale(1) }} 100% {{ opacity: 0; transform: scale(3) }} }}
      @media (prefers-reduced-motion: reduce) {{ .edge, .task, .pulse {{ animation: none }} .task {{ stroke: {ok} }} }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" rx="14" fill="url(#glow)"/>
  <rect x="516" y="28" width="364" height="160" rx="10" fill="url(#dots)" opacity=".9"/>
  <rect x=".5" y=".5" width="{Wm}" height="{Hm}" rx="14" fill="none" stroke="{border}"/>
'''.format(**c, W=W, H=H, Wm=W - 1, Hm=H - 1, CYCLE=CYCLE, run_pct=run_pct,
                run2=run_pct + 0.01, reset_pct=reset_pct, reset2=reset_pct + 0.01)]

    # status line
    out.append(f'''  <circle class="pulse" cx="48" cy="46" r="4.5" fill="{c['ok']}"/>
  <circle cx="48" cy="46" r="4.5" fill="{c['ok']}"/>
  <text x="62" y="50" class="e">{TEXT['status']}</text>
''')
    # identity
    out.append(f'''  <text x="44" y="118" class="n">{TEXT['name']}</text>
  <text x="44" y="150" class="r">{TEXT['role']}</text>
  <text x="44" y="174" class="s">{TEXT['sub']}</text>
''')

    # mini DAG
    out.append(f'  <text x="{DX0}" y="{DY0 - 14}" class="dag">dag_id: manvith_career  ·  @continuous</text>\n')
    for a, b in EDGES:
        (ax, ay), (bx, by) = pos[a], pos[b]
        sx, sy, ex, ey = ax + NW, ay + NH / 2, bx - 2, by + NH / 2
        mx = (ex - sx) / 2
        out.append(f'  <path class="edge" d="M{sx} {sy} C{sx + mx} {sy} {ex - mx} {ey} {ex} {ey}" marker-end="url(#arr)"/>\n')
    for i, (nid, label, col, row) in enumerate(NODES):
        x, y = pos[nid]
        out.append(f'  <rect class="task" x="{x}" y="{y}" width="{NW}" height="{NH}" rx="5" style="animation-delay:{i * STEP:.2f}s"/>\n')
        out.append(f'  <text x="{x + NW / 2}" y="{y + 14.5}" class="t" text-anchor="middle">{label}</text>\n')

    # metrics row
    out.append(f'  <line x1="44" y1="206" x2="856" y2="206" stroke="{c["border"]}"/>\n')
    xs = [44, 182, 310, 432, 560, 684]
    for x, (v, k) in zip(xs, METRICS):
        out.append(f'  <text x="{x}" y="242" class="k">{v}</text><text x="{x}" y="262" class="l">{k}</text>\n')
    out.append('</svg>\n')
    return "".join(out)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent / "assets"
    root.mkdir(exist_ok=True)
    for theme in THEMES:
        (root / f"header-{theme}.svg").write_text(build(theme), encoding="utf-8")
        print("wrote", root / f"header-{theme}.svg")
