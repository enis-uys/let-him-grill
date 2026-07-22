# Verify the native Codex fallback

Status: Done

## Goal

Keep compact and visual workflows usable without Python by using only native
Codex file and visualization tools.

## Behavior

- Announce `Python backend` or `Native Codex fallback` once in visual mode.
- Honor an explicitly requested backend.
- Never install Python or silently switch away from an explicitly required
  Python backend.
- Keep `.grill/decisions.json` version 2 as the source of truth.
- Apply the same validation, auto-selection, excluded-option protection, and
  transitive invalidation rules in both backends.
- Fall back to compact text when the host cannot display inline HTML.

## Acceptance scenario

In a fresh Codex task where `python3` is not used:

1. Start visual mode with the native backend.
2. Create three or four dependent decisions with two to four assessed options.
3. Render the interactive tree and expand decision and option descriptions.
4. Apply a human choice through the visualization.
5. Change an earlier choice.
6. Confirm that every transitive descendant is invalidated and reassessed.
7. Confirm that no Python, Node.js, server, or package installation ran.

## Acceptance criteria

- The backend is visible before the first decision.
- Native state matches the documented version 2 schema.
- The first render resolves from the current task's visualization directory
  without an `ENOENT` recovery step.
- The acceptance scenario completes in a fresh task.
- Python and native results have the same decisions, choices, and invalidated
  descendants for the scenario.
- README examples cover automatic, Python, and native selection.
