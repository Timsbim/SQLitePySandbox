UPDATE tournament SET result = (
    WITH cs(i, r, j, c) AS (
        SELECT 2, 0, 0, substr(input, 1, 1)
        UNION ALL
        SELECT i + 1, r + (c = char(10)), (j + (c in (';', char(10)))) % 3, substr(input, i, 1)
        FROM cs WHERE i <= length(input)
    ),
    ms(A, B, res) AS (
        SELECT group_concat(c, '') FILTER (WHERE j = 0),
               group_concat(c, '') FILTER (WHERE j = 1),
               group_concat(c, '') FILTER (WHERE j = 2)
        FROM cs WHERE c NOT in (';', char(10), '') GROUP BY r
    ),
    points(Team, P) AS (
        SELECT A, CASE res WHEN 'win' THEN 3 WHEN 'draw' THEN 1 ELSE 0 END FROM ms
        UNION ALL
        SELECT B, CASE res WHEN 'win' THEN 0 WHEN 'draw' THEN 1 ELSE 3 END FROM ms
    ),
    results(Team, MP, W, D, L, P) AS (
        SELECT Team,
               count(*),
               count(P) FILTER (WHERE P = 3),
               count(P) FILTER (WHERE P = 1),
               count(P) FILTER (WHERE P = 0),
               sum(P)
        FROM points GROUP BY Team
    ),
    rows(r) AS (
        SELECT 'Team                           | MP |  W |  D |  L |  P'
        UNION ALL
        SELECT format('%-31s|% 3u |% 3u |% 3u |% 3u |% 3u', Team, MP, W, D, L, P)
        FROM (SELECT * FROM results ORDER BY P DESC, Team)
    )
    SELECT group_concat(r, char(10)) FROM rows
)
