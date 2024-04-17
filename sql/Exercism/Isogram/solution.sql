WITH RECURSIVE letters(phrase, low, pos, letter) AS (
    SELECT phrase, lower(phrase), 1, lower(substr(phrase, 1, 1)) FROM isogram
    UNION ALL
    SELECT phrase, low, pos + 1, substr(low, pos + 1, 1) FROM letters
    WHERE length(phrase) > pos
),
checks(phrase, is_isogram) AS (
    SELECT phrase, count(letter) = count(DISTINCT letter) FROM letters
    WHERE letter GLOB '[a-z]'
    GROUP BY phrase
    UNION SELECT '', 1
)
UPDATE isogram
SET is_isogram = checks.is_isogram
FROM checks
WHERE isogram.phrase = checks.phrase;
