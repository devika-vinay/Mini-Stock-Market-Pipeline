-- 1) Latest metrics for each ticker
SELECT p.* FROM prices p
JOIN (
  SELECT ticker, MAX(date) AS max_date FROM prices GROUP BY ticker
) m ON p.ticker = m.ticker AND p.date = m.max_date;

-- 2) 3-month summary stats
SELECT ticker,
       AVG(daily_return) AS avg_daily_return,
       STDDEV(daily_return) AS std_daily_return
FROM prices
WHERE date >= date('now','-90 day')
GROUP BY ticker;

-- 3) Cross-ticker comparison on most recent day
WITH last AS (
  SELECT ticker, MAX(date) AS d FROM prices GROUP BY ticker
)
SELECT p.ticker, p.date, p.adj_close, p.ma_20, p.ma_50, p.vol_20
FROM prices p
JOIN last l ON p.ticker=l.ticker AND p.date=l.d
ORDER BY p.vol_20 DESC;
