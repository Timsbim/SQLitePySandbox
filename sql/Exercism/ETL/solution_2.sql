UPDATE etl
SET result = (
    WITH lists(points, list) AS (
        SELECT CAST(key AS INTEGER), value
        FROM json_each(input)
    ),
    chars(letter, points) AS (
        SELECT lower(value), lists.points
        FROM lists, json_each(list)
        ORDER BY value
    )
    SELECT json_group_object(letter, points) FROM chars
)
