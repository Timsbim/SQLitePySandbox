WITH RECURSIVE stacks(input, pos, stack) AS (
    SELECT input, 1, "" FROM "matching-brackets"
    UNION ALL
    SELECT
        input, pos + 1,
        CASE substr(input, pos, 1)
            WHEN stack = "X" THEN stack
            WHEN "[" THEN "[" || stack
            WHEN "{" THEN "{" || stack
            WHEN "(" THEN "(" || stack
            WHEN "]" THEN iif(substr(stack, 1, 1) = "[", substr(stack, 2), "X")
            WHEN "}" THEN iif(substr(stack, 1, 1) = "{", substr(stack, 2), "X")
            WHEN ")" THEN iif(substr(stack, 1, 1) = "(", substr(stack, 2), "X")
            ELSE stack
        END
    FROM stacks WHERE pos <= length(input)
)
UPDATE "matching-brackets"
SET result = s.stack = ""
FROM stacks AS s
WHERE "matching-brackets".input = s.input AND s.pos = length(s.input) + 1;
