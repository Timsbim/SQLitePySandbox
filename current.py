from pathlib import Path
from pprint import pprint
from textwrap import dedent, indent
import sqlite3 as sqlite


print(f"\nSQLite version: {sqlite.sqlite_version}", end="\n\n")


# Helper functions


def print_query(query, filepath=None):
    """Print the query/ies formatted, and write to file if filename
    provided"""
    if isinstance(query, list):
        query = "\n\n".join(query)
    if filepath is not None:
        filepath.write_text(query)
    query = indent(query, "\t")
    print(f"Executing:\n\n{query}")


# Constants

SQL_PATH = Path("sql/Exercism/")
SQL_PATH.mkdir(parents=True, exist_ok=True)


# Exercism SQLite path exercises


def high_scores():
    """Exercism SQLite path exercise 18, High Scores:
    https://exercism.org/tracks/sqlite/exercises/high-scores"""

    sql_path = SQL_PATH / "High-Scores"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE scores (game_id TEXT, score INT);
            CREATE TABLE results (game_id TEXT, property TEXT, result TEXT);
            INSERT INTO results(game_id, property)
                VALUES
                    ('1035eb93-2208-4c22-bab8-fef06769a73c', 'scores'),
                    ('6aa5dbf5-78fa-4375-b22c-ffaa989732d2', 'latest'),
                    ('b661a2e1-aebf-4f50-9139-0fb817dd12c6', 'personalBest'),
                    ('3d996a97-c81c-4642-9afc-80b80dc14015', 'personalTopThree'),
                    ('1084ecb5-3eb4-46fe-a816-e40331a4e83a', 'personalTopThree'),
                    ('e6465b6b-5a11-4936-bfe3-35241c4f4f16', 'personalTopThree'),
                    ('f73b02af-c8fd-41c9-91b9-c86eaa86bce2', 'personalTopThree'),
                    ('16608eae-f60f-4a88-800e-aabce5df2865', 'personalTopThree'),
                    ('2df075f9-fec9-4756-8f40-98c52a11504f', 'latest'),
                    ('809c4058-7eb1-4206-b01e-79238b9b71bc', 'scores'),
                    ('ddb0efc0-9a86-4f82-bc30-21ae0bdc6418', 'latest'),
                    ('6a0fd2d1-4cc4-46b9-a5bb-2fb667ca2364', 'scores');
            """)
        con.executescript(query)
        inputs = (
            ('1035eb93-2208-4c22-bab8-fef06769a73c', '30,50,20,70'),
            ('6aa5dbf5-78fa-4375-b22c-ffaa989732d2', '100,0,90,30'),
            ('b661a2e1-aebf-4f50-9139-0fb817dd12c6', '40,100,70'),
            ('3d996a97-c81c-4642-9afc-80b80dc14015', '10,30,90,30,100,20,10,0,30,40,40,70,70'),
            ('1084ecb5-3eb4-46fe-a816-e40331a4e83a', '20,10,30'),
            ('e6465b6b-5a11-4936-bfe3-35241c4f4f16', '40,20,40,30'),
            ('f73b02af-c8fd-41c9-91b9-c86eaa86bce2', '30,70'),
            ('16608eae-f60f-4a88-800e-aabce5df2865', '40'),
            ('2df075f9-fec9-4756-8f40-98c52a11504f', '70,50,20,30'),
            ('809c4058-7eb1-4206-b01e-79238b9b71bc', '30,50,20,70'),
            ('ddb0efc0-9a86-4f82-bc30-21ae0bdc6418', '20,70,15,25,30'),
            ('6a0fd2d1-4cc4-46b9-a5bb-2fb667ca2364', '20,70,15,25,30')
        )
        data = (
            (ID, int(score))
            for ID, string in inputs
            for score in string.split(",")
        )
        con.executemany("INSERT INTO scores VALUES(?, ?)", data)
        query = dedent("""\
            SELECT game_id,
                   group_concat(score, ',') scores,
                   max(score) personalBest
            FROM scores
            GROUP BY game_id
            """)
        query = dedent("""\
            SELECT results.game_id,
                   (SELECT group_concat(score, '-')
                    FROM scores
                    WHERE scores.game_id = results.game_id
                    ORDER BY score ASC
                    LIMIT 3)
            FROM results, scores
            WHERE results.game_id = scores.game_id
            GROUP BY results.game_id
            """)
        #print_query(query, filepath=sql_path / "solution.sql")        
        #con.execute(query)
        #query = "SELECT * FROM results;"
        res = con.execute(query)
        pprint(res.fetchall())


high_scores()


def luhn():
    """Exercism SQLite path exercise 20, Luhn:
    https://exercism.org/tracks/sqlite/exercises/luhn"""
 
    sql_path = SQL_PATH / "Luhn"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE luhn (value TEXT, result Boolean);
            INSERT INTO luhn (value)
               VALUES
                    ("1"),
                    ("0"),
                    ("059"),
                    ("59"),
                    ("055 444 285"),
                    ("055 444 286"),
                    ("8273 1232 7352 0569"),
                    ("1 2345 6789 1234 5678 9012"),
                    ("1 2345 6789 1234 5678 9013"),
                    ("095 245 88"),
                    ("234 567 891 234"),
                    ("059a"),
                    ("055-444-285"),
                    ("055# 444$ 285"),
                    (" 0"),
                    ("0000 0"),
                    ("091"),
                    ("9999999999 9999999999 9999999999 9999999999"),
                    ("109"),
                    ("055b 444 285"),
                    (":9"),
                    ("59%59");
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query_1 = dedent("""\
            UPDATE luhn SET result = 0;
            WITH RECURSIVE
            clean(value, clean) AS (
                SELECT value, replace(value, ' ', '') FROM luhn
                WHERE NOT value GLOB '*[^0-9 ]*'
            ),
            sums(value, n, digit, sum, rest) AS (
                SELECT value, 1, 0, 0, '0' || clean FROM clean WHERE length(clean) > 1
                UNION ALL
                SELECT
                    value, n + 1,
                    CAST(substr(rest, length(rest)) AS INTEGER),
                    sum + iif(switch > 0, iif(digit < 5, 2 * digit, 2 * digit - 9), digit)
                    substr(rest, 0, length(rest))
                FROM sums
                WHERE length(rest) > 0
            )
            UPDATE luhn
            SET result = sums.sum % 10 = 0
            FROM sums
            WHERE (luhn.value, rest) = (sums.value, '');
            """)
        print_query(query_1, filepath=sql_path / "solution_1.sql")
        query_2 = dedent("""\
            UPDATE luhn SET result = 0;
            WITH RECURSIVE clean(value, clean) AS (
                SELECT value, replace(value, ' ', '') FROM luhn
                WHERE NOT value GLOB '*[^0-9 ]*'
            ),
            sums(value, clean, pos, switch, digit, sum) AS (
                SELECT value, '0' || clean, length(clean) + 1, 1, 0, 0 FROM clean
                WHERE length(clean) > 1
                UNION ALL
                SELECT
                    value, clean, pos - 1, switch * -1,
                    CAST(substr(clean, pos, 1) AS INTEGER),
                    sum + iif(switch > 0, iif(digit < 5, 2 * digit, 2 * digit - 9), digit)
                FROM sums
                WHERE pos > 0
            )
            UPDATE luhn
            SET result = sums.sum % 10 = 0
            FROM sums
            WHERE (luhn.value, pos) = (sums.value, 0);
            """)
        print_query(query_2, filepath=sql_path / "solution_2.sql")
        con.executescript(query_2)
        query = "SELECT * FROM luhn;"
        res = con.execute(query)
        pprint(res.fetchall())
 
 
#luhn()


def isogram():
    """Exercism SQLite path exercise 19, Isogram:
    https://exercism.org/tracks/sqlite/exercises/isogram"""
 
    sql_path = SQL_PATH / "Isogram"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE isogram (phrase TEXT, is_isogram INT);
            INSERT INTO isogram (phrase)
                VALUES
                    (''),
                    ('isogram'),
                    ('eleven'),
                    ('zzyzx'),
                    ('subdermatoglyphic'),
                    ('Alphabet'),
                    ('alphAbet'),
                    ('thumbscrew-japingly'),
                    ('thumbscrew-jappingly'),
                    ('six-year-old'),
                    ('Emily Jung Schwartzkopf'),
                    ('accentor'),
                    ('angola'),
                    ('up-to-date');
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
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
            """)
        print_query(query, filepath=sql_path / "solution.txt")
        con.executescript(query)
        query = "SELECT * FROM isogram;"
        res = con.execute(query)
        pprint(res.fetchall())


#isogram()


def collatz():
    """Exercism SQLite path exercise 17, Collatz Conjecture:
    https://exercism.org/tracks/sqlite/exercises/collatz-conjecture"""

    sql_path = SQL_PATH / "Collatz-Conjecture"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE collatz (number INTEGER, steps INTEGER);
            INSERT INTO collatz (number)
                VALUES (1), (16), (12), (1000000);
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
            WITH RECURSIVE steps(number, n, step) AS (
                SELECT number, number, 0 FROM collatz
                UNION ALL
                SELECT number, CASE WHEN n % 2 THEN 3 * n + 1 ELSE n / 2 END, step + 1
                FROM steps
                WHERE n != 1
            )
            UPDATE collatz
            SET steps = steps.step
            FROM steps 
            WHERE (collatz.number, 1) = (steps.number, n);
            """)
        print_query(query, filepath=sql_path / "solution.sql")        
        con.execute(query)
        query = "SELECT * FROM collatz;"
        res = con.execute(query)
        pprint(res.fetchall())


#collatz()


def allergies():
    """Exercism SQLite path exercise 11, Allergies:
    https://exercism.org/tracks/sqlite/exercises/allergies"""

    sql_path = SQL_PATH / "Allergies"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE allergies (
                task TEXT,
                item TEXT,
                score INT NOT NULL,
                result TEXT
            );
            INSERT INTO allergies (task, item, score)
                VALUES
                    ('allergicTo', 'eggs', 0),
                    ('allergicTo', 'eggs', 1),
                    ('allergicTo', 'eggs', 3),
                    ('allergicTo', 'eggs', 2),
                    ('allergicTo', 'eggs', 255),
                    ('allergicTo', 'peanuts', 0),
                    ('allergicTo', 'peanuts', 2),
                    ('allergicTo', 'peanuts', 7),
                    ('allergicTo', 'peanuts', 5),
                    ('allergicTo', 'peanuts', 255),
                    ('allergicTo', 'shellfish', 0),
                    ('allergicTo', 'shellfish', 4),
                    ('allergicTo', 'shellfish', 14),
                    ('allergicTo', 'shellfish', 10),
                    ('allergicTo', 'shellfish', 255),
                    ('allergicTo', 'strawberries', 0),
                    ('allergicTo', 'strawberries', 8),
                    ('allergicTo', 'strawberries', 28),
                    ('allergicTo', 'strawberries', 20),
                    ('allergicTo', 'strawberries', 255),
                    ('allergicTo', 'tomatoes', 0),
                    ('allergicTo', 'tomatoes', 16),
                    ('allergicTo', 'tomatoes', 56),
                    ('allergicTo', 'tomatoes', 40),
                    ('allergicTo', 'tomatoes', 255),
                    ('allergicTo', 'chocolate', 0),
                    ('allergicTo', 'chocolate', 32),
                    ('allergicTo', 'chocolate', 112),
                    ('allergicTo', 'chocolate', 80),
                    ('allergicTo', 'chocolate', 255),
                    ('allergicTo', 'pollen', 0),
                    ('allergicTo', 'pollen', 64),
                    ('allergicTo', 'pollen', 224),
                    ('allergicTo', 'pollen', 160),
                    ('allergicTo', 'pollen', 255),
                    ('allergicTo', 'cats', 0),
                    ('allergicTo', 'cats', 128),
                    ('allergicTo', 'cats', 192),
                    ('allergicTo', 'cats', 64),
                    ('allergicTo', 'cats', 255),
                    ('list', '', 0),
                    ('list', '', 1),
                    ('list', '', 2),
                    ('list', '', 8),
                    ('list', '', 3),
                    ('list', '', 5),
                    ('list', '', 248),
                    ('list', '', 255),
                    ('list', '', 509),
                    ('list', '', 257);
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query_1 = dedent("""\
            CREATE TABLE codes (item TEXT, code INT);
            INSERT INTO codes
                VALUES
                    ('eggs', 1), ('peanuts', 2), ('shellfish', 4), ('strawberries', 8),
                    ('tomatoes', 16), ('chocolate', 32), ('pollen', 64), ('cats', 128);
            UPDATE allergies
            SET result = CASE WHEN allergies.score & c.code THEN 'true' ELSE 'false' END
            FROM codes c
            WHERE task = 'allergicTo' AND allergies.item = c.item;
            UPDATE allergies
            SET result = coalesce(
                    (SELECT group_concat(c.item, ', ')
                     FROM codes c
                     WHERE allergies.score & c.code),
                     ''
                )
            WHERE task = 'list';
            """)
        print_query(query_1, filepath=sql_path / "solution_1.sql") 
        query_2 = dedent("""\
            WITH codes(item, code) AS (
                VALUES
                    ('eggs', 1), ('peanuts', 2), ('shellfish', 4), ('strawberries', 8),
                    ('tomatoes', 16), ('chocolate', 32), ('pollen', 64), ('cats', 128)
            )
            UPDATE allergies
            SET result = CASE task
                    WHEN 'allergicTo' THEN
                        CASE WHEN score & c.code THEN 'true' ELSE 'false' END
                    ELSE coalesce(
                            (SELECT group_concat(codes.item, ', ')
                             FROM codes
                             WHERE score & codes.code),
                            ''
                        )
                END
            FROM codes c
            WHERE (task, allergies.item) = ('allergicTo', c.item) OR task = 'list';
            """)
        print_query(query_2, filepath=sql_path / "solution_2.sql")   
        query_3 = dedent("""\
            WITH
                codes(item, code) AS (
                    VALUES
                        ('eggs', 1), ('peanuts', 2), ('shellfish', 4), ('strawberries', 8),
                        ('tomatoes', 16), ('chocolate', 32), ('pollen', 64), ('cats', 128)
                ),
                results(score, result) AS (
                    SELECT score, group_concat(codes.item, ', ')
                    FROM (SELECT DISTINCT score FROM allergies WHERE task = 'list'), codes
                    WHERE score & code
                    GROUP BY score
                    UNION SELECT 0, ''
                )
            UPDATE allergies
            SET result = CASE task
                    WHEN 'allergicTo' THEN
                        CASE WHEN allergies.score & c.code THEN 'true' ELSE 'false' END
                    ELSE r.result
                END
            FROM codes c, results r
            WHERE
                (task, allergies.item) = ('allergicTo', c.item)
                OR (task, allergies.score) = ('list', r.score);
            """)
        print_query(query_3, filepath=sql_path / "solution_3.sql")   
        con.executescript(query_3)
        query = "SELECT * FROM allergies;"
        res = con.execute(query)
        pprint(res.fetchall())


#allergies()


def two_fer():
    """Exercism SQLite path exercise 10, Two-Fer:
    https://exercism.org/tracks/sqlite/exercises/two-fer"""

    sql_path = SQL_PATH / "Two-Fer"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE twofer (input TEXT, response TEXT);
            INSERT INTO twofer (input)
                VALUES (''), ('Alice'), ('Bob');
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
            UPDATE twofer
            SET response =
                'One for ' || coalesce(nullif(input, ''), 'you') || ', one for me.';
            """)
        print_query(query, filepath=sql_path / "solution.sql")        
        con.execute(query)
        query = "SELECT * FROM twofer;"
        res = con.execute(query)
        pprint(res.fetchall())


#two_fer()


def resistor_color_duo():
    """Exercism SQLite path exercise 9, Resistor Color Duo:
    https://exercism.org/tracks/sqlite/exercises/resistor-color-duo"""

    sql_path = SQL_PATH / "Resistor-Color-Duo"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE color_code (color1 TEXT, color2 TEXT, result INT);
            INSERT INTO color_code (color1, color2)
                VALUES
                    ('brown', 'black'),
                    ('blue', 'grey'),
                    ('yellow', 'violet'),
                    ('white', 'red'),
                    ('orange', 'orange'),
                    ('black', 'brown');
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
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
            SET result = c1.code || c2.code
            FROM coding c1, coding c2
            WHERE (color1, color2) = (c1.color, c2.color);
            """)
        print_query(query, filepath=sql_path / "solution.sql")        
        con.execute(query)
        query = "SELECT * FROM color_code;"
        res = con.execute(query)
        pprint(res.fetchall())


#resistor_color_duo()


def resistor_color():
    """Exercism SQLite path exercise 8, Resistor Color:
    https://exercism.org/tracks/sqlite/exercises/resistor-color"""

    sql_path = SQL_PATH / "Resistor-Color"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE color_code (color TEXT, result INT);
            INSERT INTO color_code (color)
                VALUES ('black'), ('white'), ('orange');
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
            UPDATE color_code
            SET result = CASE color
                    WHEN 'black'  THEN 0
                    WHEN 'brown'  THEN 1
                    WHEN 'red'    THEN 2
                    WHEN 'orange' THEN 3
                    WHEN 'yellow' THEN 4
                    WHEN 'green'  THEN 5
                    WHEN 'blue'   THEN 6
                    WHEN 'violet' THEN 7
                    WHEN 'grey'   THEN 8
                    WHEN 'white'  THEN 9
                END;
            """)
        print_query(query, filepath=sql_path / "solution_1.sql")
        query = dedent("""\
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
            SET result = coding.code
            FROM coding
            WHERE color_code.color = coding.color;
            """)
        print_query(query, filepath=sql_path / "solution_2.sql")        
        con.execute(query)
        query = "SELECT * FROM color_code;"
        res = con.execute(query)
        pprint(res.fetchall())


#resistor_color()


def raindrops():
    """Exercism SQLite path exercise 7, Raindrops:
    https://exercism.org/tracks/sqlite/exercises/raindrops"""

    sql_path = SQL_PATH / "Raindrops"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE raindrops (number INT, sound TEXT);
            INSERT INTO raindrops (number)
                VALUES
                    (1),
                    (3),
                    (5),
                    (7),
                    (6),
                    (8),
                    (9),
                    (10),
                    (14),
                    (15),
                    (21),
                    (25),
                    (27),
                    (35),
                    (49),
                    (52),
                    (105),
                    (3125);
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
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
            """)
        print_query(query, filepath=sql_path / "solution.sql")
        con.execute(query)
        query = "SELECT * FROM raindrops;"
        res = con.execute(query)
        pprint(res.fetchall())


#raindrops()


def leap():
    """Exercism SQLite path exercise 6, Leap:
    https://exercism.org/tracks/sqlite/exercises/leap"""

    sql_path = SQL_PATH / "Leap"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE leap (year INT, is_leap BOOL);
            INSERT INTO leap (year)
                VALUES
                    (2015),
                    (1970),
                    (1996),
                    (1960),
                    (2100),
                    (1900),
                    (2000),
                    (2400),
                    (1800);
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
            UPDATE leap
            SET is_leap = CASE
                    WHEN year % 100 = 0 THEN year % 400 = 0
                    ELSE year % 4 = 0
                END;
            """)
        print_query(query, filepath=sql_path / "solution.sql")
        con.execute(query)
        query = "SELECT * FROM leap;"
        res = con.execute(query)
        pprint(res.fetchall())


#leap()


def grains():
    """Exercism SQLite path exercise 5, Grains:
    https://exercism.org/tracks/sqlite/exercises/grains"""

    sql_path = SQL_PATH / "Grains"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE grains (task TEXT, square INT, result INT);
            INSERT INTO grains (task, square)
                VALUES
                    ('single-square', 1),
                    ('single-square', 2),
                    ('single-square', 3),
                    ('single-square', 4),
                    ('single-square', 16),
                    ('single-square', 32),
                    ('single-square', 64),
                    ('total', 0);
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
            WITH RECURSIVE counts(square, grains) AS (
                SELECT 1, 1
                UNION ALL
                SELECT square + 1, grains * 2 FROM counts
                LIMIT 65
            )
            UPDATE grains
            SET result = CASE
                    WHEN task = 'single-square' THEN counts.grains
                    ELSE counts.grains - 1
                END
            FROM counts
            WHERE
                (grains.task = 'single-square' AND grains.square = counts.square)
                OR (grains.task = 'total' AND counts.square = 65);
            """)
        print_query(query, filepath=sql_path / "solution_with_rec.sql")
        query = dedent("""\
            UPDATE grains
            SET result = CASE task
                    WHEN 'single-square' THEN power(2, square - 1)
                    ELSE power(2, 64) - 1
                END;
            """)
        print_query(query, filepath=sql_path / "solution.sql")
        con.execute(query)
        query = "SELECT * FROM grains;"
        res = con.execute(query)
        pprint(res.fetchall())


#grains()


def gigasecond():
    """Exercism SQLite path exercise 4, Gigasecond:
    https://exercism.org/tracks/sqlite/exercises/gigasecond"""

    sql_path = SQL_PATH / "Gigasecond"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE gigasecond (moment TEXT, result TEXT);
            INSERT INTO gigasecond (moment)
                VALUES
                    ('2011-04-25'),
                    ('1977-06-13'),
                    ('1959-07-19'),
                    ('2015-01-24T22:00:00'),
                    ('2015-01-24T23:59:59');
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
            UPDATE gigasecond
            SET result = strftime('%Y-%m-%dT%H:%M:%S', moment, '1000000000 seconds');
            --SET result = strftime('%FT%T', moment, '1000000000 seconds');
            """)
        print_query(query, filepath=sql_path / "solution.sql")
        con.execute(query)
        query = "SELECT * FROM gigasecond;"
        res = con.execute(query)
        pprint(res.fetchall())


#gigasecond()


def difference_of_squares():
    """Exercism SQLite path exercise 3, Difference-of-Squares:
    https://exercism.org/tracks/sqlite/exercises/difference-of-squares"""

    sql_path = SQL_PATH / "Difference-of-Squares"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE "difference-of-squares"
                (number INT, property TEXT, result INT);
            INSERT INTO "difference-of-squares" (number, property)
                VALUES
                    (1, 'squareOfSum'),
                    (5, 'squareOfSum'),
                    (100, 'squareOfSum'),
                    (1, 'sumOfSquares'),
                    (5, 'sumOfSquares'),
                    (100, 'sumOfSquares'),
                    (1, 'differenceOfSquares'),
                    (5, 'differenceOfSquares'),
                    (100, 'differenceOfSquares');
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
            UPDATE "difference-of-squares"
            SET result =
                CASE
                    WHEN property = 'squareOfSum' THEN
                        number * number * (number + 1) * (number + 1) / 4
                    WHEN property = 'sumOfSquares' THEN
                        number * (number + 1) * (2 * number + 1) / 6
                    ELSE
                        number * number * (number + 1) * (number + 1) / 4
                        - number * (number + 1) * (2 * number + 1) / 6
                END;
            """)
        print_query(query, filepath=sql_path / "solution.sql")
        con.execute(query)
        query = '''SELECT * FROM "difference-of-squares";'''
        res = con.execute(query)
        pprint(res.fetchall())


#difference_of_squares()


def darts():
    """Exercism SQLite path exercise 2, Darts:
    https://exercism.org/tracks/sqlite/exercises/darts"""

    sql_path = SQL_PATH / "Darts"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        query = dedent("""
            CREATE TABLE darts (x REAL, y REAL, score INT);
            INSERT INTO darts (x, y)
                VALUES
                    (-9, 9),
                    (0, 10),
                    (-5, 0),
                    (0, -1),
                    (0, 0),
                    (-0.1, -0.1),
                    (0.7, 0.7),
                    (0.8, -0.8),
                    (-3.5, 3.5),
                    (-3.6, -3.6),
                    (-7.0, 7.0),
                    (7.1, -7.1),
                    (0.5, -4);
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
            UPDATE darts
            SET score = CASE
                            WHEN dist > 100 THEN 0
                            WHEN dist > 25 THEN 1
                            WHEN dist > 1 THEN 5
                            ELSE 10
                        END
            FROM (SELECT x, y, (x * x + y * y) AS dist FROM darts) as dists
            WHERE darts.x = dists.x AND darts.y = dists.y;
            """)
        print_query(query, filepath=sql_path / "solution.sql")
        con.execute(query)
        query = "SELECT * FROM darts;"
        res = con.execute(query)
        pprint(res.fetchall())


#darts()
