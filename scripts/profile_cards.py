"""Render the live GitHub activity card.

Runs nightly from .github/workflows/profile-cards.yml. Standard library only.

Sources, all public:
  - contribution calendar  https://github.com/users/<user>/contributions  (no token needed)
  - pull-request counts    GitHub search API
  - languages              public, non-fork repositories, summed by bytes

Writes assets/stats-dark.svg and assets/stats-light.svg.

If any source fails, the script raises before writing anything, so the last good card
stays committed. A stale card beats a card with a wrong number.
"""
import datetime as dt
import html
import json
import os
import re
import urllib.request
from pathlib import Path

USER = os.environ.get("GH_USER", "manvith1604")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ROOT = Path(__file__).resolve().parent.parent

W = 900
LEVELS = {
    "dark": ["#16233d", "#0e3a5e", "#1666b8", "#3d9bff", "#00c7d4"],
    "light": ["#e3eaf4", "#b6d4f5", "#6aa9ef", "#017cee", "#0891b2"],
}
THEMES = {
    "dark": dict(bg1="#0b1120", bg2="#111b30", border="#22314f", text="#e6edf7", muted="#94a3bd",
                 faint="#5d6c88", accent="#3d9bff", teal="#00c7d4", ok="#22c55e"),
    "light": dict(bg1="#f5f8fc", bg2="#e9f0f9", border="#d9e1ec", text="#0f1b2d", muted="#4a5a72",
                  faint="#8a98ad", accent="#017cee", teal="#0891b2", ok="#16a34a"),
}
LANG_COLORS = {
    "Python": "#3776AB", "Jupyter Notebook": "#F37626", "HTML": "#E34F26", "CSS": "#1572B6",
    "JavaScript": "#F7DF1E", "TypeScript": "#3178C6", "TSQL": "#CC2927", "PLpgSQL": "#336791",
    "Shell": "#89E051", "R": "#276DC3", "Java": "#ED8B00", "Dockerfile": "#2496ED", "SCSS": "#C6538C",
}


# ---------------------------------------------------------------- fetching
def get(url, accept="application/vnd.github+json", raw=False):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": f"{USER}-profile-cards"})
    if TOKEN and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8")
    return body if raw else json.loads(body)


def contributions():
    page = get(f"https://github.com/users/{USER}/contributions", accept="text/html", raw=True)
    days = {}
    for m in re.finditer(r'data-date="(\d{4}-\d\d-\d\d)"\s+id="([^"]+)"\s+data-level="(\d)"', page):
        days[m.group(2)] = [dt.date.fromisoformat(m.group(1)), 0, int(m.group(3))]
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', page):
        if m.group(1) in days:
            n = re.match(r"([\d,]+) contribution", m.group(2))
            days[m.group(1)][1] = int(n.group(1).replace(",", "")) if n else 0
    out = sorted((tuple(v) for v in days.values()), key=lambda d: d[0])
    if len(out) < 300:
        raise RuntimeError(f"contribution calendar looks wrong ({len(out)} days)")
    return out


def streaks(days):
    today = days[-1][0]
    longest = run = 0
    for _, n, _ in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    current = 0
    # today with no contributions yet doesn't break the streak
    for d, n, _ in reversed(days):
        if n:
            current += 1
        elif d == today:
            continue
        else:
            break
    return current, longest


def pr_counts():
    base = "https://api.github.com/search/issues?per_page=1&q="
    opened = get(base + f"author:{USER}+type:pr")["total_count"]
    merged = get(base + f"author:{USER}+type:pr+is:merged")["total_count"]
    return opened, merged


def languages():
    # Share of repositories by their primary language. Byte counts were misleading here:
    # notebook outputs inflate Jupyter, and vendored files skew whole repos.
    repos = [r for r in get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
    counts = {}
    for r in repos:
        if r["language"]:
            counts[r["language"]] = counts.get(r["language"], 0) + 1
    total = sum(counts.values()) or 1
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:6]
    return [(k, v / total) for k, v in top], len(repos)


# ---------------------------------------------------------------- rendering
def render(theme, days, cur, longest, opened, merged, langs, repo_count, updated):
    c, lv = THEMES[theme], LEVELS[theme]
    year = days[-371:]
    total = sum(n for _, n, _ in year)
    active = sum(1 for _, n, _ in year if n)
    last30 = sum(n for _, n, _ in year[-30:])

    H = 300
    metrics = [
        (f"{total:,}", "contributions, last year"),
        (f"{last30:,}", "in the last 30 days"),
        (f"{cur}d", "current streak"),
        (f"{longest}d", "longest streak"),
        (f"{merged}/{opened}", "PRs merged / opened"),
        (f"{active}", "active days"),
    ]
    s = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub activity for {USER}, updated {updated}. ''' +
         ". ".join(f"{v} {k}" for v, k in metrics) + ". Top languages: " +
         ", ".join(f"{k} {p:.0%}" for k, p in langs) + f'''.">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/></linearGradient>
    <style>
      .h {{ font: 600 10.5px ui-monospace, SFMono-Regular, Menlo, monospace; fill: {c['teal']}; letter-spacing: 1.6px }}
      .u {{ font: 400 10.5px ui-monospace, SFMono-Regular, Menlo, monospace; fill: {c['faint']} }}
      .k {{ font: 700 20px ui-monospace, SFMono-Regular, Menlo, monospace; fill: {c['accent']} }}
      .l {{ font: 400 11px -apple-system, "Segoe UI", Inter, sans-serif; fill: {c['muted']} }}
      .m {{ font: 400 9.5px -apple-system, "Segoe UI", Inter, sans-serif; fill: {c['faint']} }}
      .today {{ animation: beat 1.8s ease-in-out infinite }}
      .live {{ animation: beat 1.8s ease-in-out infinite }}
      @keyframes beat {{ 50% {{ opacity: .35 }} }}
      @media (prefers-reduced-motion: reduce) {{ .today, .live {{ animation: none }} }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{c['border']}"/>
  <circle class="live" cx="48" cy="38" r="4" fill="{c['ok']}"/>
  <text x="60" y="42" class="h">GITHUB ACTIVITY · LIVE</text>
  <text x="856" y="42" class="u" text-anchor="end">updated {updated} · public data</text>
''']
    xs = [44, 180, 316, 428, 540, 690]
    for x, (v, k) in zip(xs, metrics):
        s.append(f'  <text x="{x}" y="82" class="k">{v}</text><text x="{x}" y="100" class="l">{k}</text>\n')

    # heatmap: 53 weeks x 7 days, Sunday at top, like GitHub's own calendar
    x0, y0, cell, gap = 44, 128, 11, 3
    first = year[0][0]
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    last_month, last_label_col = None, -9
    for d, n, level in year:
        idx = (d - start).days
        col, row = idx // 7, idx % 7
        x, y = x0 + col * (cell + gap), y0 + row * (cell + gap)
        if row == 0 and d.month != last_month:
            # skip a label that would collide with the previous one (partial first month)
            if col - last_label_col >= 3 and col < 52:
                s.append(f'  <text x="{x}" y="{y0 - 6}" class="m">{d.strftime("%b")}</text>\n')
                last_label_col = col
            last_month = d.month
        cls = ' class="today"' if d == year[-1][0] else ""
        tip = f"{n} contribution{'s' if n != 1 else ''} on {d.isoformat()}"
        s.append(f'  <rect{cls} x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{lv[level]}"><title>{tip}</title></rect>\n')

    # legend
    lx = 856 - 5 * (cell + gap)
    s.append(f'  <text x="{lx - 8}" y="{y0 + 7 * (cell + gap) + 12}" class="m" text-anchor="end">less</text>\n')
    for i, col in enumerate(lv):
        s.append(f'  <rect x="{lx + i * (cell + gap)}" y="{y0 + 7 * (cell + gap) + 3}" width="{cell}" height="{cell}" rx="2.5" fill="{col}"/>\n')
    s.append(f'  <text x="{lx + 5 * (cell + gap) + 2}" y="{y0 + 7 * (cell + gap) + 12}" class="m">more</text>\n')

    # language bar
    by, bx, bw = 256, 44, 812
    s.append(f'  <text x="{bx}" y="{by - 8}" class="m">primary language across {repo_count} public repos</text>\n')
    s.append(f'  <g><clipPath id="clip"><rect x="{bx}" y="{by}" width="{bw}" height="8" rx="4"/></clipPath><g clip-path="url(#clip)">\n')
    x = bx
    for lang, p in langs:
        w = max(bw * p, 2)
        s.append(f'    <rect x="{x:.1f}" y="{by}" width="{w:.1f}" height="8" fill="{LANG_COLORS.get(lang, c["accent"])}"/>\n')
        x += w
    s.append('  </g></g>\n')
    x = bx
    for lang, p in langs:
        label = f"{html.escape(lang)} {p:.0%}"
        s.append(f'  <circle cx="{x + 4}" cy="{by + 24}" r="4" fill="{LANG_COLORS.get(lang, c["accent"])}"/><text x="{x + 12}" y="{by + 28}" class="l">{label}</text>\n')
        x += 22 + len(label) * 6.4
    s.append("</svg>\n")
    return "".join(s)


if __name__ == "__main__":
    # gather everything first; any failure raises before a single file is written
    days = contributions()
    cur, longest = streaks(days)
    opened, merged = pr_counts()
    langs, repo_count = languages()
    updated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")

    (ROOT / "assets").mkdir(exist_ok=True)
    for theme in THEMES:
        (ROOT / "assets" / f"stats-{theme}.svg").write_text(
            render(theme, days, cur, longest, opened, merged, langs, repo_count, updated), encoding="utf-8")
    print(f"ok: {sum(n for _, n, _ in days[-371:])} contributions, streak {cur}/{longest}, PRs {merged}/{opened}")
