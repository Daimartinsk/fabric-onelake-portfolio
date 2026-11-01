# Runbook — gateway / source outage

Built from a real incident: power cut at the data centre hosting the source system and the gateway server.

## Symptoms
- Dataflows Gen2 fail with credential/connection errors on `WriteToDataDestination` steps, cascading across all API-sourced tables
- Dashboards show stale data; SharePoint-sourced tables are unaffected (useful signal: the problem is on the private-network side)

## Triage (in order)

1. **Is the source up?** Open the API/back-office from inside the network. If down → source incident, not Fabric.
2. **Is the gateway online?** Fabric → *Manage connections and gateways* → gateway status. After a power cut it may need a service restart on the host.
3. **Are connection credentials valid?** Edit the connection, re-enter, test.
4. **Does the same query work in Power BI Desktop through the gateway?**
   - Yes → the connection is fine; the failure is in the Fabric run. Check the Capacity Metrics app for throttling at that time.
   - No → network/gateway side.
5. **Re-run** ingestion via the pipeline (not each dataflow by hand), so maintenance and materialisation run after it.

## Communication to IT (template)
- What's down, since when (timestamp)
- Exact error message and failing item names
- What's been ruled out (gateway status, credentials, desktop test)
- Business impact (which dashboards/entities)
- What you need from them

## Prevention
- Gateway monitoring (gateway performance template / Azure Monitor)
- Gateway cluster on a second host, or VNet Data Gateway (see [`gateway-decision.md`](gateway-decision.md))
- Pipeline failure alerts so stale data is noticed before users report it
