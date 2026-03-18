from __future__ import annotations

import argparse
import json
from pathlib import Path

from mcpaegis_analyzers.scanner import scan_path
from mcpaegis_analyzers.scoring import score_findings
from mcpaegis_policy.evaluator import evaluate_policy
from mcpaegis_policy.loader import load_policy_bundle

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
    parser.add_argument("--transport", action="append", default=[], help="Transport values such as stdio or streamable-http.")
    parser.add_argument("--ownership-verified", action="store_true", help="Whether the publisher or operator ownership is verified.")
    parser.add_argument("--remote-url", default="", help="Remote MCP URL if applicable.")
    parser.add_argument("--output", default="", help="Optional JSON report output path.")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    report = scan_path(args.target)
    score = score_findings(report.findings)
    bundle = load_policy_bundle(args.policy, _resolve_repo_path(args.schema))
    context = {
        "server": {"name": args.server_name},
        "transport": args.transport,
        "risk": {"score": score["score"], "class": score["decisionClass"]},
        "ownership": {"verified": args.ownership_verified},
        "remote": {"url": args.remote_url},
    }
    decision = evaluate_policy(bundle, context)
    recommendations = build_recommendations(report.findings, decision)

    document = {
        "scanReport": report.to_dict(),
        "riskScore": score,
        "policyDecision": decision.to_dict(),
        "recommendedActions": recommendations,
    }

    payload = json.dumps(document, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
    else:
        print(payload)


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


if __name__ == "__main__":
    main()
