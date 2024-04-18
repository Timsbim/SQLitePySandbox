WITH RECURSIVE steps(number, n, step) AS (
    SELECT number, number, 0 FROM collatz
    UNION ALL
    SELECT number, iif(n % 2, 3 * n + 1, n / 2), step + 1 FROM steps
    WHERE n != 1
)
UPDATE collatz
SET steps = steps.step
FROM steps 
WHERE collatz.number = steps.number;
