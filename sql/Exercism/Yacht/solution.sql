WITH RECURSIVE rolls(res, cat, p, roll) AS (
    SELECT dice_results, category, 4, CAST(substr(dice_results, 1, 1) AS INT) FROM yacht
    UNION ALL
    SELECT res, cat, p + 3, CAST(substr(res, p, 1) AS INT) FROM rolls WHERE p < 14
),
groups(res, cat, roll, num, score) AS (
    SELECT res, cat, roll, count(roll), sum(roll) FROM rolls GROUP BY res, cat, roll
),
results(res, cat, val) AS (
    SELECT
        res, cat,
        CASE cat
            WHEN 'ones' THEN ifnull(sum(score) FILTER (WHERE roll IS 1), 0)
            WHEN 'twos' THEN ifnull(sum(score) FILTER (WHERE roll IS 2), 0)
            WHEN 'threes' THEN ifnull(sum(score) FILTER (WHERE roll IS 3), 0)
            WHEN 'fours' THEN ifnull(sum(score) FILTER (WHERE roll IS 4), 0)
            WHEN 'fives' THEN ifnull(sum(score) FILTER (WHERE roll IS 5), 0)
            WHEN 'sixes' THEN ifnull(sum(score) FILTER (WHERE roll IS 6), 0)
            WHEN 'full house' THEN iif(group_concat(num, '') in ('23', '32'), sum(score), 0)
            WHEN 'four of a kind' THEN CASE num
                    WHEN 5 THEN score - roll
                    ELSE ifnull(sum(score) FILTER (WHERE num = 4), 0)
                END
            WHEN 'little straight' THEN iif(group_concat(roll, '') = '12345', 30, 0)
            WHEN 'big straight' THEN iif(group_concat(roll, '') = '23456', 30, 0)
            WHEN 'choice' THEN sum(score)
            WHEN 'yacht' THEN iif(sum(score) FILTER (WHERE num IS 5) IS NULL, 0, 50)
        END
    FROM groups
    GROUP BY res, cat
    ORDER BY roll
)
UPDATE yacht
SET result = val
FROM results
WHERE (yacht.dice_results, yacht.category) = (results.res, results.cat);
