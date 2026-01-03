# Model Card: LLM-as-Judge (Placeholder)

## What the judge does
In a full benchmark run, an LLM-as-judge can:
- extract atomic claims from a response
- check whether claims are supported by provided context
- label citation relevance (valid/invalid)
- flag policy-violating content for human review

## Why this repo does NOT include a judge model
This starter repository is offline and avoids external model dependencies by default.

## Known risks / biases
- Judges may favor certain writing styles
- Judges can miss subtle unsupported claims
- Judges can inherit vendor/model biases

## How to integrate later
- Add a `judging/` module and a script that calls your chosen judge via API
- Keep raw judge outputs for auditability
- Add a human adjudication layer and report agreement
