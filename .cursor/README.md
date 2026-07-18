# Cursor configuration

Agent guidance for Extended-VRM-Specs: specification prose, ADRs, and schema docs.

## Included

| Path | Purpose |
|------|---------|
| `rules/specs-repository.mdc` | Repo purpose and boundaries |
| `rules/specs-documentation.mdc` | How to write specs (normative language, structure) |
| `rules/obsidian-markdown.mdc` | Obsidian YAML tags with GitHub-compatible document bodies |
| `rules/deslop-markdown.mdc` | Run deslop on authored `.md` prose before handoff |
| `rules/handoff-and-git.mdc` | Diff/handoff/git safety |
| `skills/deslop/` | De-slop skill + tell catalog + register guide |

## Deliberately not included

- Game/UI player-facing copy deslop rules
- Unity C#, meta, asmdef, or Editor-agent workflows
- Game backlog, story, or content naming policies

## Triggers

- User says **deslop**, **de-slop**, `/deslop`, **remove AI tells**, or **humanize**
- Agent drafts or materially edits markdown prose before handoff
