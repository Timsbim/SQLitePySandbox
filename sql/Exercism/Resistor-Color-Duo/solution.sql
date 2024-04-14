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
SET result = c1.code * 10 + c2.code
FROM coding c1, coding c2
WHERE (color1, color2) = (c1.color, c2.color);
