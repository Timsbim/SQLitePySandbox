            UPDATE bob
            SET reply = CASE
                    WHEN length(trim(input, ' 
	')) = 0 THEN 'Fine. Be that way!'
                    WHEN rtrim(input, ' 
	') GLOB '*[?]' THEN
                        iif(input GLOB '*[a-zA-Z]*' AND upper(input) = input,
                            'Calm down, I know what I''m doing!', 'Sure.')
                    WHEN input GLOB '*[a-zA-Z]*' AND upper(input) = input THEN
                        'Whoa, chill out!'
                    ELSE 'Whatever.'
                END;
