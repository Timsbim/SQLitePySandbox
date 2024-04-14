WITH RECURSIVE counts(square, grains) AS (
    SELECT 1, 1
    UNION ALL
    SELECT square + 1, grains * 2 FROM counts
    LIMIT 65
)
UPDATE grains
SET result = CASE
        WHEN task = 'single-square' THEN counts.grains
        ELSE counts.grains - 1
    END
FROM counts
WHERE
    (grains.task = 'single-square' AND grains.square = counts.square)
    OR (grains.task = 'total' AND counts.square = 65);
