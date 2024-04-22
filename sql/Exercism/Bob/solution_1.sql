UPDATE bob
SET reply = CASE
        WHEN input REGEXP '^\s*$' THEN 'Fine. Be that way!'
        WHEN input REGEXP '\?\s*$' THEN
            iif(input GLOB '*[a-zA-Z]*' AND upper(input) = input,
                'Calm down, I know what I''m doing!', 'Sure.')
        WHEN input GLOB '*[a-zA-Z]*' AND upper(input) = input THEN
            'Whoa, chill out!'
        ELSE 'Whatever.'
    END;
