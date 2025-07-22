UPDATE "rest-api"
SET result = (
    CASE url
        WHEN '/users' THEN
            CASE payload
                WHEN '{}' THEN (
                    SELECT json_object("users", json_group_array(json(value)))
                    FROM (SELECT value FROM json_each(database, '$.users') ORDER BY value ->> '$.name')
                ) ELSE (
                    SELECT json_object("users", json_group_array(json(value)))
                    FROM (SELECT value, value ->> '$.name' AS name FROM json_each(database, '$.users')
                          WHERE name IN (SELECT value FROM json_each(payload, '$.users')) ORDER BY name)
                )
            END
        WHEN '/add' THEN
            json_object(
                'name', payload ->> '$.user',
                'owes', json('{}'),
                'owed_by', json('{}'),
                'balance', 0
            )
        WHEN '/iou' THEN (
            SELECT json_group_array(value)
            FROM (
                SELECT value, value ->> '$.name' AS name
                FROM json_each(database, '$.users')
                WHERE
                    name = payload ->> '$.lender'
                    OR name = payload ->> '$.borrower'
            )
        )
    END
)
