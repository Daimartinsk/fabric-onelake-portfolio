# Improvement roadmap

Ordered by effort vs. impact so the client gets relief first and structural fixes after.

## Phase 1 — Quick wins
- Delta maintenance routine (`OPTIMIZE` + `VACUUM`) → [`notebooks/delta_maintenance.py`](../notebooks/delta_maintenance.py)
- Semantic models: DirectQuery → Import with scheduled refresh

**Goal:** get the capacity out of throttling without restructuring anything.

## Phase 2 — Structural
- Materialise priority views into Delta tables → [`notebooks/materialize_views.py`](../notebooks/materialize_views.py)
- Separate raw ingestion from transformation
- Split the ingestion dataflow by source and refresh frequency
- One orchestrating Data Pipeline → [`pipelines/orchestrator.md`](../pipelines/orchestrator.md)

**Goal:** fix the cause, not the symptom.

## Phase 3 — Model
- Rebuild the semantic model as a **star schema** (facts + dimensions, bridge tables for N:N)
- Evaluate **Direct Lake** on top of the `tb_` tables once the model is clean
- Evaluate notebook-based ingestion from the internal API (requires VNet Data Gateway → [`gateway/vnet-gateway-design.md`](../gateway/vnet-gateway-design.md))

**Goal:** a model that is fast, cheap and maintainable long-term.

## Status in this engagement

| Item | Status |
|---|---|
| DirectQuery → Import + scheduled refresh | ✅ Done |
| Dataflow split (current / forecasts / history) | ✅ Done |
| View materialisation notebook | ✅ Done |
| Models repointed to `tb_` tables | ✅ Done |
| Orchestrating pipeline | ✅ Built |
| Delta maintenance notebook | ✅ Designed, chained in pipeline |
| VNet Data Gateway | ⏸ Designed, deferred by decision |
| Star schema | 🔜 Next |

<!-- TODO: adjust statuses to match exactly what is live today -->
