UPDATE leap
SET is_leap = CASE
        WHEN year % 100 = 0 THEN year % 400 = 0
        ELSE year % 4 = 0
    END;
