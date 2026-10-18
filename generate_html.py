#!/usr/bin/env python3
"""
generate_html.py
Generates an interactive HTML dashboard from output/final_report.json
"""

import json
import sys


def load_report():
    try:
        with open("output/final_report.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[!] output/final_report.json not found. Run report.py first.")
        sys.exit(1)


def build_html(report):
    domain = report["domain"]
    s = report["summary"]

    # Subdomain rows — sort interesting ones to the top
    sorted_subs = sorted(report["subdomains"], key=lambda sub: not sub.get("interesting", False))

    sub_rows = ""
    for sub in sorted_subs:
        status = "RESOLVES" if sub["resolves"] else "no resolve"
        css_class = "ok" if sub["resolves"] else "muted"
        if sub.get("interesting"):
            flag = f'<span class="flag">FLAGGED: {sub["matched_keyword"]}</span>'
        else:
            flag = ""
        sub_rows += f'<tr><td>{sub["subdomain"]}</td><td class="{css_class}">{status}</td><td>{flag}</td></tr>\n'

    # Email rows
    email_rows = ""
    for e in report["emails"]:
        status = "BREACHED" if e["breached"] else "clean"
        css_class = "danger" if e["breached"] else "ok"
        breaches = ", ".join(e.get("breaches", [])) if e["breached"] else "-"
        email_rows += f'<tr><td>{e["email"]}</td><td class="{css_class}">{status}</td><td>{breaches}</td></tr>\n'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>OSINT Exposure Report - {domain}</title>
<style>
  :root {{
    --bg: #f4f6f8; --card-bg: #ffffff; --text: #1a1a2e; --muted: #6b7280;
    --border: #e5e7eb; --accent: #1e293b; --ok: #16a34a; --danger: #dc2626;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #0f172a; --card-bg: #1e293b; --text: #f1f5f9; --muted: #94a3b8;
      --border: #334155; --accent: #1e293b; --ok: #4ade80; --danger: #f87171;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: -apple-system, Segoe UI, Roboto, sans-serif;
    background: var(--bg); color: var(--text); padding: 24px;
  }}
  .header {{
    background: var(--accent); color: #fff; padding: 24px; border-radius: 10px; margin-bottom: 20px;
  }}
  .header h1 {{ margin: 0 0 6px 0; font-size: 22px; }}
  .header p {{ margin: 0; opacity: 0.8; font-size: 14px; }}
  .cards {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px; margin-bottom: 24px;
  }}
  .card {{
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 16px;
  }}
  .card .label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}
  .card .value {{ font-size: 26px; font-weight: 700; margin-top: 4px; }}
  .section {{
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px;
    padding: 18px; margin-bottom: 20px; overflow-x: auto;
  }}
  .section h2 {{ margin-top: 0; font-size: 16px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{
    text-align: left; padding: 8px 10px; border-bottom: 2px solid var(--border);
    color: var(--muted); text-transform: uppercase; font-size: 11px;
  }}
  td {{ padding: 8px 10px; border-bottom: 1px solid var(--border); }}
  .ok {{ color: var(--ok); font-weight: 600; }}
  .danger {{ color: var(--danger); font-weight: 600; }}
  .muted {{ color: var(--muted); }}
  .flag {{
    background: #fef3c7; color: #92400e; font-size: 11px; font-weight: 700;
    padding: 2px 8px; border-radius: 4px; text-transform: uppercase;
  }}
  @media (prefers-color-scheme: dark) {{
    .flag {{ background: #78350f; color: #fef3c7; }}
  }}
  .disclaimer {{
    font-size: 12px; color: var(--muted); padding: 10px 14px; border-left: 3px solid var(--muted);
    margin-bottom: 20px;
  }}
</style>
</head>
<body>

<div class="header">
  <h1>OSINT Exposure Report</h1>
  <p>Target: {domain} — generated from public data sources only</p>
</div>

<div class="disclaimer">
  Interpretation: findings are derived from public certificate logs, pattern-generated email
  guesses, and breach-database lookups. They indicate potential exposure, not confirmed
  compromise. Validate before taking action.
</div>

<div class="cards">
  <div class="card"><div class="label">Subdomains Found</div><div class="value">{s['subdomains_found']}</div></div>
  <div class="card"><div class="label">Resolving</div><div class="value">{s['subdomains_resolving']}</div></div>
  <div class="card"><div class="label">Flagged Interesting</div><div class="value">{s['subdomains_interesting']}</div></div>
  <div class="card"><div class="label">Emails Generated</div><div class="value">{s['emails_generated']}</div></div>
  <div class="card"><div class="label">Breached Emails</div><div class="value">{s['emails_breached']}</div></div>
  <div class="card"><div class="label">Exposure Score</div><div class="value">{s['exposure_score']}</div></div>
</div>

<div class="section">
  <h2>Subdomains ({s['subdomains_found']})</h2>
  <table>
    <tr><th>Subdomain</th><th>Status</th><th>Flag</th></tr>
    {sub_rows}
  </table>
</div>

<div class="section">
  <h2>Generated Emails &amp; Breach Status ({s['emails_generated']})</h2>
  <table>
    <tr><th>Email</th><th>Status</th><th>Breaches</th></tr>
    {email_rows}
  </table>
</div>

</body>
</html>
"""
    return html


def main():
    report = load_report()
    html = build_html(report)

    with open("output/dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("[+] Dashboard generated: output/dashboard.html")
    print("[+] Open it in your browser to view the report.")


if __name__ == "__main__":
    main()