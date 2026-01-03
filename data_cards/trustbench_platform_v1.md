# Dataset Card: TrustBench-Platform v1 (Sample)

## Summary
A tiny, offline sample dataset for demonstrating evaluation of context-grounded QA.

## Intended use
- Unit tests and examples
- CI validation of repo workflows
- Starter scaffolding for larger, licensed datasets

## Data fields
- id: unique item identifier
- context_id: stable identifier for the context passage
- context: provided evidence passage
- question: user question
- answer: short gold answer string

## Licensing
This sample dataset is synthetic/demo content. Replace with properly licensed datasets for real studies.

## Limitations
- Too small for statistical conclusions
- Faithfulness scoring in this starter repo uses a simple proxy
- Does not represent real-world domain complexity

## Recommended extensions
- Add adversarial contexts (distractors)
- Add longer contexts and multi-document settings
- Add ambiguity + safety sets with careful curation
