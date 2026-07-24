---
name: let-him-grill
description: Stress-test a plan or design with project evidence, triage decisions and their options, automatically resolve reversible low-risk choices, and pause at genuine human decision gates. Supports compact text-first and visual persistent-tree modes. Use when the user invokes interactive or autonomous Grill with Docs, wants fewer step-by-step interruptions, asks to explore branches until human judgment is required, or wants to revisit earlier recommendations.
---

# Let Him Grill

Extend `grilling` and `domain-modeling`; do not modify them. Preserve their
evidence-first behavior and documentation rules while batching decisions that do
not need human judgment.

## Mode

Honor an explicitly requested mode. Otherwise choose `compact` for short or
linear discussions and `visual` when decisions branch, depend on one another, or
the user wants to revisit them. State the selected mode once.

- `compact` / `kompakt`: Work text-first. Do not create state for a single
  linear decision. At the human gate, show the resolved path, recommendation,
  2–4 real options, and material consequences as concise text. Create state or
  render a tree only when branching, revisiting, or the user requests it.
- `visual` / `visuell`: Preserve the full current behavior. Create
  `.grill/decisions.json`, persist every decision, render the interactive tree
  at each human gate and after every change, and allow earlier choices to
  invalidate their dependent subtree.

The decision logic and human-gate rules are identical in both modes. Users may
switch modes at any time. Switching to `visual` materializes known decisions;
switching to `compact` keeps existing state but stops automatic rendering.

## Backend

Compact mode needs no runtime. For visual mode, honor an explicitly requested
backend. Otherwise run `python3 --version` once and select:

- `python`: Use `decision_state.py` when Python 3 is available.
- `native`: Use Codex file and visualization tools when Python 3 is unavailable.

State the selection once as `Visual mode · Python backend` or
`Visual mode · Native Codex fallback`. If the user explicitly requires Python
and it is unavailable, stop instead of silently changing backends. Never install
Python or another runtime without permission.

## Workflow

1. Read relevant project docs, code, `CONTEXT.md`, and ADRs. Resolve discoverable
   facts with tools instead of asking.
2. Select the mode and backend. In `visual`, create `.grill/decisions.json` with
   the selected backend if no active state exists. In `compact`, keep the path
   in the conversation until persistence is useful.
3. Build the next decision and 2–4 real options. Assess every option as
   `recommended`, `solid-alternative`, `situational`, `not-recommended`, or
   `excluded`. Record a short reason, confidence, reversibility, effort, risk,
   downstream impact, and when the option becomes preferable.
4. Classify it:
   - `auto`: one option follows from evidence, is low-risk, and is cheap to
     reverse. Choose it and continue.
   - `review`: a strong reversible default exists, but preference may matter.
     Choose it provisionally and continue.
   - `human`: choice changes goals, architecture, security, privacy, external
     cost, provider lock-in, operations, or another hard-to-reverse outcome.
     Stop before choosing.
   - `derived`: choice is forced by an earlier confirmed decision.
   - `blocked`: required evidence is missing and guessing could materially
     change the result. Stop and request only that evidence.
   Use `human` when similarly strong options carry a meaningful trade-off.
5. Continue across `auto`, `review`, and `derived` nodes until reaching `human`,
   `blocked`, or shared understanding. For `auto`, allow the script to choose
   only when exactly one `recommended` option is low-risk and reversible. In
   `visual`, add each decision with
   `decision_state.py add` with the Python backend or update the state directly
   with the native backend.
6. In `compact`, present the human gate as concise text. In `visual`, render the
   state into the exact visualization directory assigned to the current Codex
   task with `decision_state.py render`. Never reuse a visualization directory
   from another task or infer it from an earlier artifact. Confirm the rendered
   file exists in the current task's directory, then embed it using:

   `::codex-inline-vis{file="<rendered-filename>.html"}`

7. When a follow-up applies an earlier persisted option, use
   `decision_state.py choose` or the native invalidation procedure below. It
   invalidates all transitive dependants. Re-research and rebuild only those
   nodes; render again only in `visual`.
8. Update domain terminology inline through `domain-modeling`. Create an ADR
   only when that skill's three ADR conditions all hold.
9. At shared understanding, summarize confirmed human decisions, provisional AI
   choices, assumptions, remaining risks or blockers, and the ordered
   implementation plan.
10. Ask the user to confirm that summary. Do not implement the discussed plan
    until the user confirms shared understanding.
11. After confirmation, update an existing canonical planning, specification,
    or decision document when the repository already has that pattern or the
    user requested documentation. Update the existing document instead of
    creating a duplicate. Otherwise keep the implementation plan in the
    conversation. Keep `CONTEXT.md` limited to domain terminology and create
    ADRs only under the rules above.

## Human gate

Stop when any answer is yes:

- Would changing this later require migration, broad rework, or coordination?
- Does it change product intent, audience, scope, or user-visible trade-offs?
- Does it authorize spend, external actions, data exposure, or security risk?
- Are multiple options reasonable because of personal or business preference?
- Is evidence missing and guessing could materially change the result?

Confidence alone never authorizes an automatic choice. Risk and reversibility
take priority.
Never select an `excluded` option. Reassess it only after its conflicting
requirement changes.

## Commands

Run the bundled script with Python 3 and no third-party dependencies. It needs
no virtual environment, package install, or lockfile. Check `python3 --version`
before the first command. If Python 3 is unavailable, do not install it without
permission; update `.grill/decisions.json` with file tools, apply the same
transitive invalidation rules, and populate the bundled visual template.

Resolve `<skill-dir>` to the directory containing this `SKILL.md`.

```bash
python3 <skill-dir>/scripts/decision_state.py init \
  .grill/decisions.json --title "Decision title"

python3 <skill-dir>/scripts/decision_state.py add \
  .grill/decisions.json --id storage --question "How store state?" \
  --type auto \
  --option local-json="Local JSON::Portable and easy to inspect" \
  --option sqlite="SQLite::Useful for larger queryable state" \
  --assessment 'local-json={"triage":"recommended","reason":"No service required","confidence":0.94,"reversible":true,"effort":"low","risk":"low","impact":"Keeps state local","preferredWhen":"One workspace owns the plan"}' \
  --assessment 'sqlite={"triage":"situational","reason":"Adds query support","confidence":0.86,"reversible":true,"effort":"medium","risk":"low","impact":"Adds schema maintenance","preferredWhen":"The tree needs complex queries"}'

python3 <skill-dir>/scripts/decision_state.py choose \
  .grill/decisions.json storage sqlite --actor human

python3 <skill-dir>/scripts/decision_state.py render \
  .grill/decisions.json /absolute/thread-visualization/decision-tree.html

python3 <skill-dir>/scripts/decision_state.py export \
  .grill/decisions.json docs/decision-path.md
```

Use `--depends-on <id>` once per dependency. Use `--replace` when rebuilding an
invalidated node with refreshed options or reasoning.

## Native backend

Do not call `python3`, Node.js, a shell renderer, or another runtime. Use Codex
file tools for all operations:

1. Create version 2 state as `{"version":2,"title":"...","nodes":[]}`. Use only
   these exact schema values; never invent synonyms:
   - `type`: `auto`, `review`, `human`, `derived`, or `blocked`
   - `status`: `recommended`, `confirmed`, `pending`, `derived`, or `invalidated`
   - `actor`: `ai`, `human`, or `null`
   - option assessment `status`: absent, or `invalidated`
2. Before every write, read the complete current state and validate those exact
   value sets, unique node IDs, known dependencies, valid option IDs, one
   assessment per option, and no selected `excluded` or invalidated option. Use
   `examples/decisions.json` as the schema example. Stop instead of writing when
   any field uses an unknown value.
3. For an `auto` node, select only when exactly one option is `recommended`,
   low-risk, and reversible. Otherwise promote the node to a human gate.
4. When a choice changes, compute the full transitive descendant set from
   `dependsOn`. Set every descendant's `choice` and `actor` to `null`, status to
   `invalidated`, reason to `Earlier dependency changed; reassessment required.`,
   confidence to `null`, and every option assessment status to `invalidated`.
5. Apply the complete JSON update in one file edit. Never partially update state.
6. Read `<skill-dir>/assets/decision-tree.html` completely. It is the canonical
   visual source; never recreate or restyle its HTML, CSS, or JavaScript.
7. Serialize the complete validated state as JSON and escape every `<` as
   `\u003c`. Replace the template's single
   `__LET_HIM_GRILL_STATE_JSON__` placeholder with that JSON object.
8. Encode the absolute state-file path as a JSON string, escape every `<` as
   `\u003c`, and replace the single
   `__LET_HIM_GRILL_STATE_PATH_JSON__` placeholder with that string.
9. Write the resulting self-contained fragment to the exact visualization
   directory assigned to the current Codex task. Never reuse a directory from
   another task or an earlier artifact. Confirm neither `__LET_HIM_GRILL_`
   placeholder remains; otherwise stop instead of presenting a broken view.
10. Confirm the HTML file exists in the current task's visualization directory,
   embed it with `::codex-inline-vis{file="<rendered-filename>.html"}`, and inspect
   the result before presenting it. If inline visualization tools are
   unavailable, show the same decision content as compact text.

## State rules

- Treat `.grill/decisions.json` as source of truth; the visualization is a view.
- Never silently overwrite a confirmed human choice.
- Reusing an invalidated recommendation requires fresh evidence.
- Replace invalidated nodes with fresh option assessments; do not reuse stale
  option triage.
- Keep reasons factual and short. Record uncertainty explicitly.
- In `visual`, render a new visualization after every persisted change; old
  responses remain historical snapshots.
