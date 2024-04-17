WITH RECURSIVE sums(number, string, e, pos, sum) AS (
    SELECT number,
           CAST(number AS TEXT),
           length(CAST(number AS TEXT)),
           0, 0
    FROM "armstrong-numbers"
    UNION ALL
    SELECT number, string, e,  pos + 1,
           sum + power(CAST(substr(string, pos + 1, 1) AS INTEGER), e)
    FROM sums
    WHERE e >= pos
)
UPDATE "armstrong-numbers"
SET result = sums.number = sums.sum
FROM sums
WHERE "armstrong-numbers".number = sums.number AND pos = e + 1;
