# MCP Aegis Policy Specification

## 1. Purpose

MCP Aegis uses policy as code to decide:

- which MCP servers may be installed
- which versions or digests are allowed
- whether a server must run in a sandbox
- what files, network targets, and environment variables it may access
- whether a remote server may be contacted

This document defines the first policy model for the project. The machine-readable schema lives in [packages/policy-spec/schema.json](../packages/policy-spec/schema.json).

## 2. Policy Model

A policy bundle contains:

- metadata
- default behavior
- selectors that match MCP servers
- rules with actions
- sandbox profiles
- environment and secret mappings
- remote target controls

Top-level structure:

```yaml
apiVersion: mcpaegis.io/v1alpha1
kind: PolicyBundle
metadata:
  name: default-team-policy
  version: 1
spec:
  defaults:
    installDecision: review
    runtimeProfile: restricted
    remoteAccess: deny
  profiles:
    sandbox:
      restricted: ...
      trusted: ...
  rules:
    - id: allow-approved-local
      match: ...
      action: ...
```

## 3. Evaluation Model

Policy evaluation should be deterministic and explainable.

Order:

1. validate bundle schema
2. load defaults
3. evaluate rules in declared order
4. apply the first terminal decision for install or runtime
5. merge non-terminal attributes when explicitly designed to be mergeable
6. emit a decision trace

Terminal decisions:

- `allow`
- `review`
- `restricted`
- `deny`

Rules should be processed top to bottom. A later rule should not silently override a terminal deny from an earlier rule.

## 4. Match Selectors

Rules may match on:

- `source.registry`
- `source.packageType`
- `server.id`
- `server.name`
- `publisher`
- `version`
- `digest`
- `transport`
- `risk.score`
- `risk.class`
- `ownership.verified`
- `remote.url`
- `labels`

Examples:

```yaml
match:
  source:
    registry: official
    packageType: pypi
  server:
    name: filesystem
  transport:
    in: [stdio]
```

```yaml
match:
  risk:
    score:
      gte: 50
```

## 5. Actions

An action may specify:

- install decision
- required sandbox profile
- required digest pinning
- allowed filesystem mounts
- allowed outbound domains
- allowed environment variables
- remote access decision
- reason message

Example:

```yaml
action:
  installDecision: restricted
  runtimeProfile: restricted
  requireDigestPin: true
  remoteAccess: deny
  reason: "High-risk packages require explicit review and restricted runtime."
```

## 6. Sandbox Profiles

Sandbox profiles are named runtime templates. A profile should define:

- whether the root filesystem is read-only
- allowed bind mounts
- temp directory behavior
- network mode
- allowed outbound targets
- CPU limit
- memory limit
- max process count
- max execution time
- allowed environment variables

Recommended first profiles:

- `trusted`
  - moderate isolation for internally reviewed servers

- `restricted`
  - default profile for third-party local servers

- `detonated`
  - aggressive isolation for suspicious packages in dynamic analysis

## 7. Filesystem Mounts

Mount definitions should be explicit and narrow.

Each mount may define:

- `hostPath`
- `containerPath`
- `readOnly`
- `createIfMissing`

Bad pattern:

```yaml
hostPath: /Users/alice
containerPath: /workspace
readOnly: false
```

Good pattern:

```yaml
hostPath: ./project
containerPath: /workspace/project
readOnly: true
```

## 8. Network Controls

The MVP should treat network egress as denied by default for restricted profiles.

Rules may allow:

- exact domains
- domain suffixes
- explicit ports

Example:

```yaml
network:
  mode: egress-allowlist
  allow:
    - host: api.github.com
      ports: [443]
    - suffix: .stripe.com
      ports: [443]
```

## 9. Secrets and Environment Variables

The host environment must not be passed through wholesale.

Supported controls:

- explicit allowlist of env var names
- secret references by logical name
- per-profile secret mapping

Example:

```yaml
environment:
  allow:
    - GIT_AUTHOR_NAME
    - GIT_AUTHOR_EMAIL
secrets:
  refs:
    - github_token
```

## 10. Remote Access Policy

Remote MCP access requires separate policy because there is no local package sandbox to rely on.

Remote controls should include:

- `allow`, `review`, or `deny`
- allowed hosts
- required verified ownership
- required TLS
- required issuer or audience constraints

Example:

```yaml
remote:
  access: review
  requireVerifiedOwnership: true
  allowedHosts:
    - mcp.example.com
  auth:
    requireTls: true
    allowedAudiences:
      - mcpaegis-gateway
```

## 11. Decision Trace

Every decision should produce a structured trace:

```json
{
  "bundle": "default-team-policy",
  "bundleVersion": 1,
  "decision": "restricted",
  "matchedRules": ["restrict-high-risk"],
  "runtimeProfile": "restricted",
  "requireDigestPin": true
}
```

If the user overrides a `review` or `restricted` result, the override reason should also be captured.

## 12. Versioning

The first schema version is:

- `apiVersion: mcpaegis.io/v1alpha1`

Versioning rules:

- new optional fields may be added in minor revisions
- field meaning must not change silently
- terminal decisions and evaluation order are compatibility-sensitive

## 13. Example Bundle

The reference example lives in [packages/policy-spec/examples/default-policy.yaml](../packages/policy-spec/examples/default-policy.yaml).

## 14. Design Constraints

The policy format must remain:

- readable by humans during review
- strict enough for machine validation
- deterministic enough for audit replay
- narrow enough that teams can reason about precedence

If a future feature makes the policy model opaque or hard to replay, it should be rejected or moved out of the core policy path.
