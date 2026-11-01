# On-prem gateway vs VNet gateway — decision record

**Status:** VNet gateway designed, **deferred**.

## Context
- The internal API is only reachable from the private network; today it reaches Fabric through an on-premises data gateway on a single physical server.
- A power outage at the data centre took that server down; after power returned the gateway stayed offline until restarted, and every API-sourced dashboard went stale.
- The consultancy's target architecture pointed toward Spark notebooks for ingestion.

## Options

| | On-prem gateway (keep) | VNet Data Gateway |
|---|---|---|
| Works with Dataflows Gen2 | ✅ | ✅ |
| Works with Spark notebooks to private IPs | ❌ | ✅ |
| Hardware / patching | Ours | Microsoft |
| Single point of failure | Yes (unless clustered) | No |
| Needs Azure networking from IT | No | Yes (VNet, subnet, RBAC, NSG) |
| Lead time | None | Depends on IT |

## Decision
After re-reading the target ("to-be") design, the current phase orchestrates the **existing Dataflows Gen2 through a Data Pipeline** — it does not require notebooks to call the private API. So:

1. Keep the on-prem gateway for now, with the outage runbook and monitoring in place.
2. Keep the VNet design ready (see [`vnet-gateway-design.md`](vnet-gateway-design.md)) for the phase where ingestion moves to notebooks.

## Why this matters
Recommending the bigger architectural change was tempting. Matching the solution to what the current phase needs saved IT effort and avoided a blocking dependency, without closing the door on the later migration.
