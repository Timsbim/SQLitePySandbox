UPDATE say SET result = (
	WITH words(n, word1, word2, word3) AS (
		VALUES
          (0, '',      'ten',       NULL),
          (1, 'one',   'eleven',    NULL),
          (2, 'two',   'twelve',    'twenty'),
          (3, 'three', 'thirteen',  'thirty'),
          (4, 'four',  'fourteen',  'forty'),
          (5, 'five',  'fifteen',   'fifty'),
          (6, 'six',   'sixteen',   'sixty'),
          (7, 'seven', 'seventeen', 'seventy'),
          (8, 'eight', 'eighteen',  'eighty'),
          (9, 'nine',  'nineteen',  'ninety')
 	),
	bs(b, rem, num) AS (
    	SELECT 0, number / 1000, number % 1000
      	UNION
      	SELECT b + 1, rem / 1000, rem % 1000 FROM bs WHERE rem > 0
    ),
  	ws(b, i, rem, d, word) AS (
    	SELECT b, 1, num / 10 - NOT num, num % 10, iif(number, NULL, 'zero')
      	FROM bs
      	UNION
      	SELECT b, i + 1, rem / 10 - NOT rem, rem % 10, CASE
     		   WHEN i = 1 AND rem % 10 = 1 THEN word2
               WHEN i = 1 THEN word1
               WHEN i = 2 AND d = 1 THEN word
               WHEN i = 2 THEN word3 || iif(word != '', '-' || word, '')
      		   ELSE word1 || ' hundred' || iif(word != '', ' ' || word, '')
      		END
      	FROM ws, words WHERE d = n AND rem >= 0
    ),
  	units(n, word) AS (
		VALUES (0, ''), (1, ' thousand'), (2, ' million'), (3, ' billion')
    )
  	SELECT group_concat(ws.word || iif(ws.word != '', us.word, ''), ' ')
  	FROM (SELECT b, word FROM ws WHERE rem = -1 ORDER BY b DESC) ws,
         (SELECT n, word FROM units ORDER BY n) us
    WHERE ws.b = us.n
) WHERE NOT error IS NOT NULL
