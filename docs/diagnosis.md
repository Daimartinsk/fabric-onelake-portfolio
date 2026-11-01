# Diagnosing capacity throttling

## Symptoms reported
- Dashboards slow or timing out during working hours
- Dataflow refreshes failing intermittently, even with the gateway online and credentials valid
- Capacity alerts for overages

## Method

1. **Fabric Capacity Metrics app** → *Compute* page
   - Utilisation chart: peaks reached **~365%** of the SKU
   - Throttling tab: interactive delay and rejection were being applied
2. **Items by CU** (matrix sorted by CU seconds, split by item kind)
   - Separate *interactive* operations (report queries) from *background* operations (dataflows, notebooks, refreshes)
   - The heaviest consumers were the DirectQuery semantic model (interactive) and the monolithic dataflow (background)
3. **Rule out connectivity before blaming capacity** — for the failing refresh:
   - Gateway status: online ✓
   - Data source credentials: valid ✓
   - Same query from Power BI Desktop through the same gateway: works ✓
   - ⇒ failure isolated to execution inside the Fabric service at a time of throttling, not the connection
4. **Read the model and storage design** to explain *why* consumption was high.

## Root causes

| # | Cause | Why it burns CUs |
|---|---|---|
| 1 | Semantic model in DirectQuery | Every visual on every report open generates SQL against the Lakehouse |
| 2 | Business logic in views, never materialised | Joins, working-day calculations and KPIs recomputed for every query |
| 3 | One dataflow for all sources and years | History re-ingested daily; extract and transform coupled; any failure fails everything |
| 4 | No Delta maintenance | Many small files → more files scanned per query |
| 5 | No star schema, N:N relationships | Expensive query plans, harder to maintain |

## What I'd check first on any new Fabric engagement

- [ ] Capacity Metrics: interactive vs background split, top 10 items by CU
- [ ] Storage mode of each semantic model (DirectQuery / Import / Direct Lake)
- [ ] Views read directly by models?
- [ ] Refresh schedules overlapping in the same window?
- [ ] Last `OPTIMIZE` per Delta table / file counts
- [ ] Gateway: single point of failure? cluster? monitored?
