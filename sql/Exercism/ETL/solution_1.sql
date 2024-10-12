WITH lists(input, points, list) AS (
    SELECT input, CAST(a.key AS INTEGER), a.value
    FROM etl, json_each(etl.input) AS a
),
chars(input, letter, points) AS (
    SELECT input, lower(b.value), lists.points
    FROM lists, json_each(list) as b
    ORDER BY input, b.value
),
results(input, result) AS (
    SELECT input, json_group_object(letter, points)
    FROM chars
    GROUP BY input
)
UPDATE etl
SET result = results.result
FROM results WHERE etl.input = results.input;
