WITH RECURSIVE sums(number, string, pos, digit, sum) AS (
    SELECT number, CAST(number AS TEXT), 1, 0, 0 FROM armstrong_numbers
    UNION ALL
    SELECT number,
           string,
           pos + 1,
           CAST(substr(string, pos, 1) AS INTEGER),
           sum + pow(digit, length(string)) 
    FROM sums
    WHERE length(string) >= pos
)
SELECT * FROM sums ORDER BY number, pos;
