from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from mcpaegis_analyzers.scanner import scan_path
from mcpaegis_analyzers.scoring import score_findings
from mcpaegis_policy.evaluator import evaluate_policy
from mcpaegis_policy.loader import load_policy_bundle
from mcpaegis_policy.planner import build_runtime_plan

try:
    from mcpaegis_scan_orchestrator.launcher import build_launch_audit_event, build_sandbox_spec
except ModuleNotFoundError:
    from launcher import build_launch_audit_event, build_sandbox_spec

try:
    from mcpaegis_scan_orchestrator.recommendations import build_recommendations
except ModuleNotFoundError:
    from recommendations import build_recommendations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run MCP Aegis detection and policy evaluation.")
    parser.add_argument("--target", required=True, help="Path to the MCP server code or package directory.")
    parser.add_argument(
        "--policy",
        required=True,
        help="Path to the policy bundle YAML file.",
    )
    parser.add_argument(
        "--schema",
        default="packages/policy-spec/schema.json",
        help="Path to the policy schema JSON file.",
    )
    parser.add_argument("--server-name", default="", help="Canonical server name for audit output.")
    parser.add_argument("--server-version", default="", help="Server version associated with the scan target.")
    parser.add_argument("--registry", default="manual", help="Registry or source label for the scanned target.")
    parser.add_argument("--transport", action="append", default=[], help="Transport values such as stdio or streamable-http.")
    parser.add_argument("--ownership-verified", action="store_true", help="Whether the publisher or operator ownership is verified.")
    parser.add_argument("--remote-url", default="", help="Remote MCP URL if applicable.")
    parser.add_argument("--container-image", default="", help="Optional container image override for sandbox planning.")
    parser.add_argument("--run-command", action="append", default=[], help="Optional explicit command for sandbox planning. Repeat for multiple args.")
    parser.add_argument("--output", default="", help="Optional JSON report output path.")
    parser.add_argument("--sql-output", default="", help="Optional PostgreSQL import SQL output path.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    generated_at = datetime.now(timezone.utc).isoformat()

    report = scan_path(args.target)
    score = score_findings(report.findings)
    bundle = load_policy_bundle(_resolve_repo_path(args.policy), _resolve_repo_path(args.schema))
    context = {
        "server": {"name": args.server_name},
        "transport": args.transport,
        "risk": {"score": score["score"], "class": score["decisionClass"]},
        "ownership": {"verified": args.ownership_verified},
        "remote": {"url": args.remote_url},
    }
    decision = evaluate_policy(bundle, context)
    recommendations = build_recommendations(report.findings, decision)
    runtime_plan = build_runtime_plan(
        bundle,
        decision,
        [finding.to_dict() for finding in report.findings],
        {
            "name": args.server_name or _default_server_name(args.target),
            "transport": args.transport,
            "remoteUrl": args.remote_url,
        },
    )
    sandbox_spec = build_sandbox_spec(
        runtime_plan,
        {
            "name": args.server_name or _default_server_name(args.target),
            "version": args.server_version,
        },
        target_path=args.target,
        image=args.container_image or None,
        command=args.run_command or None,
    )
    launch_audit_event = build_launch_audit_event(
        {
            "name": args.server_name or _default_server_name(args.target),
            "version": args.server_version,
        },
        decision.to_dict(),
        runtime_plan,
        sandbox_spec,
        generated_at,
    )

    document = {
        "reportVersion": "v1alpha1",
        "generatedAt": generated_at,
        "scannerName": "mcpaegis-static",
        "scannerVersion": "0.1.0",
        "server": {
            "name": args.server_name or _default_server_name(args.target),
            "version": args.server_version,
            "registry": args.registry,
            "targetPath": str(Path(args.target)),
            "transport": args.transport,
            "ownershipVerified": args.ownership_verified,
            "remoteUrl": args.remote_url,
        },
        "scanReport": report.to_dict(),
        "riskScore": score,
        "policyDecision": decision.to_dict(),
        "runtimePlan": runtime_plan,
        "sandboxSpec": sandbox_spec,
        "launchAuditEvent": launch_audit_event,
        "recommendedActions": recommendations,
    }

    payload = json.dumps(document, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
    else:
        print(payload)

    if args.sql_output:
        try:
            from mcpaegis_scan_orchestrator.postgres_export import build_sql
        except ModuleNotFoundError:
            from postgres_export import build_sql

        sql_output_path = Path(args.sql_output)
        sql_output_path.parent.mkdir(parents=True, exist_ok=True)
        sql_output_path.write_text(build_sql(document), encoding="utf-8")


def _resolve_repo_path(path: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute() and candidate.exists():
        return str(candidate)
    if candidate.exists():
        return str(candidate)

    current = Path.cwd()
    for base in [current, *current.parents]:
        resolved = base / path
        if resolved.exists():
            return str(resolved)

    return path


def _default_server_name(target: str) -> str:
    return Path(target).stem.replace("_", "-")


if __name__ == "__main__":
    main()
