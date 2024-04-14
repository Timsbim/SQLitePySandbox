UPDATE "difference-of-squares"
SET result =
    CASE
        WHEN property = 'squareOfSum' THEN
            number * number * (number + 1) * (number + 1) / 4
        WHEN property = 'sumOfSquares' THEN
            number * (number + 1) * (2 * number + 1) / 6
        ELSE
            number * number * (number + 1) * (number + 1) / 4
            - number * (number + 1) * (2 * number + 1) / 6
    END;
