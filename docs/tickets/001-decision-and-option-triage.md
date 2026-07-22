# Decision and option triage

Status: Done

## Goal

Let Him Grill should triage both decisions and their options before interrupting the user.

## Decision triage

- `auto`: reversible and low-impact; Codex chooses and continues.
- `review`: Codex chooses provisionally and flags it for later review.
- `human`: architecture, cost, security, or difficult-to-reverse impact; stop for input.
- `blocked`: required information is missing.

Consider dependencies and the cost of changing the decision later, not only the decision in isolation.

## Option triage

Classify each option as:

- recommended
- solid alternative
- situational
- not recommended
- excluded

Show a short rationale plus confidence, reversibility, effort, risk, downstream effects, and conditions under which the option would become preferable.

## Behavior

- Auto-select a clearly superior low-risk option.
- Create a human gate when similarly strong options involve a meaningful trade-off.
- Keep alternatives visible and allow earlier selections to be changed.
- Re-evaluate dependent decisions after a change.

## Acceptance criteria

- Every decision has one decision-triage state.
- Every option has one option-triage state and a short rationale.
- Autopilot never crosses a human gate.
- Changing an earlier selection marks affected descendants for re-evaluation.
- Compact and visual modes use the same underlying triage result.
