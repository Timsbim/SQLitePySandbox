WITH students(n, student) AS (
    VALUES (0, 'Alice'), (1, 'Bob'), (2, 'Charlie'), (3, 'David'),
           (4, 'Eve'), (5, 'Fred'), (6, 'Ginny'), (7, 'Harriet'),
           (8, 'Ileana'), (9, 'Joseph'), (10, 'Kincaid'), (11, 'Larry')
),
plants(i, student, diagram, n, plant) AS (
    SELECT 0, s.student, diagram, 2 * n + 1, ''
    FROM "kindergarten-garden" kg, students s WHERE kg.student = s.student
    UNION
    SELECT i + 1, student, diagram,
        CASE i WHEN 1 THEN n + length(diagram) / 2 ELSE n + 1 END,
        plant || CASE i WHEN 0 THEN '' ELSE ',' END || CASE substr(diagram, n, 1)
            WHEN 'G' THEN 'grass'
            WHEN 'C' THEN 'clover'
            WHEN 'R' THEN 'radishes'
            ELSE 'violets'
        END
    FROM plants WHERE i < 4
)
UPDATE "kindergarten-garden" AS kg
SET result = p.plant
FROM plants p
WHERE kg.student = p.student AND kg.diagram = p.diagram AND p.i = 4;
