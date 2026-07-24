# AI credits & model selection

Copilot bills by **usage** — GitHub AI Credits (token consumption) pooled across the whole org.
Code completions are free; every chat and agent turn spends credits. Because the pool is shared,
picking the right model tier matters for the whole team.

## Which model for which job

| Tier | Examples | Use when |
|------|----------|----------|
| **Base** | GPT-4o mini, Claude Haiku | Everyday chat, quick questions, explanations, small edits, boilerplate |
| **Workhorse** (frontier) | Claude Sonnet, GPT-4o, GPT-5 class | Agent runs, feature work, code reviews, multi-file changes |
| **Opus-class** | Claude Opus, o1, o3 | Hardest problems — architecture decisions, complex debugging. Use deliberately, **switch back right after**. |
| **Long-context variants** | Any model with 200 k+ context | Only when the task physically needs a large window — they cost more per token |

## The #1 budget burner

The model picker remembers your last choice. If you switched to Opus and forgot to switch back, every subsequent chat silently charges at the highest rate. After an Opus run, reset to your default frontier model before the next ordinary task.

## The practical rule

> Start at Base. Step up to Workhorse when the task needs it. Use Opus deliberately, then step back down.

One well-phrased prompt beats five back-and-forth clarifications — every turn costs credits,
so invest a few seconds up front to be specific.

Current rates and your remaining allowance: **GitHub → Your org → Copilot → Usage** and the
model picker.
