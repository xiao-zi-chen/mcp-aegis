# MCP Aegis Roadmap

## 1. Standard

This roadmap is written as an execution document, not a wish list. Each phase has concrete exit criteria. If a phase does not meet its exit criteria, the project should not claim the next milestone.

## 2. Phase 0: Foundation

Status: in progress

Goals:

- define architecture
- define threat model
- define policy model
- define repo structure and implementation boundaries

Exit criteria:

- architecture document is stable enough to code against
- threat model names the MVP attacker classes and controls
- policy schema exists and validates a reference bundle
- repository documents the first build order

## 3. Phase 1: Control Plane MVP

Goals:

- sync metadata from the official MCP registry
- normalize server and package identity
- expose a simple subregistry API
- store findings, policy bundles, and package versions in Postgres

Deliverables:

- registry sync service
- Postgres schema migration set
- control API skeleton
- reference package metadata model

Exit criteria:

- a synced server record can be queried from the local API
- the API returns Aegis metadata placeholders
- package version and digest identity are persisted consistently

## 4. Phase 2: Scan and Policy MVP

Goals:

- run static analyzers against package artifacts
- calculate explainable risk scores
- evaluate policy bundles for install decisions
- provide a CLI that resolves install requests through policy

Deliverables:

- scan orchestrator
- first analyzer set
- risk scoring engine
- policy evaluation library
- CLI installer

Exit criteria:

- a package can be scanned locally and assigned a score
- policy evaluation produces a deterministic decision trace
- the CLI can deny, review, or allow an install using a real bundle

## 5. Phase 3: Runtime Isolation MVP

Goals:

- launch local MCP servers inside Docker
- enforce mount restrictions and resource limits
- emit runtime audit events

Deliverables:

- sandbox launcher
- runtime profile mapping
- audit event writer
- restricted profile integration tests

Exit criteria:

- a local stdio MCP server can be launched inside an isolated profile
- denied filesystem or network actions are visible in logs
- runtime events reference the package, version, and policy bundle used

## 6. Phase 4: Gateway and Remote Controls

Goals:

- proxy remote MCP traffic through a gateway
- enforce remote target policy
- capture remote usage and auth decision events

Deliverables:

- gateway service
- remote policy evaluator
- auth validation hooks
- remote audit pipeline

Exit criteria:

- an allowed remote server can be reached through the gateway
- a denied remote target is blocked with an explainable decision
- remote access decisions are replayable from audit logs

## 7. Phase 5: Hardening

Goals:

- reduce bypass paths
- improve sandbox isolation options
- expand malicious sample coverage
- improve override and review workflows

Deliverables:

- gVisor or microVM evaluation
- malicious sample corpus
- policy override workflow
- signed policy bundle support

Exit criteria:

- the project blocks at least one intentionally malicious sample end to end
- the hardened runtime path is documented and tested
- override flows are explicit, attributable, and auditable

## 8. Workstreams

The work should run in four long-lived tracks:

- protocol and data model
- scanning and scoring
- runtime isolation
- UX and operator workflows

## 9. Immediate Next Build Order

The next implementation steps should be:

1. create the policy schema and reference example
2. scaffold the control API and registry sync service
3. define the Postgres entities and migration plan
4. build the first static analyzers
5. build the CLI policy evaluation flow

## 10. Quality Bar

Before claiming an MVP release, the repository should include:

- deterministic tests for policy evaluation
- integration tests for sandbox profiles
- sample malicious and benign MCP fixtures
- reproducible local development instructions
- architecture and threat documents that match the codebase
