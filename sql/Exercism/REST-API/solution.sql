UPDATE "rest-api"
SET result = (
    CASE url
        WHEN "/users" THEN
            (SELECT json_object("users", json_group_array(value))
             FROM json_each(database, '$.users')
             WHERE (value ->> '$.name') IN (SELECT value FROM json_each(payload, '$.users')))
        WHEN "/add" THEN
            json_object("name", payload ->> '$.user', "owes", json("{}"), "owed_by", json("{}"), "balance", 0)
        WHEN "/iou" THEN NULL
    END
)            
