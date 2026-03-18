# Contributing to MCP Aegis

## 1. Scope

MCP Aegis is intended to become a real security project, not a concept repository. Contributions should improve correctness, traceability, isolation, or operator usability.

## 2. Engineering Standards

Contributions should favor:

- explicit data models over implicit behavior
- deterministic policy evaluation
- explainable security decisions
- minimal privilege defaults
- reproducible local development

Avoid:

- hidden fallback behavior
- broad defaults for convenience
- scoring logic without evidence output
- runtime shortcuts that bypass policy

## 3. Repository Expectations

Before opening a pull request:

- update docs when behavior changes
- include tests for policy logic, parsing, or security-sensitive flows
- keep component boundaries clear
- avoid introducing a new runtime dependency without justification

## 4. Security Reporting

Do not open public issues for unpatched vulnerabilities that can put users at risk.

Use a private disclosure path once one exists. Until then, security-sensitive concerns should be described minimally in public and accompanied by a proposed remediation approach.

## 5. Change Discipline

For high-impact changes, contributors should explain:

- which threat or requirement the change addresses
- what trust boundary is affected
- what new failure modes are introduced
- how the change is tested
