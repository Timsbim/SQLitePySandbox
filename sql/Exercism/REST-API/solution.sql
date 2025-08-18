UPDATE "rest-api" SET result = CASE url
    WHEN '/users' THEN
        (SELECT json_object('users', json_group_array(json(value)))
         FROM (SELECT value, value ->> '$.name' AS name
               FROM json_each(database, '$.users')
               WHERE payload = '{}'
                     OR name IN (SELECT value FROM json_each(payload, '$.users'))
               ORDER BY name))
    WHEN '/add' THEN
        json_object('name', payload ->> '$.user',
                    'owes', json('{}'),
                    'owed_by', json('{}'),
                    'balance', 0)
    WHEN '/iou' THEN (
    	WITH ds(n, m, v) AS (
        	SELECT (us.value ->> '$.name') n, t.key m, iif(t.path GLOB '*.owes', -1, 1) * t.value
            FROM json_each(database ->> '$.users') us, json_tree(us.value) t
            WHERE n IN (payload ->> '$.lender', payload ->> '$.borrower')
                  AND m NOT IN ('name', 'balance') AND t.atom IS NOT NULL
      		UNION ALL VALUES
                ((payload ->> '$.lender'), (payload ->> '$.borrower'), (payload ->> '$.amount')),
      			((payload ->> '$.borrower'), (payload ->> '$.lender'), -(payload ->> '$.amount'))
        )
      	SELECT json_object(
            'users',
            json_group_array(
                json_object('name', n, 'owes', json(o), 'owed_by', json(ob), 'balance', b)
            )
        ) FROM (SELECT n,
                       json_group_object(m, -v) FILTER (WHERE v < 0) o,
                       json_group_object(m, v) FILTER (WHERE v > 0) ob,
          		       sum(v) b
          	    FROM (SELECT n, m, sum(v) v FROM ds GROUP BY n, m)
                GROUP BY n)
	)
END
