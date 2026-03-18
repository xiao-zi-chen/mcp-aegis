# MCP Aegis Threat Model

## 1. Purpose

This document defines the first threat model for MCP Aegis. It is intentionally practical: the goal is to identify the attacks the MVP must materially reduce, not to claim total protection against every MCP risk.

This threat model applies to:

- the MCP Aegis subregistry
- the scan pipeline
- the policy engine
- the CLI installer
- the Docker-based sandbox launcher
- the optional MCP gateway

## 2. Security Goals

The MVP should provide meaningful reduction for these risks:

- installing a malicious or obviously unsafe MCP server
- running a local MCP server with unnecessary filesystem or network access
- allowing unreviewed MCP version drift in team environments
- losing the forensic trail for who installed or ran a server and under which policy
- trusting remote MCP servers without clear ownership, auth, or target restrictions

The MVP does not need to fully solve:

- nation-state level sandbox escape resistance
- perfect malware classification
- prevention of all prompt injection at the model layer
- formal verification of third-party MCP server behavior

## 3. Assets

The assets that matter most are:

- user files and project source code
- local secrets and environment variables
- organization policies and allowlists
- approved package digests and version pins
- audit records and scan evidence
- OAuth access tokens and service credentials
- trust metadata for MCP servers

## 4. Trust Boundaries

The architecture introduces four primary trust boundaries:

1. Host client to MCP Aegis
   - the client may be trusted, semi-trusted, or misconfigured

2. MCP Aegis to third-party MCP server
   - the server is untrusted until policy and scan checks pass

3. MCP Aegis to sandbox runtime
   - the runtime must strongly limit the consequences of server execution

4. Sandbox runtime to protected resources
   - filesystem, network, secrets, and process execution must be explicitly scoped

## 5. Threat Actors

### 5.1 Malicious Package Publisher

Publishes a new MCP package or update designed to steal files, exfiltrate secrets, or execute arbitrary commands.

### 5.2 Compromised Maintainer

Takes over an existing trusted server through stolen credentials or a supply-chain compromise.

### 5.3 Malicious Remote Operator

Runs a remote MCP endpoint that behaves safely during discovery and unsafely during later use.

### 5.4 Internal Misconfiguration

A legitimate team member installs an MCP server with broad permissions, unpinned versions, or leaked credentials.

### 5.5 Adversarial Prompt / Tool Metadata Author

Uses descriptions, setup instructions, or other metadata to manipulate the user or host into unsafe actions.

## 6. Primary Abuse Cases

### 6.1 Malicious Local MCP Package

Attack path:

1. A user installs a package from a registry.
2. The package launches shell commands or scans the workspace.
3. Secrets or source code are exfiltrated.

Required MVP controls:

- install-time scan
- explainable risk score
- sandbox execution profile
- file and network allowlist
- runtime audit events

### 6.2 Trusted Package Turns Malicious

Attack path:

1. A previously safe package releases a new version.
2. Teams upgrade implicitly.
3. The new version changes behavior or introduces malicious code.

Required MVP controls:

- digest pinning
- explicit upgrade review flow
- policy-based version constraints
- rescan on version change

### 6.3 Remote MCP Endpoint Abuse

Attack path:

1. A host connects to a remote MCP endpoint.
2. The endpoint asks for broad auth scopes or uses unsafe redirects.
3. The endpoint abuses the granted token or over-collects data.

Required MVP controls:

- ownership metadata
- remote allow/block policy
- audience and issuer validation
- target domain allowlist
- audit trail of remote usage

### 6.4 Metadata-Driven Social Engineering

Attack path:

1. The server publishes persuasive or deceptive setup instructions.
2. The user manually grants unsafe permissions.
3. The server gains broad access without technical exploit code.

Required MVP controls:

- metadata linting
- high-risk wording heuristics
- explicit policy warnings
- review-required decision class

### 6.5 Sandbox Escape or Scope Expansion

Attack path:

1. A local MCP server runs in an isolated container.
2. The server attempts to write outside its mount scope, spawn extra processes, or reach blocked endpoints.
3. The sandbox configuration is bypassed or too broad.

Required MVP controls:

- read-only root filesystem
- minimal bind mounts
- process count, memory, and CPU limits
- blocked-by-default outbound network
- denied-action audit logs

## 7. Threat Inventory

| ID | Threat | Impact | Likelihood | MVP Priority | Primary Controls |
|---|---|---|---|---|---|
| T1 | Malicious code in local MCP package | High | High | P0 | scanning, sandboxing, audit |
| T2 | Silent version drift to unsafe release | High | High | P0 | pinning, rescan, policy |
| T3 | Remote MCP with unsafe auth or unknown ownership | High | Medium | P0 | remote policy, metadata, auth validation |
| T4 | Over-broad filesystem mounts | High | Medium | P0 | mount allowlist, read-only rootfs |
| T5 | Unrestricted outbound network egress | High | Medium | P0 | egress policy, logs |
| T6 | Misleading setup instructions or tool metadata | Medium | High | P1 | metadata analysis, warnings |
| T7 | Scan false negative | High | Medium | P1 | defense in depth, sandbox, policy overrides |
| T8 | Scan false positive blocks legitimate tool | Medium | Medium | P1 | explainability, override flow |
| T9 | Audit record tampering | Medium | Low | P1 | append-style events, signed policy refs |
| T10 | Sandbox escape via container runtime bug | High | Low | P2 | least privilege, hardened runtime option |

## 8. MVP Security Requirements

The MVP is not complete unless it meets these requirements:

### 8.1 Package and Version Control

- every install decision must resolve to an explicit package version
- production-oriented installs must support digest pinning
- version changes must trigger a fresh scan or stale-result warning

### 8.2 Policy Enforcement

- the CLI must deny installs that violate explicit org policy
- policies must be versioned and identifiable in audit logs
- manual overrides must be visible and attributable

### 8.3 Runtime Isolation

- local MCP servers must run without host networking by default
- allowed mounts must be explicit
- runtime limits must include CPU, memory, process count, and timeout
- the default profile must not mount home directories or SSH keys

### 8.4 Auditability

- every install decision must produce a decision record
- runtime executions must record server identity, version, policy, and outcome
- denied actions must be visible in logs

### 8.5 Explainability

- each risk score must include evidence entries
- each block or restricted decision must explain which rule triggered

## 9. Security Invariants

These invariants should remain true across future refactors:

- untrusted MCP code never runs directly on the host by default
- trust decisions are never based on download count alone
- a policy allow must be more specific than a default deny
- runtime credentials are always narrower than the host's global credential set
- audit events reference immutable server identifiers where possible

## 10. Recommended Test Strategy

The first test corpus should include:

- obviously malicious sample servers
- benign servers with noisy but harmless shell access
- servers that attempt unexpected outbound network calls
- servers that request broad filesystem access
- servers with misleading metadata
- version upgrade scenarios that flip from safe to unsafe

Minimum security test categories:

- analyzer unit tests
- policy evaluation tests
- sandbox enforcement integration tests
- audit emission integration tests

## 11. Open Questions

These questions should be resolved before calling the MVP stable:

- how strict should the default network policy be for common developer tools
- what exact metadata model should identify a remote MCP operator
- when should a scan result expire for mutable remote endpoints
- which runtime should be considered the hardened reference after Docker

## 12. Release Gate

Do not market the project as a security layer until all of the following are true:

- at least one real malicious sample is blocked by install-time analysis
- local stdio servers can be run inside an isolated profile with enforced mount restrictions
- audit records can reconstruct why a server was allowed or denied
- policy overrides are visible and attributable
