"""24/7 system regulator for Claudio.

This module turns existing Claudio technologies into a small control plane:
host_observacionista, ActionGate posture, model routing, Symphony preflight,
and the curador source-retention policy. It is intentionally non-destructive.
It writes evidence and returns lane permissions; it does not kill processes,
move files, delete sources, publish, or start heavy external agents.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "system_regulator"
LATEST_REPORT = RUNTIME / "latest_report.json"
HISTORY_LOG = RUNTIME / "history.jsonl"
SYMPHONY_PREFLIGHT = ROOT / "runtime" / "symphony_claudio" / "latest_preflight.json"
SCHEMA = "claudio.system_regulator.v1"

LANES = {
    "host_observation",
    "security_scan",
    "curador_read_only",
    "agent_evaluation",
    "conway_sync",
    "market_observation",
    "agent_launch",
    "heavy_model",
    "external_action",
    "file_delete",
}


def utc_stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _error_payload(label: str, exc: Exception) -> dict[str, Any]:
    return {"ok": False, "source": label, "error": str(exc)}


def classify_regulation_mode(host_gate: dict[str, Any]) -> str:
    gate = str(host_gate.get("gate") or "").upper()
    status = str(host_gate.get("status") or "").upper()
    if gate == "BLOCK" or status == "JAMMING":
        return "safe_hold"
    if gate == "REVIEW" or status in {"MIXTO", "CONTAMINADO"}:
        return "guarded"
    return "normal"


def lane_policy_for_mode(mode: str) -> dict[str, bool]:
    if mode == "safe_hold":
        return {
            "host_observation": True,
            "security_scan": True,
            "curador_read_only": False,
            "agent_evaluation": True,
            "conway_sync": False,
            "market_observation": False,
            "agent_launch": False,
            "heavy_model": False,
            "external_action": False,
            "file_delete": False,
        }
    if mode == "guarded":
        return {
            "host_observation": True,
            "security_scan": True,
            "curador_read_only": True,
            "agent_evaluation": True,
            "conway_sync": True,
            "market_observation": True,
            "agent_launch": False,
            "heavy_model": False,
            "external_action": False,
            "file_delete": False,
        }
    return {
        "host_observation": True,
        "security_scan": True,
        "curador_read_only": True,
        "agent_evaluation": True,
        "conway_sync": True,
        "market_observation": True,
        "agent_launch": True,
        "heavy_model": False,
        "external_action": False,
        "file_delete": False,
    }


def build_model_policy(mode: str, router_status: dict[str, Any]) -> dict[str, Any]:
    active_model = router_status.get("active_model")
    active_tier = router_status.get("active_tier")
    if mode == "safe_hold":
        qwen_scope = "triage_reset_only"
    else:
        qwen_scope = "observacionista_allowed_if_router_selects"
    return {
        "active_model": active_model,
        "active_tier": active_tier,
        "router_ok": bool(router_status.get("ok", False)),
        "ollama_alive": bool(router_status.get("ollama_alive", False)),
        "available_local_models": router_status.get("available_local_models", []),
        "qwen_observador_scope": qwen_scope,
        "qwen_0_5b_scope": "triage_reset_only",
        "heavy_models": "blocked_by_24_7_regulator",
        "weights_or_lora": "not_touched",
    }


def build_symphony_policy(mode: str, preflight: dict[str, Any]) -> dict[str, Any]:
    ready = bool(preflight.get("ready_to_launch", False))
    blocked_reasons = list(preflight.get("blocked_reasons") or [])
    if not preflight:
        blocked_reasons.append("missing_preflight")
    if mode != "normal":
        blocked_reasons.append(f"host_mode_{mode}")

    launch_allowed = ready and mode == "normal"
    return {
        "ready_to_launch": ready,
        "launch_allowed": launch_allowed,
        "wide_allowed": False,
        "blocked_reasons": sorted(set(blocked_reasons)),
        "preflight_generated_at": preflight.get("generated_at"),
        "permission_profile": preflight.get("permission_profile"),
    }


def build_action_policy(mode: str, host_gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": mode,
        "automatic_process_kill": False,
        "external_actions": False,
        "publish_actions": False,
        "file_delete": False,
        "file_move": False,
        "allowed_without_extra_gate": ["observe", "verify"],
        "requires_action_gate": [
            "file_delete",
            "file_move",
            "public_publish",
            "gumroad_publish",
            "website_deploy",
            "mouse_control",
            "symphony_agent_run",
            "heavy_model_probe",
        ],
        "host_gate": host_gate,
    }


def build_regulation(
    *,
    host_report: dict[str, Any],
    router_status: dict[str, Any],
    symphony_preflight: dict[str, Any],
    source_retention: dict[str, Any],
    generated_at: str | None = None,
) -> dict[str, Any]:
    host_gate = host_report.get("gate") or {}
    mode = classify_regulation_mode(host_gate)
    lane_policy = lane_policy_for_mode(mode)
    model_policy = build_model_policy(mode, router_status)
    symphony_policy = build_symphony_policy(mode, symphony_preflight)
    action_policy = build_action_policy(mode, host_gate)

    return {
        "schema": SCHEMA,
        "ok": True,
        "generated_at": generated_at or utc_stamp(),
        "mode": mode,
        "host": {
            "gate": host_gate,
            "metrics": host_report.get("metrics") or {},
            "process_action_plan": host_report.get("process_action_plan") or [],
            "destructive_actions": False,
        },
        "lane_policy": lane_policy,
        "model_policy": model_policy,
        "symphony_policy": symphony_policy,
        "action_policy": action_policy,
        "source_retention": source_retention,
        "integrated_technologies": [
            "host_observacionista",
            "observacion_action_gate_policy",
            "model_router_qwen_observador",
            "symphony_preflight_gate",
            "curador_source_retention",
            "daemon_247_lane_policy",
        ],
        "notes": [
            "No destructive host actions are executed by this regulator.",
            "Host REVIEW/BLOCK throttles agent launches and heavy models.",
            "Source deletion remains gated by complete ficha and DELETE_APPROVED_AFTER_HASH.",
        ],
    }


def _collect_host_report(root: Path) -> dict[str, Any]:
    try:
        from tools.host_observacionista import observe_host

        return observe_host(root, write=True)
    except Exception as exc:
        return _error_payload("host_observacionista", exc)


def _collect_router_status() -> dict[str, Any]:
    try:
        from core.model_router import router_status

        return router_status("qwen_observador")
    except Exception as exc:
        return _error_payload("model_router", exc)


def _collect_source_retention() -> dict[str, Any]:
    try:
        from limpieza.daily_cleanup import SOURCE_RETENTION_POLICY

        return dict(SOURCE_RETENTION_POLICY)
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "delete_requires_gate_state": "DELETE_APPROVED_AFTER_HASH",
            "daemon_auto_delete_unique_sources": False,
        }


def write_report(report: dict[str, Any]) -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    LATEST_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    with HISTORY_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(report, ensure_ascii=False, sort_keys=True) + "\n")


def collect_regulation(
    *,
    root: Path | str | None = None,
    write: bool = True,
    host_report: dict[str, Any] | None = None,
    router_status_payload: dict[str, Any] | None = None,
    symphony_preflight: dict[str, Any] | None = None,
    source_retention: dict[str, Any] | None = None,
) -> dict[str, Any]:
    claudio_root = Path(root).resolve() if root else ROOT
    host_payload = host_report if host_report is not None else _collect_host_report(claudio_root)
    router_payload = router_status_payload if router_status_payload is not None else _collect_router_status()
    symphony_payload = symphony_preflight if symphony_preflight is not None else _read_json(SYMPHONY_PREFLIGHT)
    retention_payload = source_retention if source_retention is not None else _collect_source_retention()
    report = build_regulation(
        host_report=host_payload,
        router_status=router_payload,
        symphony_preflight=symphony_payload,
        source_retention=retention_payload,
    )
    if write:
        write_report(report)
    return report


def lane_allowed(report: dict[str, Any], lane: str) -> bool:
    policy = report.get("lane_policy") or {}
    return bool(policy.get(lane, False))


def main() -> int:
    report = collect_regulation(write=True)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
