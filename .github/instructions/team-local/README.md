# Team-local instructions (Ring 3)

Your team's own instruction files live here. The template **never overwrites this directory**.

- Each file must have frontmatter with `applyTo:` (a glob like `"**/*.ts"` or `"**"`) so Copilot
  knows which files to apply the rules to automatically.
- Use for file-type-scoped rules that don't belong in the global `copilot-instructions.md` and
  aren't corrections to existing behavior (those go in `project-learnings.instructions.md` via `/selfimprove`).
- Trial for a sprint or two. If the rules prove useful to other teams, **propose them upstream** to
  `ai-sdlc-template` — that's how a local rule becomes a versioned, fanned-out standard without forking.
