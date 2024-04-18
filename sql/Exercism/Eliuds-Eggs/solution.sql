WITH counts(number, n, eggs) AS (
    SELECT number, number >> 1, number & 1 FROM "eliuds-eggs"
    UNION ALL
    SELECT number, n >> 1, eggs + (n & 1) FROM counts WHERE n > 0
)
UPDATE "eliuds-eggs"
SET result = eggs
FROM counts WHERE "eliuds-eggs".number = counts.number;
