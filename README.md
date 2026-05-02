# Claudio System Regulator

Public-safe extraction of the Claudio 24/7 system regulator.

The regulator converts host state, model-router state, Symphony preflight state,
and source-retention policy into a small evidence-backed lane policy. It is
intentionally non-destructive: it writes JSON evidence and returns permissions;
it does not kill processes, delete files, move files, publish, deploy, or start
heavy model runs by itself.

## Why It Exists

Local AI workstations fail in boring ways before they fail dramatically: disk
pressure, too many processes, stale preflights, heavy model routes, and agents
trying to publish while the machine is not ready. This regulator makes those
conditions explicit and turns them into lane permissions.

## Problems It Helps With

- PC overload during agent work: host pressure is measured before heavy lanes.
- Unsafe publication: external actions default to blocked until gates pass.
- Memory/source cleanup risk: source deletion stays behind a complete technical
  ficha and explicit retention policy.
- Runtime drift: latest report plus append-only history gives the next session
  evidence instead of guesses.

## What It Does

- Classifies runtime mode as `normal`, `guarded`, or `safe_hold`.
- Blocks heavy model lanes by default.
- Blocks external actions and publishing by default.
- Keeps source deletion behind a complete technical ficha and an explicit gate.
- Writes `runtime/system_regulator/latest_report.json` plus append-only history.

## Install

```powershell
python -m pip install -e .
```

## Test

```powershell
python -m pytest -q
```

## Run

```powershell
python -m claudio_system_regulator.system_regulator
```

## Public Boundary

This repository does not include the private Claudio runtime, MEDIOEVO canon,
game/TCG assets, Gumroad credentials, local sessions, browser automation, or
commercial product bundles. It is a reusable regulator kernel and evidence
contract for agentic systems.

## Commercial Companion

The companion product `Claudio OS / Brain OS v1` is live on Gumroad:
`https://lrgonzalez.gumroad.com/l/oklvqt`.

