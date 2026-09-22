
-- Step 3: sql/queries.sql
CREATE OR REPLACE TABLE g AS SELECT * FROM 'data/processed/ghcn_tx.parquet';

-- Q1: per-station extreme threshold (95th percentile of summer TMAX, 1991-2020) and extreme days per decade
CREATE OR REPLACE TABLE thr AS
SELECT STATION, quantile_cont(TMAX, 0.95) AS thr FROM g
WHERE month(DATE) BETWEEN 6 AND 8 AND year(DATE) BETWEEN 1991 AND 2020 GROUP BY 1;

SELECT (yr / 10) * 10 AS decade, AVG(cnt) AS extreme_days_per_year FROM (
  SELECT g.STATION, year(g.DATE) AS yr, SUM(g.TMAX > thr.thr) AS cnt 
  FROM g JOIN thr ON g.STATION = thr.STATION GROUP BY g.STATION, year(g.DATE))
GROUP BY 1 ORDER BY 1;

-- Q2: fastest-warming stations (slope of extreme days per year)
SELECT STATION, regr_slope(cnt, yr) AS slope FROM (
  SELECT g.STATION, year(g.DATE) AS yr, SUM(g.TMAX > thr.thr) AS cnt 
  FROM g JOIN thr ON g.STATION = thr.STATION GROUP BY g.STATION, year(g.DATE))
GROUP BY 1 ORDER BY slope DESC LIMIT 10;

-- Q3: features and targets 1-3 days ahead (2020-2024 only for modelling)
CREATE OR REPLACE TABLE feat AS
SELECT g.STATION, g.DATE, g.TMAX, g.TMIN, g.PRCP, thr.thr, dayofyear(g.DATE) AS doy,
       LAG(g.TMAX, 1) OVER w AS tmax_lag1, LAG(g.TMAX, 2) OVER w AS tmax_lag2, LAG(g.TMAX, 7) OVER w AS tmax_lag7,
       LAG(g.TMIN, 1) OVER w AS tmin_lag1, AVG(g.TMAX) OVER (w ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS tmax_ma7,
       LEAD(g.TMAX, 1) OVER w AS y_1d, LEAD(g.TMAX, 2) OVER w AS y_2d, LEAD(g.TMAX, 3) OVER w AS y_3d
FROM g JOIN thr ON g.STATION = thr.STATION WHERE year(g.DATE) >= 2020 WINDOW w AS (PARTITION BY g.STATION ORDER BY g.DATE);
