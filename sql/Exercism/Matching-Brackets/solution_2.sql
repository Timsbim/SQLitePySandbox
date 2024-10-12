UPDATE "matching-brackets"
SET result = (
    WITH RECURSIVE stacks(pos, stack) AS (
        SELECT 1, ""
        UNION ALL
        SELECT
            pos + 1,
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
    SELECT stack == "" FROM stacks WHERE pos = length(input) + 1
)
