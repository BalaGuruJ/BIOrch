# GEMINI CLI Command Workflow Validation

## Commands Inspected
- /biorch-next
- /biorch-review
- /biorch-status
- /biorch-task

## Registration Result
- Files exist in `.gemini/commands/`:
  - `biorch-next.toml`
  - `biorch-review.toml`
  - `biorch-status.toml`
  - `biorch-task.toml`
- Registration verified based on file presence in the standard directory.

## Validation Result for Each Command

| Command | Valid TOML | Prompt Present | Description Present | Argument Handling (`{{args}}`) |
| :--- | :--- | :--- | :--- | :--- |
| `/biorch-next` | Yes | Yes | Yes | N/A (no args) |
| `/biorch-review` | Yes | Yes | Yes | Correct (`"{{args}}"`) |
| `/biorch-status` | Yes | Yes | Yes | N/A (no args) |
| `/biorch-task` | Yes | Yes | Yes | Correct (`"{{args}}"`) |

## Argument-Handling Result
- Commands `/biorch-task` and `/biorch-review` correctly utilize `{{args}}` to accept inputs for objectives and review focus, respectively.

## Skill/Command Relationship
- The commands align with the project-local skills found in `.agents/skills/`.
- The governance procedures outlined in `GEMINI.md` and `governance/gemini/PHASE_INDEX.md` are respected by the commands (read-only, governance-focused).

## Defects
- None detected.

## Recommended Corrections
- None required.

## Exact Commands/Tests Executed
- Inspected `.gemini/commands/` for TOML file presence.
- Read and validated TOML file syntax and structure.
- Compared prompt content against project governance rules in `GEMINI.md`.

## Final Status: PASS
