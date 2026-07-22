# Repository instructions

- Prefer the smallest correct change and Python standard library over new
  dependencies.
- Preserve compact and visual modes unless a task explicitly changes both.
- Run `python3 scripts/test_decision_state.py` after behavior or state changes.
- Update `CHANGELOG.md` in the same change for user-visible features, fixes,
  state-schema changes, installation changes, and compatibility breaks.
- Add ongoing work under `Unreleased`. When publishing a release, move those
  entries to a dated version section and recreate an empty `Unreleased` section.
- Do not add changelog entries for formatting-only or invisible internal edits.
