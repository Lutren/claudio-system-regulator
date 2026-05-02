from claudio_system_regulator import system_regulator


def test_build_regulation_guarded_blocks_heavy_and_launch_lanes():
    report = system_regulator.build_regulation(
        host_report={
            "gate": {
                "status": "MIXTO",
                "gate": "REVIEW",
                "R": 0.5,
                "Phi_eff": 0.5,
                "lambda_sat": 0.84,
                "reasons": ["residuo_precaucion"],
            },
            "metrics": {"memory_pct": 74.0},
        },
        router_status={"ok": True, "active_model": "qwen2.5-coder:3b", "active_tier": "local", "ollama_alive": True},
        symphony_preflight={"ready_to_launch": False, "blocked_reasons": ["missing_linear_or_repo_environment"]},
        source_retention={"delete_requires_gate_state": "DELETE_APPROVED_AFTER_HASH"},
        generated_at="2026-05-02T00:00:00Z",
    )

    assert report["mode"] == "guarded"
    assert report["lane_policy"]["security_scan"] is True
    assert report["lane_policy"]["agent_launch"] is False
    assert report["lane_policy"]["heavy_model"] is False
    assert report["model_policy"]["heavy_models"] == "blocked_by_24_7_regulator"
    assert report["symphony_policy"]["launch_allowed"] is False


def test_collect_regulation_writes_runtime_report(tmp_path, monkeypatch):
    runtime = tmp_path / "runtime"
    monkeypatch.setattr(system_regulator, "RUNTIME", runtime)
    monkeypatch.setattr(system_regulator, "LATEST_REPORT", runtime / "latest_report.json")
    monkeypatch.setattr(system_regulator, "HISTORY_LOG", runtime / "history.jsonl")
    monkeypatch.setattr(system_regulator, "SYMPHONY_PREFLIGHT", tmp_path / "missing.json")

    report = system_regulator.collect_regulation(
        root=tmp_path,
        write=True,
        host_report={
            "gate": {"status": "LIMPIO", "gate": "APPROVE", "R": 0.2},
            "metrics": {"cpu_pct": 10.0},
            "process_action_plan": [],
        },
        router_status_payload={
            "ok": True,
            "active_model": "qwen2.5-coder:3b",
            "active_tier": "local",
            "ollama_alive": True,
            "available_local_models": ["qwen2.5-coder:3b"],
        },
        source_retention={"daemon_auto_delete_unique_sources": False},
    )

    assert report["mode"] == "normal"
    assert report["lane_policy"]["agent_launch"] is True
    assert report["action_policy"]["automatic_process_kill"] is False
    assert (runtime / "latest_report.json").exists()
    assert (runtime / "history.jsonl").read_text(encoding="utf-8").strip()

