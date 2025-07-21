WITH ns(i, n) AS (
	VALUES (0, 'M'), (1, 'D'), (2, 'C'), (3, 'L'), (4, 'X'), (5, 'V'), (6, 'I')
),
rms(n, i, d, r, p, rm) AS (
	SELECT number, 0, number / 1000, number % 1000, 100, ''
  	FROM "roman-numerals"
  	UNION
  	SELECT n, i + 2, r / p, r % p, p / 10,
  		   CASE
  		       WHEN d = 0 THEN ''
  			   WHEN d < 4 THEN
  			       printf('%.*c', d, (SELECT n FROM ns WHERE ns.i = rms.i))
  			   WHEN d = 4 THEN
  				   (SELECT n FROM ns WHERE ns.i = rms.i)
  				     || (SELECT n FROM ns WHERE ns.i = rms.i - 1)
  			   WHEN d = 5 THEN
  				   (SELECT n FROM ns WHERE ns.i = rms.i - 1)
  			   WHEN d < 9 THEN
  				   (SELECT n FROM ns WHERE ns.i = rms.i - 1)
  				     || printf('%.*c', d-5, (SELECT n FROM ns WHERE ns.i = rms.i))
  			   ELSE
  			       (SELECT n FROM ns WHERE ns.i = rms.i)
  				     || (SELECT n FROM ns WHERE ns.i = rms.i - 2)
  		   END
  	FROM rms WHERE i < 8
)
UPDATE "roman-numerals"
SET result = rm
FROM (SELECT n, group_concat(rm, '') rm FROM rms GROUP BY n)
WHERE number = n;
