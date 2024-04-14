UPDATE darts
SET score = CASE
                WHEN dist > 100 THEN 0
                WHEN dist > 25 THEN 1
                WHEN dist > 1 THEN 5
                ELSE 10
            END
FROM (SELECT x, y, (x * x + y * y) AS dist FROM darts) as dists
WHERE darts.x = dists.x AND darts.y = dists.y;
