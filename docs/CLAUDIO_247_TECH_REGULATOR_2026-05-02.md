# Claudio 24/7 Technology Regulator - 2026-05-02

## Decision

La tecnologia existente queda integrada al daemon 24/7 como regulador no destructivo.

El objetivo no es que el 24/7 haga mas cosas a ciegas. El objetivo es que mida la PC, lea los gates, limite acciones pesadas cuando el host esta cargado y deje evidencia para mejorar el framework.

## Integrado al 24/7

Archivo nuevo:

- `core/system_regulator.py`

Daemon actualizado:

- `claudio_daemon_247.py`
- hilo nuevo: `Regulador`
- intervalo: `INTERVAL_REGULADOR = 300`

API nueva:

- `GET /api/daemon/247/regulator`

Evidencia runtime:

- `runtime/system_regulator/latest_report.json`
- `runtime/system_regulator/history.jsonl`

## Tecnologias conectadas

- `host_observacionista`: mide CPU, memoria, disco, procesos y gate `APPROVE/REVIEW/BLOCK`.
- `observacion_action_gate`: queda como politica para acciones externas, borrado, movimientos, publicacion, mouse y modelos pesados.
- `model_router`: expone la ruta activa; en esta PC el regulador observa `qwen2.5-coder:3b` como modelo activo local.
- `symphony_preflight`: mantiene Symphony bloqueado si `ready_to_launch=false` o si el host no esta en modo normal.
- `curador_source_retention`: conserva la regla `DELETE_APPROVED_AFTER_HASH` para fuentes.
- `daemon_247_lane_policy`: convierte todo lo anterior en permisos por carril.

## Politica de carriles

Modo `normal`:

- permite seguridad, host observation, curador, evaluacion, sincronizacion y observacion de mercado;
- permite `agent_launch` solo si el host esta sano;
- mantiene `heavy_model=false`, `external_action=false`, `file_delete=false` por defecto.

Modo `guarded`:

- permite seguridad, host observation, curador, evaluacion y sincronizacion;
- bloquea `agent_launch`;
- bloquea `heavy_model`;
- bloquea acciones externas y borrado.

Modo `safe_hold`:

- conserva solo seguridad, host observation y evaluacion minima;
- pausa curador, sincronizacion no esencial, mercado, lanzamientos y modelos pesados.

## Estado vivo verificado

Comando de verificacion:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:47047/api/daemon/247/regulator'
```

Resultado observado:

- daemon 24/7: `running=true`
- threads: `7`
- PSI: `running=true`
- regulator: `ok=true`
- mode: `guarded`
- host: `MIXTO/REVIEW`
- `agent_launch=false`
- `heavy_model=false`
- active model: `qwen2.5-coder:3b`
- Symphony launch: `false`
- agentes visibles: `5`

## Pruebas

```powershell
python -m pytest tests\test_system_regulator.py tests\test_claudio_daemon_247.py tests\test_limpieza_curador.py tests\test_host_observacionista.py tests\test_qwen_observacion_gate_report.py tests\test_qwen_observacion_benchmark_suite.py -q
```

Resultado:

```txt
29 passed in 0.67s
```

Prueba de integración Mission Control:

```powershell
python -m pytest tests\test_hormiguero_mission_control_api.py tests\test_system_regulator.py tests\test_claudio_daemon_247.py -q
```

Resultado:

```txt
28 passed in 2.80s
```

## Superficie UI

Mission Control ya expone una lectura humana del regulador:

- ruta UI: `http://127.0.0.1:5050/#regulator-section`
- proxy local: `GET /api/regulator/status`
- puertos verificados: `5050` y `5051`
- sección visible: `Regulador 24/7`
- semáforo visible: host, modelo activo, Symphony, política de fuentes y carriles

Resultado vivo observado después de reiniciar solo Mission Control:

- mode: `guarded`
- host: `CONTAMINADO/REVIEW`
- active model: `qwen2.5-coder:3b`
- `agent_launch=false`
- `heavy_model=false`
- Symphony launch: `false`
- HTML servido contiene `Regulador 24/7`, `/regulator/status` y `regulator-lane-grid`

## Fronteras

- No mata procesos automaticamente.
- No borra fuentes.
- No mueve archivos.
- No publica.
- No arranca Symphony.
- No usa modelos pesados.
- No toca pesos, LoRA ni fine-tuning.

## Siguiente mejora

El siguiente paso tecnico es conectar el panel de accesos del Escritorio con esta misma lectura para que los botones muestren por que una app esta permitida, pausada o bloqueada antes de intentar abrirla.
