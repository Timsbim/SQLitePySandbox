WITH part_1(game_id, property, result) AS (
    SELECT game_id, property, iif(property = 'scores', group_concat(score), max(score))
    FROM scores RIGHT JOIN results USING (game_id)
    WHERE property IN ('scores', 'personalBest')
    GROUP BY game_id, property
),
scores_ns(game_id, n, score) AS (
    SELECT game_id, row_number() OVER (PARTITION BY game_id ORDER BY score DESC), score
    FROM scores
    WHERE game_id in (SELECT DISTINCT game_id FROM results WHERE property = 'personalTopThree')
),
part_2(game_id, property, result) AS (
    SELECT game_id, 'personalTopThree', group_concat(score) FILTER (WHERE n <= 3)
    FROM scores_ns
    GROUP BY game_id
    UNION SELECT * FROM part_1
),
parts(game_id, property, result) AS (
    SELECT game_id, 'latest', score FROM scores
    WHERE game_id in (SELECT DISTINCT game_id FROM results WHERE property = 'latest')
    GROUP BY game_id HAVING ROWID = max(ROWID)
    UNION SELECT * FROM part_2
)
UPDATE results
SET result = parts.result
FROM parts
WHERE (results.game_id, results.property) = (parts.game_id, parts.property);
