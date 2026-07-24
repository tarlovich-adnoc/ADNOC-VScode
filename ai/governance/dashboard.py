#!/usr/bin/env python3
"""ADNOC Governance — AI Usage Dashboard

Reads agent-runs.jsonl (self-reported by agents — estimates, not an invoice) and renders
a self-contained HTML dashboard the bi-weekly review runs on: per-agent cost AND failure
share, per-model burn (so a "forgotten Opus" is visible), per-skill usage, per-team and
per-workflow rollups, and week-over-week trend.

Usage:  python dashboard.py [--input <path>] [--output <path>] [--snapshot]
        --snapshot also writes ai/governance/reports/dashboard-YYYY-MM-DD.html
        (committed, dated evidence — pipeline artifacts expire, git doesn't)
"""
import argparse
import datetime
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument("--input", default=os.path.join(HERE, "agent-runs.jsonl"))
parser.add_argument("--output", default=os.path.join(HERE, "dashboard.html"))
parser.add_argument("--snapshot", action="store_true",
                    help="also write ai/governance/reports/dashboard-YYYY-MM-DD.html")
args = parser.parse_args()

LOG = args.input
OUT = args.output

rows = []
if os.path.exists(LOG):
    for line in open(LOG, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass


def model_class(model: str) -> str:
    """Heuristic cost tier from the model name. Actual per-token rates are authoritative;
    this only has to separate 'light', 'workhorse' and 'heavy'. Word-boundary matching —
    a bare 'mini' substring would mis-class 'gemini' as light."""
    import re
    m = (model or "").lower()
    if "opus" in m:
        return "heavy"
    # explicit cheap tiers, matched at token boundaries (not bare substrings)
    if re.search(r"(?:^|[-_ /.])(?:mini|nano|base|haiku|flash|lite)(?:$|[-_ /.0-9])", m):
        return "light"
    return "standard"


by_agent = defaultdict(lambda: {"runs": 0, "in": 0, "out": 0, "cost": 0.0, "fail": 0})
by_team = defaultdict(lambda: {"runs": 0, "cost": 0.0})
by_workflow = defaultdict(lambda: {"runs": 0, "cost": 0.0})
by_model = defaultdict(lambda: {"runs": 0, "cost": 0.0, "cls": ""})
by_skill = defaultdict(lambda: {"runs": 0, "fail": 0})
by_week = defaultdict(lambda: {"runs": 0, "cost": 0.0, "fail": 0})
total = {"runs": 0, "in": 0, "out": 0, "cost": 0.0, "fail": 0}
heavy_routine = []  # heavy-tier runs on routine workflows — the named #1 burner

for r in rows:
    cost = float(r.get("costUsd", 0))
    ok = bool(r.get("ok", True))
    a = by_agent[r.get("agent", "?")]
    a["runs"] += 1
    a["in"] += int(r.get("inTok", 0))
    a["out"] += int(r.get("outTok", 0))
    a["cost"] += cost
    a["fail"] += 0 if ok else 1
    total["runs"] += 1
    total["in"] += int(r.get("inTok", 0))
    total["out"] += int(r.get("outTok", 0))
    total["cost"] += cost
    total["fail"] += 0 if ok else 1
    by_team[r.get("team", "unknown")]["runs"] += 1
    by_team[r.get("team", "unknown")]["cost"] += cost
    by_workflow[r.get("workflow", "ad-hoc")]["runs"] += 1
    by_workflow[r.get("workflow", "ad-hoc")]["cost"] += cost
    model = r.get("model", "?")
    by_model[model]["runs"] += 1
    by_model[model]["cost"] += cost
    by_model[model]["cls"] = model_class(model)
    if by_model[model]["cls"] == "heavy":
        heavy_routine.append(f'{r.get("agent","?")}/{r.get("workflow","ad-hoc")}')
    for s in r.get("skills") or []:
        by_skill[s]["runs"] += 1
        by_skill[s]["fail"] += 0 if ok else 1
    ts = r.get("ts", "")
    try:
        d = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        week = f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
    except ValueError:
        week = "unknown"
    by_week[week]["runs"] += 1
    by_week[week]["cost"] += cost
    by_week[week]["fail"] += 0 if ok else 1

max_cost_agent = max([v["cost"] for v in by_agent.values()], default=1) or 1


def fail_cell(fails: int, runs: int) -> str:
    if runs == 0:
        return "—"
    pct = fails / runs * 100
    mark = ' style="color:#b91c1c;font-weight:600"' if pct >= 20 else ""
    return f"<span{mark}>{fails} ({pct:.0f}%)</span>"


agent_bars = ""
sorted_agents = sorted(by_agent.items(), key=lambda kv: -kv[1]["cost"])
for i, (agent, v) in enumerate(sorted_agents):
    pct = int(v["cost"] / max_cost_agent * 100)
    hint = "← top optimization candidate" if i == 0 and v["cost"] > 0 else ""
    agent_bars += f"""
      <tr>
        <td>{agent}</td>
        <td>{v['runs']}</td>
        <td>{fail_cell(v['fail'], v['runs'])}</td>
        <td>{v['in']:,}</td>
        <td>{v['out']:,}</td>
        <td>${v['cost']:.5f}</td>
        <td><div class="bar" style="width:{pct}%"></div></td>
        <td class="hint">{hint}</td>
      </tr>"""

model_rows = ""
for model, v in sorted(by_model.items(), key=lambda kv: -kv[1]["cost"]):
    flag = ' <b style="color:#b91c1c">[warn] heavy</b>' if v["cls"] == "heavy" else ""
    model_rows += f"""
      <tr><td>{model}</td><td>{v['cls']}{flag}</td><td>{v['runs']}</td><td>${v['cost']:.5f}</td></tr>"""

heavy_note = ""
if heavy_routine:
    uniq = sorted(set(heavy_routine))
    heavy_note = (f'<div class="warn"><b>[warn] {len(heavy_routine)} run(s) on a heavy-tier model</b> '
                  f'({", ".join(uniq[:6])}{"…" if len(uniq) > 6 else ""}) — the house rule says heavy models are '
                  f'deliberate-only; check these were intentional (the "forgotten Opus" is the #1 budget burner).</div>')

skill_rows = ""
for s, v in sorted(by_skill.items(), key=lambda kv: -kv[1]["runs"]):
    skill_rows += f"""
      <tr><td>{s}</td><td>{v['runs']}</td><td>{fail_cell(v['fail'], v['runs'])}</td></tr>"""

team_rows = ""
for team, v in sorted(by_team.items(), key=lambda kv: -kv[1]["cost"]):
    team_rows += f"""
      <tr><td>{team}</td><td>{v['runs']}</td><td>${v['cost']:.5f}</td></tr>"""

workflow_rows = ""
for wf, v in sorted(by_workflow.items(), key=lambda kv: -kv[1]["cost"]):
    workflow_rows += f"""
      <tr><td>{wf}</td><td>{v['runs']}</td><td>${v['cost']:.5f}</td></tr>"""

week_rows = ""
for week, v in sorted(by_week.items()):
    week_rows += f"""
      <tr><td>{week}</td><td>{v['runs']}</td><td>{fail_cell(v['fail'], v['runs'])}</td><td>${v['cost']:.5f}</td></tr>"""

# Projection: cost-per-run × 12 workflows/dev/day × 50 devs × 21 working days.
cost_per_run = (total["cost"] / total["runs"]) if total["runs"] > 0 else 0
monthly_proj = cost_per_run * 12 * 50 * 21

html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>ADNOC Governance — AI Usage Dashboard</title>
<style>
  body {{ font-family: system-ui; max-width: 920px; margin: 40px auto; color:#1a1a1a; }}
  h1 {{ margin-bottom: 4px; }} h2 {{ margin-top: 32px; }}
  .sub {{ color:#666; margin-top:0; }}
  .cards {{ display:flex; gap:16px; margin:24px 0; }}
  .card {{ flex:1; border:1px solid #e3e3e3; border-radius:10px; padding:16px; }}
  .card .n {{ font-size:28px; font-weight:700; }}
  table {{ width:100%; border-collapse:collapse; }}
  th,td {{ text-align:left; padding:8px; border-bottom:1px solid #eee; font-size:14px; }}
  .bar {{ height:14px; background:#2563eb; border-radius:4px; }}
  .hint {{ color:#888; font-size:12px; }}
  .note {{ background:#f7f7f9; border-radius:10px; padding:14px; margin-top:24px; font-size:14px; }}
  .warn {{ background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:12px; margin:16px 0; font-size:14px; }}
</style></head><body>
  <h1>AI Usage Dashboard</h1>
  <p class="sub">runs · failures · models · skills · trend — source: <code>{os.path.basename(LOG)}</code>
  (self-reported estimates; authoritative spend = Copilot usage report)</p>

  <div class="cards">
    <div class="card"><div class="n">{total['runs']}</div>agent runs</div>
    <div class="card"><div class="n">{fail_cell(total['fail'], total['runs'])}</div>failed runs</div>
    <div class="card"><div class="n">{(total['in']+total['out']):,}</div>total tokens (est.)</div>
    <div class="card"><div class="n">${total['cost']:.5f}</div>est. spend (log lifetime)</div>
  </div>
  {heavy_note}

  <h2>Per-agent</h2>
  <table>
    <tr><th>Agent</th><th>Runs</th><th>Failed</th><th>In tok</th><th>Out tok</th><th>Cost</th><th>Share</th><th></th></tr>
    {agent_bars or '<tr><td colspan=8>No runs yet — run an agentic workflow first.</td></tr>'}
  </table>

  <h2>Per-model (cost tier is a name heuristic — actual per-token rates are authoritative)</h2>
  <table>
    <tr><th>Model</th><th>Class</th><th>Runs</th><th>Cost</th></tr>
    {model_rows or '<tr><td colspan=4>No model data.</td></tr>'}
  </table>

  <h2>Per-skill (which skills load — feeds post-ship skill eval)</h2>
  <table>
    <tr><th>Skill</th><th>Runs it loaded in</th><th>Failed</th></tr>
    {skill_rows or '<tr><td colspan=3>No skills field logged yet.</td></tr>'}
  </table>

  <h2>Per-team</h2>
  <table>
    <tr><th>Team</th><th>Runs</th><th>Cost</th></tr>
    {team_rows or '<tr><td colspan=3>No team data — add "team" field to agent-runs.jsonl entries.</td></tr>'}
  </table>

  <h2>Per-workflow</h2>
  <table>
    <tr><th>Workflow</th><th>Runs</th><th>Cost</th></tr>
    {workflow_rows or '<tr><td colspan=3>No workflow data.</td></tr>'}
  </table>

  <h2>Week-over-week (did the last optimization move the number?)</h2>
  <table>
    <tr><th>ISO week</th><th>Runs</th><th>Failed</th><th>Cost</th></tr>
    {week_rows or '<tr><td colspan=4>No timestamps parsed.</td></tr>'}
  </table>

  <div class="note">
    <b>Why this matters:</b> the heaviest agent, the failure hot-spots and any heavy-tier runs are
    visible at a glance, so the bi-weekly review can act (tighter prompts, narrower masks, demote
    noisy agents, fix top failure via /selfimprove). Naive projection to a 50-dev fleet
    (12 workflows/dev/day × 50 devs × 21 days): <b>${monthly_proj:,.0f}/mo</b> — a ballpark
    <i>built from self-reported estimates</i>, not an invoice.
    See <code>ai/governance/optimization-log.md</code> for the running record of cuts applied.
  </div>
</body></html>"""

open(OUT, "w", encoding="utf-8").write(html)
print(f"Wrote {OUT} ({total['runs']} runs, {total['fail']} failed, ${total['cost']:.5f} est. spend).")

if args.snapshot:
    rep_dir = os.path.join(HERE, "reports")
    os.makedirs(rep_dir, exist_ok=True)
    snap = os.path.join(rep_dir, f"dashboard-{datetime.date.today().isoformat()}.html")
    open(snap, "w", encoding="utf-8").write(html)
    print(f"Snapshot: {snap} — commit it; dated snapshots are the evidence trail.")
