---
name: mentor-task-interpreter
description: Reconstruct mentor chat logs, meeting notes, and attachments into evidence-backed task briefs and Codex handoffs. Use when fragmented supervision needs a directly executable task, not for drafting a project from scratch.
metadata:
  version: "0.1"
  short-description: "Turn mentor records into executable tasks"
---

# Mentor Task Interpreter

Turn scattered mentor communications into a faithful, executable task package. Preserve the distinction between what the mentor said, what the records establish, and what you infer. Do not invent missing attachments, commitments, deadlines, or technical choices.

## Workflow

1. **Inventory inputs.** Assign each chat export, meeting record, document, link, image, and attachment a stable source ID. Record missing or unreadable material as a clarification; do not silently fill it in.
2. **Restore context.** Build a chronological timeline using timestamps when available; otherwise retain source order and mark timing as uncertain. Identify the active project, prior decisions, deliverables, and changes of mind.
3. **Extract instructions.** Capture action verbs, scope, acceptance signals, dates, prohibitions, and conditional language. Resolve pronouns and phrases such as “that figure” or “the previous version” only when their antecedent is evidenced. Link each statement to evidence.
4. **Merge fragments.** Combine complementary fragments into one requirement only when they concern the same object and outcome. Preserve alternatives and uncertainty instead of forcing a merge.
5. **Decide what governs.** Apply [instruction priority](references/instruction-priority.md) and [reconstruction rules](references/reconstruction-rules.md) to superseded, conflicting, and conditional instructions. Record the rationale and evidence for every non-obvious decision.
6. **Produce the package.** Fill `task-spec.json` against [the schema](references/task-spec.schema.json), then render a human-readable brief from [task-brief.md](templates/task-brief.md) and a ready-to-send handoff from [codex-handoff.md](templates/codex-handoff.md). Follow [evidence rules](references/evidence-rules.md).
7. **Validate and hand off.** Run `python3 scripts/validate_task_spec.py task-spec.json`; resolve validation errors. Keep unresolved decisions in `clarifications`, state the confidence, and give Codex only the current effective requirements plus the relevant input paths.

## Output standard

The task brief must state the goal, ordered deliverables and acceptance criteria, inputs and attachments, effective requirements, constraints, deadlines, dependencies, and open questions. The Codex handoff must be self-contained enough to begin work, but it must not present inference as a command. Cite source IDs and locations next to consequential claims.

Use the fixture only as a format example: `python3 scripts/validate_task_spec.py fixtures/meeting-summary.task-spec.json`. Run `python3 scripts/run_checks.py` after changing the skill or schema.
