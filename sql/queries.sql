-- Q1: extreme days per decade
WITH thr AS (
    SELECT STATION, quantile_cont(PRCP, 0.95) AS thr 
    FROM 'data/processed/ghcn_tx.parquet'
    WHERE month(DATE) BETWEEN 6 AND 8 AND year(DATE) BETWEEN 1991 AND 2020 
    GROUP BY 1
),
yearly_cnt AS (
    SELECT g.STATION, year(g.DATE) AS yr, SUM(g.PRCP > thr) AS cnt 
    FROM 'data/processed/ghcn_tx.parquet' g 
    JOIN thr ON g.STATION = thr.STATION 
    GROUP BY 1, 2
)
SELECT (yr / 10) * 10 AS decade, AVG(cnt) AS extreme_days_per_year 
FROM yearly_cnt 
GROUP BY 1 
ORDER BY 1;

-- Q2: fastest-warming stations
WITH thr AS (
    SELECT STATION, quantile_cont(PRCP, 0.95) AS thr 
    FROM 'data/processed/ghcn_tx.parquet'
    WHERE month(DATE) BETWEEN 6 AND 8 AND year(DATE) BETWEEN 1991 AND 2020 
    GROUP BY 1
),
yearly_cnt AS (
    SELECT g.STATION, year(g.DATE) AS yr, SUM(g.PRCP > thr) AS cnt 
    FROM 'data/processed/ghcn_tx.parquet' g 
    JOIN thr ON g.STATION = thr.STATION 
    GROUP BY 1, 2
)
SELECT STATION, regr_slope(cnt, yr) AS slope 
FROM yearly_cnt 
GROUP BY 1 
ORDER BY slope DESC 
LIMIT 10;
