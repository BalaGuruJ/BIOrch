# BIOrch Command Registration Root Cause Analysis

## Findings

### Collision Mechanism
The Gemini CLI environment automatically registers both files in `.gemini/commands/` (workspace commands) and `name:` fields from `.agents/skills/*/SKILL.md` (skill commands) as slash commands.

A collision occurs when the basename of a `.toml` file in `.gemini/commands/` matches the `name:` field in a skill's `SKILL.md` file. 

For example, `biorch-status` collides because:
- `.gemini/commands/biorch-status.toml` exists.
- `.agents/skills/biorch-status/SKILL.md` contains `name: biorch-status`.

### Observed Renaming Behavior
When the Gemini CLI detects this collision at startup, it resolves the ambiguity by:
1. Registering one version as the canonical `/biorch-status`.
2. Renaming the conflicting command, typically prepending `workspace.` to the workspace command (e.g., `/workspace.biorch-status`) or appending a numeric suffix (e.g., `/biorch-status1`) to one of the registration sources to ensure accessibility.

This behavior is deterministic based on registration order, which may not be guaranteed.

### Root Cause
The root cause is the overlapping naming convention used for both workspace slash-command definition files (`.gemini/commands/biorch-*.toml`) and the `name:` property within skill definitions (`.agents/skills/biorch-*/SKILL.md`).

## Conclusion
To establish `.gemini/commands/` as the canonical source without disabling skills:
- The skill `name:` property must be distinct from the workspace command names if they are meant to be separate entities, OR
- The skill `name:` property should only be used for skill-specific activation/discovery, not slash-command registration.

Since skill definitions in this project are primarily procedural documentation, the `name:` property in `SKILL.md` is currently fulfilling a role beyond just description, triggering inadvertent command registration.
