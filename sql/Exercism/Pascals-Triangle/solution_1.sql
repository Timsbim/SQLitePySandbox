WITH arrays(row, ns) AS (
  	SELECT 1, '[1]'
  	UNION
  	SELECT row + 1,
    	   (SELECT json_group_array(n)
            FROM (SELECT 1 n
                  UNION ALL
                  SELECT a.value + b.value n
                  FROM json_each(ns) a, json_each(ns) AS b
                  WHERE a.ROWID = b.ROWID - 1
                  UNION ALL
                  SELECT 1 n))
  	FROM arrays
  	LIMIT (SELECT max(input) FROM "pascals-triangle")
),
rows(row, ns) AS (SELECT row, replace(trim(ns, '[]'), ',', ' ') FROM arrays)
UPDATE "pascals-triangle"
SET result = coalesce(trios.trio, '')
FROM (SELECT input, group_concat(ns, char(10)) AS trio 
      FROM "pascals-triangle" LEFT JOIN rows ON row <= input
      GROUP BY input) trios
WHERE "pascals-triangle".input = trios.input;
