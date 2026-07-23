# Changelog

All notable user-facing changes to Let Him Grill are recorded here.

## [Unreleased]

### Added

- One canonical decision-tree template shared by the Python renderer, native
  Codex fallback, and recorded demo.
- An 18-second workflow demo and accessible poster frame showing autonomous
  progress, a human gate, branch invalidation, and reassessment.
- Reproducible five-scenario workflow benchmark with ten raw transcripts and an
  evidence-backed before-and-after result.
- Invalidated decision paths now offer a direct Codex reassessment action while
  preventing stale options from being selected.
- Decision triage for `auto`, `review`, `human`, `derived`, and `blocked` paths.
- Option triage for recommended, alternative, situational, discouraged, and
  excluded choices.
- Per-option rationale, confidence, reversibility, effort, risk, downstream
  impact, and preferred conditions.
- Deterministic auto-selection when exactly one recommendation is low-risk and
  reversible.
- Subtle option status accents and expandable assessment details in the visual
  decision tree.
- Protection against selecting excluded or invalidated options.
- Transitive invalidation of dependent decisions and their option assessments.
- Explicit Python and runtime-free native Codex backends for visual mode, with
  visible backend selection and matching state rules.

### Changed

- The interactive tree now confirms successful Codex follow-up delivery and
  preserves the complete prompt when the host bridge is unavailable or rejects
  the request.
- Added the verified one-line `skills` CLI installation as the primary setup
  path, while retaining Git installation as a fallback.
- State format moved to version 2; version 1 state is intentionally unsupported
  before the first public release.
- The project and skill were renamed from Grill with Docs Interactive to Let Him
  Grill.
- The public example and generated interface now use English labels.

### Fixed

- Confirmed human decisions now display as confirmed instead of continuing to
  appear as decision-required nodes.
- Native visual rendering now targets and verifies the exact current Codex task
  directory instead of reusing another task's visualization directory.

## [0.0.1] - 2026-07-22

Initial pre-release baseline:

- Compact and visual Grill with Docs workflows.
- Persistent workspace JSON and Markdown export.
- Interactive Codex decision tree with selectable and expandable options.
- Transitive invalidation after changing an earlier decision.
- Python standard-library state engine with no package installation or virtual
  environment requirement.
- README, MIT license, product notes, screenshot, examples, and initial tests.
