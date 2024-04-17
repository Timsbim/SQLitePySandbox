WITH selection(game_id) AS (
    SELECT DISTINCT game_id FROM results
    WHERE property IN ('scores', 'personalBest')
),
part_1 (game_id, scores, personalBest) AS (
    SELECT game_id, group_concat(score, ','), max(score) FROM scores
    WHERE game_id IN selection
    GROUP BY game_id
)
UPDATE results
SET result = CASE property
        WHEN 'scores' THEN part_1.scores ELSE personalBest
    END
FROM part_1
WHERE results.game_id = part_1.game_id;
