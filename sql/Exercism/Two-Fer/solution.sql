UPDATE twofer
SET response =
    'One for ' || coalesce(nullif(input, ''), 'you') || ', one for me.';
