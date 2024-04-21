WITH scores_ns(game_id, n, score) AS (
    SELECT game_id, row_number() OVER (PARTITION BY game_id ORDER BY score DESC), score
    FROM scores
    WHERE game_id in (SELECT DISTINCT game_id FROM results WHERE property = 'personalTopThree')
),
res(game_id, property, result) AS (
    SELECT game_id, property, iif(property = 'scores', group_concat(score), max(score))
    FROM scores RIGHT JOIN results USING (game_id)
    WHERE property IN ('scores', 'personalBest')
    GROUP BY game_id, property
    UNION
    SELECT game_id, 'personalTopThree', group_concat(score) FILTER (WHERE n <= 3)
    FROM scores_ns
    GROUP BY game_id
    UNION
    SELECT game_id, 'latest', score FROM scores
    WHERE game_id in (SELECT DISTINCT game_id FROM results WHERE property = 'latest')
    GROUP BY game_id HAVING ROWID = max(ROWID)
)
UPDATE results
SET result = res.result
FROM res
WHERE (results.game_id, results.property) = (res.game_id, res.property);
