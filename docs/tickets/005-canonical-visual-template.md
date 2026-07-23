# Use one canonical visual template

Status: Done

## Problem

The Python backend currently assembles the decision-tree HTML inside
`scripts/decision_state.py`. The native Codex fallback recreates HTML from prose
instructions. This allows both paths, and any separately produced demo, to drift
into different interfaces.

## Goal

Bundle one framework-free HTML template as the visual source of truth. Python
and native Codex rendering must inject state into that same template instead of
reimplementing its structure, styling, or interaction behavior.

## Scope

- Add one canonical template containing the final CSS, markup shell,
  interactions, accessibility behavior, and Codex follow-up bridge.
- Keep decision data and the absolute state path as the only generated inputs.
- Make `python3 scripts/decision_state.py render` load and populate the bundled
  template.
- Make the native fallback copy the bundled template and replace the documented
  data placeholders using Codex file tools only.
- Preserve option selection, Apply selection, Reassess path, descriptions,
  Expand all, Collapse all, status labels, keyboard controls, feedback, and
  compact responsive layout.
- Re-record the README demo from the canonical template.
- Do not add a package, framework, server, build step, or runtime dependency.

## Public test seam

Treat the rendered HTML file as the public boundary:

- rendering succeeds from an installed skill layout
- the output contains no unresolved template placeholders
- the injected state and absolute state path are safely encoded
- the required controls and Codex bridge remain present
- the native instructions point to the exact bundled template and replacement
  contract instead of authoring a new interface

## Acceptance criteria

- The template is the only repository source for visualization CSS and client
  JavaScript.
- Python output is produced from that template and passes the existing renderer
  behavior tests.
- Native fallback instructions require the same template and define its two
  data substitutions precisely.
- A rendered example is visually inspected at desktop and narrow widths.
- The 15–25 second README demo and poster are regenerated from the canonical
  interface and retain the measured scenario 04 summary.
- `python3 scripts/test_decision_state.py` passes without third-party packages.
