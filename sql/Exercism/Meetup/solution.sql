WITH daysofweek(dayofweek, day_no) AS (
    VALUES ('Sunday', 0), ('Monday', 1), ('Tuesday', 2), ('Wednesday', 3),
           ('Thursday', 4), ('Friday', 5), ('Saturday', 6)
),
weeks(week, week_no) AS (
    VALUES ('first', 0), ('second', 1), ('third', 2), ('fourth', 3)
),
dates_1(year, month, week, doyofweek, dow, start) AS (
    SELECT year, month, week, dayofweek, day_no,
           CASE week
               WHEN 'teenth' THEN format('%i-%.2i-%.2i', year, month, 13)
               WHEN 'last' THEN date(
                        format('%i-%.2i-%.2i', year, month, 1),
                        '1 months', '-1 days'
                    )
               ELSE format('%i-%.2i-%.2i', year, month, week_no * 7 + 1)
           END
    FROM meetup LEFT JOIN weeks USING(week)
                LEFT JOIN daysofweek USING(dayofweek)
),
dates(year, month, week, dayofweek, dow, start, sdow) AS (
    SELECT *, CAST(strftime('%w', start) AS INT) FROM dates_1
)
UPDATE meetup
SET result = date(
        start,
        format(
            '%i days',
            iif(sdow <= dow, dow - sdow, 7 - sdow + dow)
                - iif(meetup.week = 'last' AND sdow != dow, 7, 0)
        )
    )
FROM dates
WHERE (meetup.year, meetup.month, meetup.week, meetup.dayofweek)
      = (dates.year, dates.month, dates.week, dates.dayofweek);
