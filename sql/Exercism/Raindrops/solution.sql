UPDATE raindrops
SET sound = coalesce(
        nullif(
            CASE WHEN number % 3 THEN '' ELSE 'Pling' END ||
            CASE WHEN number % 5 THEN '' ELSE 'Plang' END ||
            CASE WHEN number % 7 THEN '' ELSE 'Plong' END,
            ''
        ),
        number
    );
