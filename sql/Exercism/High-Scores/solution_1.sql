CREATE TABLE base (game_id TEXT, property TEXT, score INT);
INSERT INTO base
    SELECT game_id, property, score FROM scores RIGHT JOIN results USING (game_id);
WITH scores_ns(game_id, n, score) AS (
    SELECT game_id, row_number() OVER (PARTITION BY game_id ORDER BY score DESC), score
    FROM base WHERE property = 'personalTopThree'
),
res(game_id, property, result) AS (
    SELECT game_id, property,
           CASE property
                WHEN 'scores' THEN group_concat(score)
                WHEN 'personalBest' THEN max(score)
                ELSE score
            END
    FROM base WHERE property IN ('scores', 'personalBest', 'latest')
    GROUP BY game_id HAVING ROWID = max(ROWID)
    UNION
    SELECT game_id, 'personalTopThree', group_concat(score) FILTER (WHERE n <= 3)
    FROM scores_ns
    GROUP BY game_id
)
UPDATE results
SET result = res.result
FROM res
WHERE (results.game_id, results.property) = (res.game_id, res.property);
DROP TABLE base;
