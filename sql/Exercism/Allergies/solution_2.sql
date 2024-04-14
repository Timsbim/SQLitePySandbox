WITH codes(item, code) AS (
    VALUES
        ('eggs', 1),
        ('peanuts', 2),
        ('shellfish', 4),
        ('strawberries', 8),
        ('tomatoes', 16),
        ('chocolate', 32),
        ('pollen', 64),
        ('cats', 128)
)
UPDATE allergies
SET result = CASE task
        WHEN 'allergicTo' THEN
            CASE WHEN allergies.score & codes.code THEN 'true' ELSE 'false' END
        ELSE coalesce(
                (SELECT group_concat(codes.item, ', ')
                 FROM codes
                 WHERE allergies.score & codes.code),
                ''
            )
    END
FROM codes
WHERE (task, allergies.item) = ('allergicTo', codes.item) OR task = 'list';
