# Let Him Grill

## Where should the decision tree live?

- Type: `human`
- Status: `confirmed`
- Choice: Native Codex visualization
- Reason: It stays in the conversation without a server or separate frontend.

## Where should persistent state live?

- Type: `review`
- Status: `recommended`
- Choice: Workspace JSON
- Reason: The visualization remains a replaceable view.

## How should Grill with Docs be extended?

- Type: `review`
- Status: `recommended`
- Choice: Dedicated orchestrator skill
- Reason: The original skill remains unchanged and independently updateable.

## When should the workflow stop?

- Type: `derived`
- Status: `derived`
- Choice: Only for material decisions
- Reason: This follows directly from the product goal.
