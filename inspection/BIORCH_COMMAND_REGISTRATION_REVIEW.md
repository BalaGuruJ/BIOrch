# BIOrch Command Registration Review

## Overview
An investigation was conducted into command registration collisions between workspace commands (`.gemini/commands/`) and skill commands (`.agents/skills/`).

## Findings

### Command Mapping

| Command Name | Workspace Command | Skill Command | Collision Status |
| :--- | :--- | :--- | :--- |
| `biorch-status` | Yes | Yes | **COLLISION** |
| `biorch-review` | Yes | Yes | **COLLISION** |
| `biorch-task` | Yes | Yes | **COLLISION** |
| `biorch-sync` | Yes | Yes | **COLLISION** |
| `biorch-close` | Yes | No | None |
| `biorch-contract`| Yes | No | None |
| `biorch-governance`| Yes | No | None |
| `biorch-next` | Yes | No | None |
| `biorch-roadmap` | Yes | No | None |
| `biorch-bi-inventory` | No | Yes | None |
| `biorch-contract-review` | No | Yes | None |
| `biorch-implementation` | No | Yes | None |
| `biorch-investigation` | No | Yes | None |
| `biorch-phase-closure` | No | Yes | None |
| `biorch-task-record` | No | Yes | None |
| `biorch-validation` | No | Yes | None |

## Collision Analysis
The Gemini CLI environment automatically registers commands from both the `workspace` and `skill` directories. When a naming collision occurs, the system automatically resolves the ambiguity by renaming the conflicting commands to ensure they remain accessible, typically by prepending `workspace.` to the workspace command or appending a numeric suffix to one of the conflicting commands (e.g., `/workspace.biorch-status` and `/biorch-status1`).

This renaming behavior causes confusion for end-users, who expect consistent command names.

## Recommendation: Canonical Naming
To resolve these collisions and establish a clean, predictable command interface, it is recommended to adopt a distinct naming convention for the two types of commands:

1.  **Workspace Commands:** Prefix workspace-level, human-triggered commands with `cmd-` or `prj-` (e.g., `/cmd-biorch-status`).
2.  **Skill Commands:** Maintain the current skill naming convention (e.g., `/biorch-status`) or prepend `skill-` to make them explicitly identifiable if desired.

Alternatively, migrate functionality entirely to either workspace commands or skills to eliminate the overlap.
