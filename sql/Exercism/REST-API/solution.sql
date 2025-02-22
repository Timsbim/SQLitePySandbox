UPDATE "rest-api"
SET result = (
    CASE url
        WHEN '/users' THEN
            CASE payload
                WHEN 'null' THEN (
                    SELECT json_object(
                        "users",
                        json_group_array(json(value))
                    )
                    FROM (
                        SELECT value
                        FROM json_each(database, '$.users')
                        ORDER BY value ->> '$.name'
                    )
                ) ELSE (
                    SELECT json_object(
                        "users",
                        json_group_array(json(value))
                    )
                     FROM (
                        SELECT value, value ->> '$.name' AS name
                        FROM json_each(database, '$.users')
                        WHERE name IN (
                            SELECT value
                            FROM json_each(payload, '$.users')
                        )
                        ORDER BY name
                    )
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
            --coalesce(database ->> '$.users[5]', '"foo!"')                           
            SELECT json_group_array(json(user))
            FROM (
                SELECT
                    CASE value ->> '$.name'
                        WHEN "rest-api".payload ->> '$.lender' THEN
                            "rest-api".payload ->> '$.amount'
                        WHEN "rest-api".payload ->> '$.borrower' THEN
                            json_set(
                                value,
                                '$.amount',
                                coalesce(value ->> '$.amount', 0)
                                    + ("rest-api".payload ->> '$.amount'),
                                value,
                                '$.owed_by',
                                json_set(
                                    value ->> '$.owed_by',
                                    "rest-api".payload ->> '$.borrower',
                                    coalesce(
                                        value ->> ('$.owed_by.' || ("rest-api".payload -> '$.borrower')),
                                        0
                                    ) + ("rest-api".payload ->> '$.amount')
                                )
                            )
                    END AS user
                FROM json_each(database, '$.users')
                WHERE user IS NOT NULL
            )
        )
    END
)
