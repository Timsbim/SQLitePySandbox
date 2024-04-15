WITH RECURSIVE steps(number, n, step) AS (
    SELECT number, number, 0 FROM collatz
    UNION ALL
    SELECT number, CASE WHEN n % 2 THEN 3 * n + 1 ELSE n / 2 END, step + 1
    FROM steps
    WHERE n != 1
)
UPDATE collatz
SET steps = steps.step
FROM steps 
WHERE (collatz.number, 1) = (steps.number, n);
