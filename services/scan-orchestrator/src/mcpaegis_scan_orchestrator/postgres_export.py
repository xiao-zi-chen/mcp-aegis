from __future__ import annotations

import json


def build_sql(document: dict) -> str:
    server = document["server"]
    risk = document["riskScore"]
    policy = document["policyDecision"]
    recommended_actions = document["recommendedActions"]
    scan_report = document["scanReport"]

    statements = [
        "BEGIN;",
        (
            "INSERT INTO policy_evaluations "
            "(server_name, server_version, bundle_name, bundle_version, decision, runtime_profile, remote_access, require_digest_pin, matched_rules, reasons, recommended_actions, evaluated_at) "
            f"VALUES ({sql_string(server['name'])}, {sql_string(server.get('version', ''))}, {sql_string(policy['bundle'])}, {policy['bundleVersion']}, "
            f"{sql_string(policy['decision'])}, {sql_string(policy['runtimeProfile'])}, {sql_string(policy['remoteAccess'])}, "
            f"{sql_bool(policy['requireDigestPin'])}, {sql_json(policy['matchedRules'])}, {sql_json(policy['reasons'])}, {sql_json(recommended_actions)}, "
            f"{sql_string(document['generatedAt'])}::timestamptz);"
        ),
        (
            "INSERT INTO audit_events "
            "(event_type, server_name, server_version, policy_bundle_name, policy_bundle_version, decision, event_data, created_at) "
            f"VALUES ('scan-evaluated', {sql_string(server['name'])}, {sql_string(server.get('version', ''))}, {sql_string(policy['bundle'])}, {policy['bundleVersion']}, "
            f"{sql_string(policy['decision'])}, {sql_json({'riskScore': risk, 'scanReport': scan_report})}, {sql_string(document['generatedAt'])}::timestamptz);"
        ),
        (
            "INSERT INTO audit_events "
            "(event_type, server_name, server_version, policy_bundle_name, policy_bundle_version, decision, event_data, created_at) "
            f"VALUES ('scan-findings-snapshot', {sql_string(server['name'])}, {sql_string(server.get('version', ''))}, {sql_string(policy['bundle'])}, {policy['bundleVersion']}, "
            f"{sql_string(policy['decision'])}, {sql_json({'findings': scan_report['findings']})}, {sql_string(document['generatedAt'])}::timestamptz);"
        ),
    ]

    statements.append("COMMIT;")
    return "\n".join(statements) + "\n"


def sql_string(value: str) -> str:
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def sql_json(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False).replace("'", "''")
    return f"'{payload}'::jsonb"


def sql_bool(value: bool) -> str:
    return "TRUE" if value else "FALSE"
