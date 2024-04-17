SELECT id,
       part,
       row_number() OVER(PARTITION BY part),
       row_number() OVER(PARTITION BY part ORDER BY value),
       value
FROM test;
