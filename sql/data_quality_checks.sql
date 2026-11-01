-- Find rows that will break a load because a text column holds an invalid date.
-- Seen in production: materialisation failed on a conversion error coming from
-- free-text values in a source date column.

SELECT TOP 100 *
FROM dbo.Aggregations_2025
WHERE TRY_CONVERT(date, OrderDate) IS NULL
  AND OrderDate IS NOT NULL;

-- Row counts per year table, to catch a silent empty load.
SELECT '2024' AS yr, COUNT(*) AS n FROM dbo.Aggregations_2024
UNION ALL SELECT '2025', COUNT(*) FROM dbo.Aggregations_2025
UNION ALL SELECT '2026', COUNT(*) FROM dbo.Aggregations_2026;

-- View vs materialised table must match after each run.
SELECT
    (SELECT COUNT(*) FROM dbo.vw_UnitA_Forecasts) AS view_rows,
    (SELECT COUNT(*) FROM dbo.tb_UnitA_Forecasts) AS table_rows;
