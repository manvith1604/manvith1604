"""Generate the experience, education and certification cards (dark + light) in assets/.

Same theme as the header and the portfolio: navy, Airflow blue + teal, Airflow task states.
Each role is a "task" in the career DAG: the current one is running (lime, pulsing),
finished ones are success (green). Edit the data below and run:

    python3 scripts/make_cards.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = Path(__file__).resolve().parent / "icons"

THEMES = {
    "dark": dict(bg1="#0b1120", bg2="#111b30", border="#22314f", text="#e6edf7", muted="#94a3bd",
                 faint="#5d6c88", accent="#3d9bff", teal="#00c7d4", ok="#22c55e", running="#a3e635",
                 chip="#16233d", op_de="#3d9bff", op_coop="#f59e0b", op_analyst="#00c7d4", op_edu="#a78bfa"),
    "light": dict(bg1="#ffffff", bg2="#f1f5fb", border="#d9e1ec", text="#0f1b2d", muted="#4a5a72",
                  faint="#8a98ad", accent="#017cee", teal="#0891b2", ok="#16a34a", running="#65a30d",
                  chip="#eef3fa", op_de="#017cee", op_coop="#d97706", op_analyst="#0891b2", op_edu="#7c3aed"),
}
SANS = '-apple-system, "Segoe UI", Inter, sans-serif'
MONO = 'ui-monospace, SFMono-Regular, Menlo, monospace'

ROLES = [
    dict(id="walnutech", op="DataEngOperator", op_color="op_de", task="walnutech_ai", state="running",
         company="Walnutech AI", role="Data Engineer", where="Chandler, AZ", when="Apr 2026 – now",
         summary="Built the scholarship and pre-college discovery pipeline from scratch in Python and PostgreSQL.",
         metrics=[("76%→&lt;1%", "extraction failure rate"), ("2.3h→10m", "monthly crawl stage"),
                  ("15,000+", "records in the live catalog")]),
    dict(id="cdf", op="DataEngOperator", op_color="op_de", task="community_dreams", state="success",
         company="Community Dreams Foundation", role="Data Engineer", where="Remote", when="Jun 2025 – Jun 2026",
         summary="Lineage-tracked ETL and a 9-table Postgres model for an FDA-compliant food-safety SaaS.",
         metrics=[("50+", "automated data-quality rules"), ("9", "RAG knowledge libraries"),
                  ("0", "production incidents")]),
    dict(id="plymouth", op="CoopOperator", op_color="op_coop", task="plymouth_coop", state="success",
         company="Plymouth Rock Assurance", role="Data Engineer Co-op", where="Boston, MA", when="Jul 2024 – Jan 2025",
         summary="Migrated SAS pipelines to Python and Polars, Parquet on S3, run on Fargate and Step Functions.",
         metrics=[("−77%", "pipeline runtime"), ("300M+", "rows of vendor data"), ("−80%", "cloud compute cost")]),
    dict(id="disney", op="AnalystOperator", op_color="op_analyst", task="accenture_disney", state="success",
         company="The Walt Disney Company", role="Data Analyst → Senior Data Analyst · via Accenture",
         where="Bangalore, IN", when="Jan 2020 – Jan 2023",
         summary="SQL analytics and event-driven pipelines (EventBridge, Lambda) for park booking; led a team of 8.",
         metrics=[("5M+", "records across 6 apps"), ("−80%", "manual booking validation"),
                  ("+40%", "dashboard refresh speed")]),
]

SCHOOLS = [
    dict(name="Northeastern University", degree="M.S. Data Analytics Engineering", where="Boston, MA",
         when="Jan 2023 – May 2025", badge="GPA 3.9 / 4.0", task="northeastern_ms"),
    dict(name="JSS Science &amp; Technology University", degree="Bachelor of Engineering", where="Mysore, India",
         when="Aug 2016 – Jun 2020", badge="B.E.", task="jss_be"),
]

CERTS = [
    dict(id="aws", title="AWS Certified Cloud Practitioner", issuer="Amazon Web Services", icon="amazonwebservices", color="#FF9900"),
    dict(id="google-da", title="Google Data Analytics Professional", issuer="Google · Coursera", icon="google", color="#4285F4"),
    dict(id="dataexpert", title="Data Engineering Bootcamp", issuer="DataExpert.io", mono="DE", color="#00c7d4"),
    dict(id="leetcode-sql", title="LeetCode SQL 50", issuer="LeetCode study plan", icon="leetcode", color="#FFA116"),
    dict(id="java-se", title="Java Programming &amp; Software Engineering", issuer="Coursera specialization", icon="coursera", color="#0056D2"),
    dict(id="java-oop", title="Object Oriented Java: Data Structures", issuer="Coursera specialization", icon="coursera", color="#0056D2"),
    dict(id="java-udemy", title="Java Programming Masterclass (11 &amp; 17)", issuer="Udemy", icon="udemy", color="#A435F0"),
    dict(id="diploma", title="Diploma in Computer Applications", issuer="KEONICS · NBCE", mono="DCA", color="#a78bfa"),
]


def frame(w, h, c, body, label, extra_css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/></linearGradient>
    <style>
      .co {{ font: 700 22px {SANS}; fill: {c['text']}; letter-spacing: -.4px }}
      .ro {{ font: 500 14px {SANS}; fill: {c['text']} }}
      .mu {{ font: 400 12.5px {SANS}; fill: {c['muted']} }}
      .op {{ font: 700 10px {MONO}; letter-spacing: .2px }}
      .id {{ font: 400 10.5px {MONO}; fill: {c['faint']} }}
      .dt {{ font: 600 11px {MONO}; fill: {c['accent']} }}
      .mv {{ font: 700 17px {MONO}; fill: {c['accent']} }}
      .ml {{ font: 400 11px {SANS}; fill: {c['muted']} }}
      .pulse {{ animation: pulse 1.8s ease-in-out infinite }}
      @keyframes pulse {{ 50% {{ opacity: .3 }} }}
      @media (prefers-reduced-motion: reduce) {{ .pulse {{ animation: none }} }}{extra_css}
    </style>
  </defs>
  <rect width="{w}" height="{h}" rx="14" fill="url(#bg)"/>
  <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{c['border']}"/>
{body}</svg>
'''


def state_pip(x, y, state, c):
    col = c["running"] if state == "running" else c["ok"]
    word = "running" if state == "running" else "success"
    pulse = ' class="pulse"' if state == "running" else ""
    return (f'  <circle{pulse} cx="{x}" cy="{y}" r="4.5" fill="{col}"/>\n'
            f'  <text x="{x + 10}" y="{y + 4}" class="op" fill="{col}">{word}</text>\n')


def role_card(r, theme):
    c = THEMES[theme]
    w, h = 900, 186
    op = c[r["op_color"]]
    b = [f'  <rect x="0" y="0" width="6" height="{h}" rx="3" fill="{op}"/>\n',
         f'  <text x="28" y="35" class="id">task_id: {r["task"]}</text>\n',
         state_pip(780, 31, r["state"], c),
         f'  <text x="28" y="72" class="co">{r["company"]}</text>\n',
         f'  <text x="872" y="70" class="dt" text-anchor="end">{r["when"]}</text>\n',
         f'  <text x="28" y="94" class="ro">{r["role"]}</text>\n',
         f'  <text x="872" y="94" class="mu" text-anchor="end">{r["where"]}</text>\n',
         f'  <text x="28" y="117" class="mu">{r["summary"]}</text>\n']
    for i, (v, k) in enumerate(r["metrics"]):
        x = 28 + i * 286
        b.append(f'  <rect x="{x}" y="132" width="272" height="40" rx="8" fill="{c["chip"]}" stroke="{c["border"]}"/>\n')
        b.append(f'  <text x="{x + 12}" y="158" class="mv">{v}</text>\n')
        b.append(f'  <text x="{x + 14 + len(re.sub("&[a-z]+;", "x", v)) * 10.6:.0f}" y="157" class="ml">{k}</text>\n')
    label = (f'{r["company"]}. {r["role"]}, {r["where"]}, {r["when"]}. {r["summary"]} '
             + ". ".join(f"{v} {k}" for v, k in r["metrics"])).replace("&lt;", "under ")
    return frame(w, h, c, "".join(b), label)


def education_card(theme):
    c = THEMES[theme]
    w, h = 900, 150
    op = c["op_edu"]
    b = []
    for i, s in enumerate(SCHOOLS):
        x = 24 + i * 432
        b.append(f'  <rect x="{x}" y="20" width="420" height="110" rx="10" fill="{c["chip"]}" stroke="{c["border"]}"/>\n')
        b.append(f'  <rect x="{x}" y="20" width="5" height="110" rx="2.5" fill="{op}"/>\n')
        b.append(f'  <text x="{x + 20}" y="47" class="id">task_id: {s["task"]}</text>\n')
        b.append(state_pip(x + 334, 43, "success", c))
        b.append(f'  <text x="{x + 20}" y="78" class="ro" style="font-weight:700;font-size:16px">{s["name"]}</text>\n')
        b.append(f'  <text x="{x + 20}" y="99" class="mu">{s["degree"]} · {s["where"]}</text>\n')
        b.append(f'  <text x="{x + 20}" y="119" class="dt">{s["when"]}</text>\n')
        bw = len(s["badge"]) * 6.6 + 16
        b.append(f'  <rect x="{x + 404 - bw:.0f}" y="106" width="{bw:.0f}" height="20" rx="10" fill="{c["accent"]}" opacity=".15"/>\n')
        b.append(f'  <text x="{x + 404 - bw / 2:.0f}" y="120" class="op" fill="{c["accent"]}" text-anchor="middle">{s["badge"]}</text>\n')
    label = ". ".join(f'{s["degree"]}, {s["name"]}, {s["where"]}, {s["when"]}, {s["badge"]}' for s in SCHOOLS)
    return frame(w, h, c, "".join(b), label.replace("&amp;", "and"))


def icon_paths(name):
    svg = (ICONS / f"{name}.svg").read_text()
    return re.findall(r'<path d="([^"]+)"', svg)


def cert_tile(cert, theme):
    c = THEMES[theme]
    w, h = 436, 76
    col = cert["color"]
    b = [f'  <rect x="16" y="14" width="48" height="48" rx="10" fill="{col}" opacity=".14"/>\n']
    if "icon" in cert:
        for d in icon_paths(cert["icon"]):
            b.append(f'  <path d="{d}" fill="{col}" transform="translate(28 26) scale(1)"/>\n')
    else:
        b.append(f'  <text x="40" y="43" class="op" fill="{col}" text-anchor="middle" style="font-size:12px">{cert["mono"]}</text>\n')
    b.append(f'  <text x="78" y="35" class="ro" style="font-weight:600">{cert["title"]}</text>\n')
    b.append(f'  <text x="78" y="55" class="id">{cert["issuer"]}</text>\n')
    b.append(f'  <text x="414" y="35" class="id" text-anchor="end">↗</text>\n')
    label = f'{cert["title"]}, {cert["issuer"]}'.replace("&amp;", "and")
    return frame(w, h, c, "".join(b), label)


if __name__ == "__main__":
    out = ROOT / "assets"
    out.mkdir(exist_ok=True)
    for theme in THEMES:
        for r in ROLES:
            (out / f"exp-{r['id']}-{theme}.svg").write_text(role_card(r, theme), encoding="utf-8")
        (out / f"education-{theme}.svg").write_text(education_card(theme), encoding="utf-8")
        for cert in CERTS:
            (out / f"cert-{cert['id']}-{theme}.svg").write_text(cert_tile(cert, theme), encoding="utf-8")
    print("wrote", len(list(out.glob("exp-*"))) + len(list(out.glob("education-*"))) + len(list(out.glob("cert-*"))), "cards")
