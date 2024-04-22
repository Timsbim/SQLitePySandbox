WITH daysofweek(dayofweek, day_no) AS (
    VALUES ('Monday', 0), ('Tuesday', 1), ('Wednesday', 2),
           ('Thursday', 3), ('Friday', 4), ('Saturday', 5),
           ('Sunday', 6)
),
weeks(week, week_no) AS (
    VALUES ('first', 0), ('second', 1), ('third', 2), ('fourth', 3)
)
SELECT year, month, week,
       day_no,
       CASE week
           WHEN 'teenth' THEN format('%i-%.2i-%.2i', year, month, 10)
           WHEN 'last' THEN
               date(format('%i-%.2i-%.2i', year, month, 1), '1 months', '-1 days')
           ELSE format('%i-%.2i-%.2i', year, month, week_no * 7 + 1)
       END start
FROM meetup
     LEFT JOIN daysofweek USING(dayofweek)
     LEFT JOIN weeks USING(week)
;
