UPDATE luhn SET result = 0;
WITH RECURSIVE clean(value, clean) AS (
    SELECT value, replace(value, ' ', '') FROM luhn
    WHERE NOT value GLOB '*[^0-9 ]*'
),
sums(value, clean, pos, switch, d, sum) AS (
    SELECT value, '0' || clean, length(clean) + 1, 1, 0, 0 FROM clean
    WHERE length(clean) > 1
    UNION ALL
    SELECT value, clean, pos - 1, switch * -1,
           CAST(substr(clean, pos, 1) AS INTEGER),
           sum + iif(switch > 0, iif(d < 5, 2 * d, 2 * d - 9), d)
    FROM sums
    WHERE pos > 0
)
UPDATE luhn
SET result = sums.sum % 10 = 0
FROM sums
WHERE luhn.value = sums.value;
