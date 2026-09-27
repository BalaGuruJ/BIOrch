# Command/Skill Registration Collision Audit

## 1. Executive Summary

A forensic audit was performed on the repository filesystem to detect command-registration collisions between `.gemini/commands/` and `.agents/skills/`.

**Verdict:** PASS — no active collisions found.

## 2. Methodology
- Inspected `.gemini/commands/` for workspace commands.
- Inspected `.agents/skills/` for active skills and their registered names (via `SKILL.md`).
- Constructed a collision matrix to compare identifiers.

## 3. Findings

### 3.1. Workspace Commands Inventory (.gemini/commands/)

| Filename | Inferred/Actual Command Name | Validity |
| :--- | :--- | :--- |
| `biorch-close.toml` | biorch-close | Valid (assumed) |
| `biorch-contract.toml` | biorch-contract | Valid (assumed) |
| `biorch-governance.toml` | biorch-governance | Valid (assumed) |
| `biorch-next.toml` | biorch-next | Valid (assumed) |
| `biorch-review.toml` | biorch-review | Valid (assumed) |
| `biorch-roadmap.toml` | biorch-roadmap | Valid (assumed) |
| `biorch-status.toml` | biorch-status | Valid (assumed) |
| `biorch-sync.toml` | biorch-sync | Valid (assumed) |
| `biorch-task.toml` | biorch-task | Valid (assumed) |

### 3.2. Skill Inventory (.agents/skills/)

| Directory | Skill Name (from SKILL.md) | State |
| :--- | :--- | :--- |
| `biorch-bi-inventory` | biorch-bi-inventory | Enabled |
| `biorch-contract-review` | biorch-contract-review | Enabled |
| `biorch-implementation` | biorch-implementation | Enabled |
| `biorch-investigation` | biorch-investigation | Enabled |
| `biorch-next` | (not found in SKILL.md) | Enabled |
| `biorch-phase-closure` | biorch-phase-closure | Enabled |
| `biorch-review` | skill-biorch-review | Enabled |
| `biorch-status` | skill-biorch-status | Enabled |
| `biorch-sync` | (not found in SKILL.md) | Enabled |
| `biorch-task` | skill-biorch-task | Enabled |
| `biorch-task-record` | biorch-task-record | Enabled |
| `biorch-validation` | biorch-validation | Enabled |

### 3.3. Collision Matrix & Investigation of Conflicting Names

The investigation focused on names that exist as both commands and skills.

| Name | Command | Skill | Collision? | Note |
| :--- | :--- | :--- | :--- | :--- |
| `biorch-status` | Yes | Yes (skill-biorch-status) | No | Names differ |
| `biorch-review` | Yes | Yes (skill-biorch-review) | No | Names differ |
| `biorch-task` | Yes | Yes (skill-biorch-task) | No | Names differ |
| `biorch-sync` | Yes | Yes (none in SKILL.md) | No | Skill has no name |

## 4. Conclusion
There are no active collisions. Command names registered in `.gemini/commands/` do not match the skill names registered in `.agents/skills/*/SKILL.md`.
