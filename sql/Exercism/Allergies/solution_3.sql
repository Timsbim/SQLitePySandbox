WITH
    codes(item, code) AS (
        VALUES
            ('eggs', 1), ('peanuts', 2), ('shellfish', 4),
            ('strawberries', 8), ('tomatoes', 16),
            ('chocolate', 32), ('pollen', 64), ('cats', 128)
    ),
    results(score, result) AS (
        SELECT score, group_concat(codes.item, ', ')
        FROM (SELECT DISTINCT score FROM allergies WHERE task = 'list'), codes
        WHERE score & code
        GROUP BY score
        UNION SELECT 0, ''
    )
UPDATE allergies
SET result = CASE task
        WHEN 'allergicTo' THEN
            CASE WHEN allergies.score & c.code THEN 'true' ELSE 'false' END
        ELSE r.result
    END
FROM codes c, results r
WHERE
    (task, allergies.item) = ('allergicTo', c.item)
    OR (task, allergies.score) = ('list', r.score);
