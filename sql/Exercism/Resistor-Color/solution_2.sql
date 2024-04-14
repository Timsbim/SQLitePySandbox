WITH coding(color, code) AS (
    VALUES
        ('black',  0),
        ('brown',  1),
        ('red',    2),
        ('orange', 3),
        ('yellow', 4),
        ('green',  5),
        ('blue',   6),
        ('violet', 7),
        ('grey',   8),
        ('white',  9)              
)
UPDATE color_code
SET result = coding.code
FROM coding
WHERE color_code.color = coding.color;
