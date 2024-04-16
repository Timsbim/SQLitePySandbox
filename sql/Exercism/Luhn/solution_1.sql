UPDATE luhn SET result = 0;
WITH RECURSIVE
clean(value, clean) AS (
    SELECT value, replace(value, ' ', '') FROM luhn
    WHERE NOT value GLOB '*[^0-9 ]*'
),
sums(value, n, digit, sum, rest) AS (
    SELECT value, 1, 0, 0, '0' || clean FROM clean WHERE length(clean) > 1
    UNION ALL
    SELECT
        value, n + 1,
        CAST(substr(rest, length(rest)) AS INTEGER),
        sum + iif(switch > 0, iif(digit < 5, 2 * digit, 2 * digit - 9), digit)
        substr(rest, 0, length(rest))
    FROM sums
    WHERE length(rest) > 0
)
UPDATE luhn
SET result = sums.sum % 10 = 0
FROM sums
WHERE (luhn.value, rest) = (sums.value, '');
