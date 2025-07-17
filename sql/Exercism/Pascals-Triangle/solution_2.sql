WITH arrays(row, arr, ns) AS (
  	SELECT 1, '[1,1]', '1'
  	UNION
  	SELECT row + 1,
    	   (SELECT json_group_array(n)
            FROM (SELECT 1 n
                  UNION ALL
                  SELECT a.value + b.value n
                  FROM json_each(arr) a, json_each(arr) AS b
                  WHERE a.ROWID = b.ROWID - 1
                  UNION ALL
                  SELECT 1 n)),
  			ns || char(10) || replace(trim(arr, '[]'), ',', ' ')
  	FROM arrays
  	LIMIT (SELECT max(input) FROM "pascals-triangle")
)
UPDATE "pascals-triangle"
SET result = coalesce(ns, '')
FROM ("pascals-triangle" a LEFT JOIN arrays ON row = input) trios
WHERE "pascals-triangle".input = trios.input;
