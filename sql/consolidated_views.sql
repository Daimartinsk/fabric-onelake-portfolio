-- Lakehouse SQL analytics endpoint (T-SQL).
-- Raw data lands as one Delta table per year. A consolidated view unions them,
-- so adding a new year is one new table + one line here, and past years are
-- never rewritten by the daily load.

CREATE OR ALTER VIEW dbo.vw_Aggregations_Consolidated AS
SELECT * FROM dbo.Aggregations_2023
UNION ALL
SELECT * FROM dbo.Aggregations_2024
UNION ALL
SELECT * FROM dbo.Aggregations_2025
UNION ALL
SELECT * FROM dbo.Aggregations_2026;
GO

-- Pattern for a business view with working-day logic against a calendar table.
CREATE OR ALTER VIEW dbo.vw_UnitA_WorkingDays AS
SELECT
    p.ProcessId,
    p.StartDate,
    p.EndDate,
    COUNT(c.[Date]) AS WorkingDays
FROM dbo.vw_UnitA AS p
JOIN dbo.Calendar AS c
  ON c.[Date] BETWEEN p.StartDate AND p.EndDate
 AND c.IsWorkingDay = 1
GROUP BY p.ProcessId, p.StartDate, p.EndDate;
GO

-- Semantic models read the materialised table, not the view:
--   Power Query:  Source{[Schema="dbo", Item="tb_UnitA_Forecasts"]}[Data]
--   (was:         Source{[Schema="dbo", Item="vw_UnitA_Forecasts"]}[Data])
