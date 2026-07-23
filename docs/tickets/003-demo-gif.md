# Record the workflow demo

Status: Done

Depends on: [ticket 002](002-benchmark-before-after.md)

## Goal

Create a 15–25 second GIF or short video that makes the workflow understandable
without relying on a static decision-tree screenshot.

## Sequence

Show one representative benchmark scenario:

1. Before: Codex asks several decisions as separate questions.
2. After: Let Him Grill resolves the safe choices and stops at genuine human
   gates.
3. Change an earlier option.
4. Show the dependent branch being invalidated and reassessed.
5. End with a compact summary such as
   `8 decisions evaluated · 6 resolved autonomously · 2 human gates`.

Use the actual measured values from ticket 002 rather than forcing the example
numbers.

## Deliverables

- Optimized GIF or short video suitable for GitHub and social sharing.
- Poster frame or screenshot for clients that do not autoplay media.
- README placement near the product promise and installation command.
- Short accessible caption describing the visible state changes.

## Acceptance criteria

- The demo lasts 15–25 seconds.
- Autonomous progress, a human gate, an earlier-option change, and dependent
  reassessment are all visible.
- Text remains readable at the README display size.
- The summary matches the recorded benchmark run.

## Result

The 18-second [demo](../demo.gif) and its [poster frame](../demo-poster.png)
show the measured scenario 04 path: six decisions evaluated, five resolved
autonomously, one human gate, then one dependent reassessment. Every frame is
rendered from the canonical visual template tracked by
[ticket 005](005-canonical-visual-template.md).
