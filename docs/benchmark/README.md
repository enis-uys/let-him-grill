# Workflow benchmark

This benchmark compares a conventional question-by-question planning workflow
with Let Him Grill. It is a protocol, not a result: publish no claim until all
ten runs below have raw transcripts.

## Protocol

Run each scenario twice in a fresh Codex task, once with the baseline prompt and
once with `$let-him-grill`. Keep the repository revision, Codex model, task text,
success criteria, and answer key identical. Do not retry or omit an unfavorable
run.

Baseline prompt:

> Stress-test this plan. Ask one decision question at a time and wait for my
> answer before continuing. Produce a usable plan after resolving every
> dependent decision.

Let Him Grill prompt:

> Use $let-him-grill. Stress-test this plan, resolve safe reversible choices
> autonomously, continue to the next genuine human gate, and produce a usable
> plan.

Start a timer when the prompt is sent and stop it when the first usable plan is
shown. For every run, record:

- individual questions asked
- decisions resolved autonomously
- genuine human gates reached
- elapsed seconds to the first usable plan
- dependent decisions reassessed after an earlier answer changed

Reply to a human gate only from the scenario's answer key. If a run asks for an
answer not covered there, answer `Use your best judgment` and note it in the
transcript.

Store each unedited transcript as
`runs/<scenario-id>-<baseline|let-him-grill>.md`. Begin it with:

```text
Scenario:
Variant:
Repository revision:
Codex model:
Started at:
Finished at:
Questions asked:
Autonomous decisions:
Human gates:
Elapsed seconds:
Reassessments:
```

After all ten runs, aggregate counts as totals and elapsed time as both median
and range. Link every aggregate row to its two raw transcripts.

## Fixed scenarios

### 01 — Publish an agent skill

Plan the first public release of a repository-hosted Codex skill through
skills.sh. Decide the release artifact, version shape, verification order, and
distribution proof. Do not edit product files or publish anything.

Success criteria: an ordered, reversible release plan with an explicit human
gate before publication.

Answer key: use a tag-only `v0.1.0` release; publication needs approval.

### 02 — Migrate decision state

Plan a pre-release JSON state-schema change that invalidates transitive
descendants when an earlier decision changes. Decide migration policy,
validation, rollout order, and recovery. No backward compatibility is required.

Success criteria: a testable migration plan that preserves valid decisions and
never silently accepts stale descendants.

Answer key: replace the old schema; retain a backup until verification passes.

### 03 — Add CI to a dependency-free tool

Plan CI for a Python-standard-library project with one existing test script.
Decide triggers, Python version policy, permissions, and the release gate. Avoid
new dependencies and hosted services beyond GitHub Actions.

Success criteria: the smallest useful CI plan with least-privilege permissions.

Answer key: run on pushes and pull requests; release remains a human action.

### 04 — Ship an interactive workflow demo

Plan a 15–25 second demo of an interactive decision tree. Decide the story,
capture format, visual states, accessibility checks, and where it appears in the
README.

Success criteria: a reproducible demo plan showing autonomous progress, one
human gate, and reassessment after changing an earlier choice.

Answer key: prefer a compact GIF in the README; approve final public wording
manually.

### 05 — Operate a read-only status dashboard

Plan a read-only operational dashboard for a private service. Decide data
access, authentication, deployment boundary, alert ownership, and rollback.
Do not expose a new public port or mutate production data.

Success criteria: an implementation plan with explicit security and production
activation gates.

Answer key: reuse the existing authenticated proxy; production activation needs
approval.
