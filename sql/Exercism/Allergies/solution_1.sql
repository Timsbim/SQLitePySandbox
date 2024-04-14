CREATE TABLE codes (item TEXT, code INT);
INSERT INTO codes
    VALUES
        ('eggs', 1),
        ('peanuts', 2),
        ('shellfish', 4),
        ('strawberries', 8),
        ('tomatoes', 16),
        ('chocolate', 32),
        ('pollen', 64),
        ('cats', 128);
UPDATE allergies
SET result = CASE WHEN allergies.score & codes.code THEN 'true' ELSE 'false' END
FROM codes
WHERE (task, allergies.item) = ('allergicTo', codes.item);
UPDATE allergies
SET result = coalesce(
        (SELECT group_concat(codes.item, ', ')
         FROM codes
         WHERE allergies.score & codes.code),
        ''
    )
WHERE task = 'list';
