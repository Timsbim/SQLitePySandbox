SELECT id,
       part,
       row_number() OVER(PARTITION BY part ORDER BY value),
       row_number() OVER(PARTITION BY part),
       value
FROM test;
