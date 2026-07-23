# Let Him Grill roadmap

## Product promise

> Let the agent cook. Grill only what matters.

Let Him Grill should resolve reversible decisions autonomously and interrupt the
user only when a choice materially changes the outcome.

## 1. Complete the core workflow

- [x] Implement decision and option triage from
      [ticket 001](tickets/001-decision-and-option-triage.md).
- [x] Use the same triage model in compact and visual modes; persist it whenever
      state is materialized.
- [x] Auto-select a clearly superior low-risk option.
- [x] Create a human gate for meaningful trade-offs.
- [x] Reassess dependent decisions after an earlier choice changes.
- [x] Verify the runtime-free visual path from
      [ticket 004](tickets/004-native-codex-fallback.md) in a fresh Codex task.

Done when one realistic workflow resolves several decisions autonomously, stops
at a genuine human gate, and correctly rebuilds an affected branch after a
change.

## 2. Make installation effortless

- [x] Put the one-line Codex install command near the top of the README:

  ```bash
  npx skills add enis-uys/let-him-grill -g -a codex -y
  ```

- [x] Keep the Git installation as a fallback.
- [x] Verify repository discovery and installation in a clean environment.
- [x] Verify `$let-him-grill` invocation in a fresh Codex task.

Done when a new user can install and invoke `$let-him-grill` without editing
files manually.

## 3. Prove the benefit

- [x] Complete [ticket 002](tickets/002-benchmark-before-after.md).
- [x] Define 5–10 representative planning scenarios.
- [x] Compare normal Grill with Docs against Let Him Grill.
- [x] Record questions asked, autonomous decisions, human gates, and time to a
      usable plan.
- [x] Publish honest aggregate results and raw examples.

Done when the README can support one concrete claim such as "8 questions became
2 human gates" without relying on invented or cherry-picked data.

## 4. Show the workflow

- [x] Complete [ticket 005](tickets/005-canonical-visual-template.md) so the
      Python backend, native fallback, and demo share one interface.
- [x] Complete [ticket 003](tickets/003-demo-gif.md).
- [x] Record a 15–25 second demo showing autonomous progress, a human gate, and
      switching an earlier option.
- [x] Add a compact post-run summary such as:
      `9 decisions evaluated · 7 resolved autonomously · 2 human gates`.
- [x] Make the summary easy to copy as Markdown.
- [x] Restructure the README around promise, demo, install, before/after,
      operation, safety, attribution, and license.

Done when the project can be understood from the README in under one minute.

## 5. Prepare the first release

- [x] Add a small CI check for `python3 scripts/test_decision_state.py`.
- [ ] Remove obsolete or generated repository files.
- [ ] Add relevant GitHub topics and a social preview image.
- [ ] Publish `v0.1.0` with the demo and installation command.
- [ ] Confirm discoverability through skills.sh.

Done when the tagged release installs cleanly and the repository has no known
setup or documentation blockers.

## 6. Launch

- [ ] Share the finished project with Matt Pocock and keep the inspiration link
      prominent.
- [ ] Publish one short problem → demo → install post.
- [ ] Share it with Codex and agent-skill communities.
- [ ] Turn repeated user feedback into focused issues; avoid speculative feature
      expansion.

Do not start launch work before steps 1–4 are reproducible.
