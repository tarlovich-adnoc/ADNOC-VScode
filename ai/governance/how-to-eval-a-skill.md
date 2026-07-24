# `ai/governance/how-to-eval-a-skill.md` — evaluate a Copilot skill/instruction before you propose it upstream

You wrote one `SKILL.md` or one `*.instructions.md`. Before you PR it into the shared template,
run it up this 4-tier ladder. Stop at the tier that gives you enough confidence for the change's
blast radius: a path-scoped instruction touching one repo can stop at Tier 2; anything going into
the **shared template** (every team inherits it) must clear Tier 3, and a new always-on instruction
must clear Tier 4.

Definitions:
- **Skill** = `.github/skills/<name>/SKILL.md` — procedural, loaded only when its `description` matches the prompt.
- **Instruction** = an optional team-owned `.github/copilot-instructions.md` (always-on) or a
  `.github/instructions/**/*.instructions.md` file selected via `applyTo`.

---

## The ladder

### Tier 1 — Static / structural (5 min)

**Checks:** it parses; frontmatter is valid; description is well-formed; no leaked absolute paths,
secrets, or internal hostnames; length is sane.

**How:**
```bash
# YAML frontmatter parses + required keys present
python - <<'PY'
import sys,glob,yaml
for f in glob.glob('.github/skills/**/SKILL.md',recursive=True)+glob.glob('.github/instructions/**/*.instructions.md',recursive=True):
    t=open(f,encoding='utf-8').read()
    assert t.startswith('---'),f"{f}: no frontmatter"
    fm=yaml.safe_load(t.split('---',2)[1])
    assert fm.get('description'),f"{f}: missing description"
    print(f,"OK",len(t.split()),"words")
PY
# Secret / path leak scan
git grep -nE 'AKIA|password|api[_-]?key|C:\\\\Users|/home/[a-z]+|dev\.azure\.com/.+@|\.internal\.adnoc' -- '.github/**/*.md'
```
Also eyeball: description is **one sentence, action + trigger nouns** ("Use when generating Azure
Functions HTTP triggers in .NET"); body under ~400 words for a skill, under ~150 lines for an
always-on instruction (it burns context on every request).

**Pass:** script prints OK for the file; secret scan returns nothing; description ≤ 2 lines; body within budget.

---

### Tier 2 — Triggering / discovery (15 min)

**Checks:** does Copilot actually load it at the right moment — and *not* at the wrong one? The
`description` (skill) and `applyTo` (instruction) are the only things that decide this, so this tier
tests them directly.

**How** — in VS Code Copilot Chat (Agent mode) or Rider's Copilot chat, run 3 prompts and inspect the
**References / context** chip on each reply:
1. **Bullseye** — a prompt squarely in scope. Expect the skill name in References.
2. **Adjacent** — same domain, different task. Should *not* load (catches over-broad descriptions).
3. **Off-topic** — unrelated request. Must *not* load.

Confirm firing two ways: (a) the file appears in the References chip; (b) behavior visibly changes —
the answer follows a convention only the skill specifies. For instructions, add a sentinel line like
`Always start the answer with [POLICY-X]` during testing and check it appears, then remove it.

**Pass:** bullseye loads, adjacent and off-topic do not, and the behavioral fingerprint shows up on
the bullseye only. If adjacent fires too, the description is too broad — tighten it and re-run.

---

### Tier 3 — Behavioral A/B (1–2 h)

**Checks:** does output actually get *better* with the skill than without? This is the real question.

**Build a fixed eval set** — 5–10 representative prompts, committed so anyone can re-run:
`ai/governance/evals/<skill-name>/prompts.md`, one task per heading, each with a one-line expected outcome.

**Run A/B (reproducible):**
1. **WITHOUT** — `git mv` the skill out of `.github/skills/` (or rename to `SKILL.md.off`). Reload the
   window. Run all prompts in **fresh chats** (one prompt per chat — no cross-contamination). Save each
   reply to `evals/<skill>/without/NN.md`.
2. **WITH** — restore the file, reload, repeat into `evals/<skill>/with/NN.md`.
3. Keep model + mode constant (note them: e.g. `gpt-5.4`, Agent mode). Randomise/alternate order so you
   aren't priming yourself.
4. Score both columns on the rubric below.

**Pass:** mean rubric score WITH ≥ WITHOUT **by ≥ 2 points total**, **and zero dimension regresses**.
If WITH only ties WITHOUT, the skill earns its context cost on nothing — cut it or sharpen it.

---

### Tier 4 — Adversarial / judge (2–3 h, required for always-on / constitution-level content)

**Checks:** over-triggering, false confidence, and regressions on *unrelated* tasks — the failure modes
a happy-path A/B misses.

**How:**
- **Blind judge.** Paste rubric + the two anonymised outputs (label them X/Y, randomise which is WITH)
  into a *second* agent — a separate Copilot chat — and ask it to score each on the rubric and
  pick the stronger, with reasons. Do this for all eval prompts. Disagreement with your own Tier-3
  scores = re-examine that item.
- **Regression probe.** Add 3 deliberately **out-of-scope** prompts to the eval set. The skill must NOT
  change those answers. If it does, it's over-triggering or its guidance bleeds — fix the description.
- **Adversarial probe.** One prompt that *looks* in-scope but where the skill's advice is wrong/dangerous.
  Confirm the dev (or judge) catches it rather than the skill driving confident-but-wrong output.

**Pass:** blind judge agrees WITH ≥ WITHOUT on ≥ 80% of items; zero regression on out-of-scope prompts;
adversarial case handled.

---

## The rubric (apply in Tier 3/4) — score each 0/1/2

| # | Dimension | 0 | 1 | 2 |
|---|---|---|---|---|
| 1 | **Correctness** | wrong/won't build | minor errors | correct, runs |
| 2 | **Follows convention** | ignores house style | partial | matches ADNOC/repo conventions |
| 3 | **Completeness** | stub/TODO | gaps | fully addresses the task |
| 4 | **No over-reach** | edits/advises far outside scope | some drift | stays on task |
| 5 | **Safety / accuracy of claims** | confident & wrong | hedged | accurate, flags uncertainty |
| 6 | **Conciseness / context cost** | bloated | acceptable | tight, earns its tokens |

Max 12. Compare WITH vs WITHOUT totals per prompt, then mean across the eval set.

---

## Quantified reliability bars — pass@k / pass^k

LLM output is nondeterministic: one good run proves little, one bad run damns little. Run each eval
prompt **k times** (k=3 is the practical default) and score reliability, not luck
(pattern popularized by ECC's eval-harness, MIT):

| Metric | Means | Use for | Bar |
|---|---|---|---|
| **pass@3** | at least 1 of 3 runs passes | **capability** — "can it do the thing at all" | **≥ 0.90** across the eval set |
| **pass^3** | all 3 of 3 runs pass | **regression** — "does it never break what worked" | **= 1.00** for release-critical prompts |

Rules that keep the numbers honest:

- **Define the evals BEFORE building the skill** — capability prompts + regression prompts are part
  of the skill's definition of done, not an afterthought. (Same discipline as TDD: RED first.)
- **Grader hierarchy — deterministic > model > human:**
  1. **Code grader** (grep/regex on output, test execution, exit codes) — use whenever checkable;
     it's the only grader allowed to *block* a release gate.
  2. **Model grader** (blind judge + the rubric above, 1–5 or 0–2 scale) — for open-ended quality;
     fine for scoring, **never as a sole release gate** (flaky graders in gates = noise people learn
     to ignore).
  3. **Human grader** — required for ambiguous calls and **always for security-relevant checks.
     Never fully automate security sign-off.**
- **Record every run**, not just the best one. Convention under `ai/governance/evals/<name>/`:
  `eval.md` (prompt set + bars), `runs.log` (append-only run history), `baseline.json`
  (the scores the next version must not regress below).

---

## Definition of Done — before you PR to the shared template

- [ ] Tier 1 clean (parses, no leaks, length budget).
- [ ] Tier 2: fires on bullseye, silent on adjacent + off-topic.
- [ ] Tier 3: eval set committed under `ai/governance/evals/<name>/`; WITH beats WITHOUT by ≥2, no dimension regresses.
- [ ] Tier 4 (always-on content only): blind judge agrees; no out-of-scope regression.
- [ ] **Reliability bars met over k=3 runs:** capability `pass@3 ≥ 0.90`; regression `pass^3 = 1.00`
      on release-critical prompts; `runs.log` + `baseline.json` committed.
- [ ] **No duplicate** — `git grep -il "<core trigger phrase>" .github/skills .github/instructions` finds nothing equivalent.
- [ ] **No contradiction** — doesn't conflict with the ADNOC standard, a team-owned
      `.github/copilot-instructions.md`, or another matching instruction (read all applicable files).
- [ ] `applyTo`/`description` reviewed by one other engineer (the trigger is the riskiest line).
- [ ] PR body links the eval folder and pastes the WITH-vs-WITHOUT score table.

---

## Ongoing eval after it ships — tie to `agent-runs.jsonl`

The pre-ship ladder is a point-in-time gate; telemetry is the standing monitor. Every agent run already
appends a line to `ai/governance/agent-runs.jsonl`. Add a `skills` field listing which skills loaded that run
(*`dashboard.py` reports per-skill usage from this field — log it and it shows up in the rollup*):

```json
{"ts":"2026-06-09T10:00:22Z","agent":"coder","workflow":"spec-to-impl","team":"orders","repo":"orders-api","model":"gpt-5.4","ok":true,"skills":["azure-func-http"]}
```

Then `ai/governance/dashboard.py` can report, per skill:
- **Trigger rate** — % of runs where it loaded. Near-100% on an always-on file is expected; a *narrow*
  skill firing on 60%+ of runs is the over-broad-description smell from Tier 2 — re-evaluate.
- **Co-occurrence with `ok:false`** — if runs that loaded the skill fail more than the baseline, it's
  hurting; re-run Tier 3.
- **Zero-fire after 4 weeks** — never triggers in real use → dead weight; deprecate.

Champions review these in the weekly `agent-runs.jsonl` pass (see `CHAMPIONS.md`). A skill that drifts
on telemetry goes back through Tier 3.

---

## Anti-patterns the eval must catch

1. **Over-broad description** ("helpful coding guidance", "use for backend work") → fires on everything,
   pollutes context, slows every request. *Caught by* Tier 2 adjacent/off-topic prompts + telemetry trigger-rate.
2. **Vague guidance** ("write clean, idiomatic code", "follow best practices") → no behavioral fingerprint;
   WITH ≈ WITHOUT. *Caught by* Tier 3 (no score lift) — if removing it changes nothing, it says nothing.
3. **Duplicate of an existing skill** → two files compete to load, advice diverges over time.
   *Caught by* the DoD `git grep` duplicate check before PR.
4. **Contradicts another instruction** (e.g. one says "throw on error", another "never throw") →
   non-deterministic output, dev confusion. *Caught by* the DoD contradiction read + Tier 4 regression probe.
