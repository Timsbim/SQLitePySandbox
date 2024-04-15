CREATE TABLE codes (item TEXT, code INT);
INSERT INTO codes
    VALUES
        ('eggs', 1), ('peanuts', 2), ('shellfish', 4), ('strawberries', 8),
        ('tomatoes', 16), ('chocolate', 32), ('pollen', 64), ('cats', 128);
UPDATE allergies
SET result = CASE WHEN allergies.score & c.code THEN 'true' ELSE 'false' END
FROM codes c
WHERE task = 'allergicTo' AND allergies.item = c.item;
UPDATE allergies
SET result = coalesce(
        (SELECT group_concat(c.item, ', ')
         FROM codes c
         WHERE allergies.score & c.code),
         ''
    )
WHERE task = 'list';
