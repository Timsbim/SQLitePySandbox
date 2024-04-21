from pathlib import Path
from pprint import pprint
from textwrap import dedent, indent
import csv
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

DATA_PATH = Path("data/Exercsim/")
DATA_PATH.mkdir(parents=True, exist_ok=True)
SQL_PATH = Path("sql/Exercism/")
SQL_PATH.mkdir(parents=True, exist_ok=True)


# Exercism SQLite path exercises


def yacht():
    """Exercism SQLite path exercise 21, Yacht:
    https://exercism.org/tracks/sqlite/exercises/yacht"""
 
    data_path = DATA_PATH / "Yacht"
    sql_path = SQL_PATH / "Yacht"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        data_path = data_path / "data.csv"
        query = dedent(f"""\
            CREATE TABLE yacht (dice_results TEXT, category TEXT, result INT);
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.execute(query)
        with open(data_path, "r") as file:
            con.executemany(
                "INSERT INTO yacht(dice_results, category) VALUES(?, ?);",
                (row[:2] for row in csv.reader(file))
            )
        query = dedent("""\
            WITH rolls(res, cat, p, roll) AS (
                SELECT dice_results, category, 4, CAST(substr(dice_results, 1, 1) AS INT) FROM yacht
                UNION ALL
                SELECT res, cat, p + 3, CAST(substr(res, p, 1) AS INT) FROM rolls WHERE p < 14
            ),
            groups(res, cat, roll, num, score) AS (
                SELECT res, cat, roll, count(roll), sum(roll) FROM rolls GROUP BY res, cat, roll
            ),
            results(res, cat, val) AS (
                SELECT
                    res,
                    cat,
                    CASE cat
                        WHEN 'ones' THEN ifnull(sum(score) FILTER (WHERE roll = 1), 0)
                        WHEN 'twos' THEN ifnull(sum(score) FILTER (WHERE roll = 2), 0)
                        WHEN 'threes' THEN ifnull(sum(score) FILTER (WHERE roll = 3), 0)
                        WHEN 'fours' THEN ifnull(sum(score) FILTER (WHERE roll = 4), 0)
                        WHEN 'fives' THEN ifnull(sum(score) FILTER (WHERE roll = 5), 0)
                        WHEN 'sixes' THEN ifnull(sum(score) FILTER (WHERE roll = 6), 0)
                        WHEN 'full house' THEN iif(group_concat(num, '') IN ('23', '32'), sum(score), 0)
                        WHEN 'four of a kind' THEN CASE num
                                WHEN 5 THEN score - roll
                                ELSE ifnull(sum(score) FILTER (WHERE num = 4), 0)
                            END
                        WHEN 'little straight' THEN iif(group_concat(roll, '') = '12345', 30, 0)
                        WHEN 'big straight' THEN iif(group_concat(roll, '') = '23456', 30, 0)
                        WHEN 'choice' THEN sum(score)
                        WHEN 'yacht' THEN iif(num = 5, 50, 0)
                   END
                FROM groups
                GROUP BY res, cat
                ORDER BY roll
            )
            UPDATE yacht
            SET result = val
            FROM results
            WHERE (yacht.dice_results, yacht.category) = (results.res, results.cat);
            """)
        print_query(query, filepath=sql_path / "solution.sql")       
        con.execute(query)
        query = "SELECT * FROM yacht;"
        res = con.execute(query)
        pprint(res.fetchall())


#yacht()


def high_scores():
    """Exercism SQLite path exercise 18, High Scores:
    https://exercism.org/tracks/sqlite/exercises/high-scores"""
 
    data_path = DATA_PATH / "High-Scores"
    sql_path = SQL_PATH / "High-Scores"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE scores (game_id TEXT, score INT);
            CREATE TABLE results (game_id TEXT, property TEXT, result TEXT);
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        with open(data_path / "scores.csv", "r") as file:
            con.executemany(
                "INSERT INTO scores VALUES(?, ?);",
                ((ID, int(score)) for ID, score in csv.reader(file))
            )
        with open(data_path / "results.csv", "r") as file:
            con.executemany(
                "INSERT INTO results(game_id, property) VALUES(?, ?);",
                (row[:2] for row in csv.reader(file))
            )
        query_1 = dedent("""\
            CREATE TABLE base (game_id TEXT, property TEXT, score INT);
            INSERT INTO base
                SELECT game_id, property, score FROM scores RIGHT JOIN results USING (game_id);
            WITH RECURSIVE part_1(game_id, property, result) AS (
                SELECT game_id, property, iif(property = 'scores', group_concat(score), max(score))
                FROM base WHERE property IN ('scores', 'personalBest')
                GROUP BY game_id, property
            ),
            scores_ns(game_id, n, score) AS (
                SELECT game_id, row_number() OVER (PARTITION BY game_id ORDER BY score DESC), score
                FROM base WHERE property = 'personalTopThree'
            ),
            part_2(game_id, property, result) AS (
                SELECT game_id, 'personalTopThree', group_concat(score) FILTER (WHERE n <= 3)
                FROM scores_ns
                GROUP BY game_id
                UNION SELECT * FROM part_1
            ),
            parts(game_id, property, result) AS (
                SELECT game_id, property, score FROM base WHERE property = 'latest'
                GROUP BY game_id HAVING ROWID = max(ROWID)
                UNION SELECT * FROM part_2
            )
            UPDATE results
            SET result = parts.result
            FROM parts
            WHERE (results.game_id, results.property) = (parts.game_id, parts.property);
            DROP TABLE base;
            """)
        print_query(query_1, filepath=sql_path / "solution_1.sql")
        query_2 = dedent("""\
            WITH part_1(game_id, property, result) AS (
                SELECT game_id, property, iif(property = 'scores', group_concat(score), max(score))
                FROM scores RIGHT JOIN results USING (game_id)
                WHERE property IN ('scores', 'personalBest')
                GROUP BY game_id, property
            ),
            scores_ns(game_id, n, score) AS (
                SELECT game_id, row_number() OVER (PARTITION BY game_id ORDER BY score DESC), score
                FROM scores
                WHERE game_id in (SELECT DISTINCT game_id FROM results WHERE property = 'personalTopThree')
            ),
            part_2(game_id, property, result) AS (
                SELECT game_id, 'personalTopThree', group_concat(score) FILTER (WHERE n <= 3)
                FROM scores_ns
                GROUP BY game_id
                UNION SELECT * FROM part_1
            ),
            parts(game_id, property, result) AS (
                SELECT game_id, 'latest', score FROM scores
                WHERE game_id in (SELECT DISTINCT game_id FROM results WHERE property = 'latest')
                GROUP BY game_id HAVING ROWID = max(ROWID)
                UNION SELECT * FROM part_2
            )
            UPDATE results
            SET result = parts.result
            FROM parts
            WHERE (results.game_id, results.property) = (parts.game_id, parts.property);
            """)
        print_query(query_2, filepath=sql_path / "solution_2.sql")
        con.executescript(query_2)
        query = "SELECT * FROM results;"
        res = con.execute(query)
        pprint(res.fetchall())


#high_scores()


def luhn():
    """Exercism SQLite path exercise 20, Luhn:
    https://exercism.org/tracks/sqlite/exercises/luhn"""
 
    data_path = DATA_PATH / "Luhn"
    sql_path = SQL_PATH / "Luhn"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        query = """CREATE TABLE luhn (value TEXT, result Boolean);""";
        print_query(query, filepath=sql_path / "build_table.sql")
        con.execute(query)
        with open(data_path / "data.csv", "r") as file:
            con.executemany(
                "INSERT INTO luhn (value) VALUES (?)",
                (row[:1] for row in csv.reader(file))
            )
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
            sums(value, clean, pos, switch, d, sum) AS (
                SELECT value, '0' || clean, length(clean) + 1, 1, 0, 0 FROM clean
                WHERE length(clean) > 1
                UNION ALL
                SELECT value, clean, pos - 1, switch * -1,
                       CAST(substr(clean, pos, 1) AS INTEGER),
                       sum + iif(switch > 0, iif(d < 5, 2 * d, 2 * d - 9), d)
                FROM sums
                WHERE pos > 0
            )
            UPDATE luhn
            SET result = sums.sum % 10 = 0
            FROM sums
            WHERE luhn.value = sums.value;
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
                    (''), ('isogram'), ('eleven'), ('zzyzx'),
                    ('subdermatoglyphic'), ('Alphabet'), ('alphAbet'),
                    ('thumbscrew-japingly'), ('thumbscrew-jappingly'),
                    ('six-year-old'), ('Emily Jung Schwartzkopf'),
                    ('accentor'), ('angola'), ('up-to-date');
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
        print_query(query, filepath=sql_path / "solution.sql")
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
                SELECT number, iif(n % 2, 3 * n + 1, n / 2), step + 1 FROM steps
                WHERE n != 1
            )
            UPDATE collatz
            SET steps = steps.step
            FROM steps 
            WHERE collatz.number = steps.number;
            """)
        print_query(query, filepath=sql_path / "solution.sql")        
        con.execute(query)
        query = "SELECT * FROM collatz;"
        res = con.execute(query)
        pprint(res.fetchall())


#collatz()


def armstrong_numbers():
    """Exercism SQLite path exercise 16, Armstrong Numbers:
    https://exercism.org/tracks/sqlite/exercises/armstrong-numbers"""
 
    sql_path = SQL_PATH / "Armstrong-Numbers"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE "armstrong-numbers" (number INT, result BOOLEAN);
            INSERT INTO "armstrong-numbers"(number)
               VALUES
                    (0), (5), (10), (153), (100), (9474), (9475),
                    (9926315), (9926314);
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
            WITH RECURSIVE sums(number, string, e, pos, sum) AS (
                SELECT number,
                       CAST(number AS TEXT),
                       length(CAST(number AS TEXT)),
                       0, 0
                FROM "armstrong-numbers"
                UNION ALL
                SELECT number, string, e,  pos + 1,
                       sum + power(CAST(substr(string, pos + 1, 1) AS INTEGER), e)
                FROM sums
                WHERE e >= pos
            )
            UPDATE "armstrong-numbers"
            SET result = sums.number = sums.sum
            FROM sums
            WHERE "armstrong-numbers".number = sums.number AND pos = e + 1;
            """)
        print_query(query, filepath=sql_path / "solution.sql")
        con.execute(query)
        query = """SELECT * FROM "armstrong-numbers";"""
        res = con.execute(query)
        pprint(res.fetchall())


#armstrong_numbers()


def nucleotide_count():
    """Exercism SQLite path exercise 15, Nucleotide Count:
    https://exercism.org/tracks/sqlite/exercises/nucleotide-count"""

    data_path = DATA_PATH / "Nucleotide-Count"
    sql_path = SQL_PATH / "Nucleotide-Count"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE "nucleotide-count" (
                strand TEXT CHECK (NOT "strand" GLOB '*[^ACGT]*'),
                result TEXT
            );
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.execute(query)
        with open(data_path / "data.csv", "r") as file:
            con.executemany(
                """INSERT INTO "nucleotide-count" (strand) VALUES (?);""",
                (row[:1] for row in csv.reader(file))
            )
        query_1 = dedent("""\
            WITH RECURSIVE counts(strand, pos, n) AS (
                SELECT strand, 1, json('{"A":0,"C":0,"G":0,"T":0}') FROM "nucleotide-count"
                UNION ALL
                SELECT
                    strand,
                    pos + 1,
                    CASE substr(strand, pos, 1)
                        WHEN 'A' THEN json_set(n, '$.A', (n ->> '$.A') + 1)
                        WHEN 'C' THEN json_set(n, '$.C', (n ->> '$.C') + 1)
                        WHEN 'G' THEN json_set(n, '$.G', (n ->> '$.G') + 1)
                        ELSE json_set(n, '$.T', (n ->> '$.T') + 1)
                    END
                FROM counts
                WHERE pos <= length(strand)
            )
            UPDATE "nucleotide-count"
            SET result = n
            FROM counts
            WHERE "nucleotide-count".strand = counts.strand
                  AND pos = length(counts.strand) + 1;
            """)
        print_query(query_1, filepath=sql_path / "solution_1.sql")       
        query_2 = dedent("""\
            WITH RECURSIVE counts(strand, pos, n, jstr) AS (
                SELECT strand, 2,
                       format('$.%s', substr(strand, 1, 1)),
                       json('{"A":0,"C":0,"G":0,"T":0}')
                FROM "nucleotide-count"
                UNION ALL
                SELECT strand, pos + 1,
                       format('$.%s', substr(strand, pos, 1)),
                       json_set(jstr, n, (jstr ->> n) + 1)
                FROM counts
                WHERE pos <= length(strand) + 1
            )
            UPDATE "nucleotide-count"
            SET result = jstr
            FROM counts
            WHERE "nucleotide-count".strand = counts.strand
                  AND pos = length(counts.strand) + 2;
            """)
        print_query(query_2, filepath=sql_path / "solution_2.sql")
        query_3 = dedent("""\
            WITH RECURSIVE counts(strand, pos, n, A, C, G, T) AS (
                SELECT strand, 2, substr(strand, 1, 1), 0, 0, 0, 0 FROM "nucleotide-count"
                UNION ALL
                SELECT strand, pos + 1, substr(strand, pos, 1),
                       iif(n = 'A', A + 1, A), iif(n = 'C', C + 1, C),
                       iif(n = 'G', G + 1, G), iif(n = 'T', T + 1, T)
                FROM counts
                WHERE pos <= length(strand) + 1
            )
            UPDATE "nucleotide-count"
            SET result = format('{"A":%i,"C":%i,"G":%i,"T":%i}', A, C, G, T)
            FROM counts
            WHERE "nucleotide-count".strand = counts.strand
                  AND pos = length(counts.strand) + 2;
            """)
        print_query(query_3, filepath=sql_path / "solution_3.sql")
        con.execute(query_3)
        query = """SELECT * FROM "nucleotide-count";"""
        res = con.execute(query)
        pprint(res.fetchall())
 
 
#nucleotide_count()


def eliuds_eggs():
    """Exercism SQLite path exercise 13, Eliuds Eggs:
    https://exercism.org/tracks/sqlite/exercises/eliuds-eggs"""
 
    sql_path = SQL_PATH / "Eliuds-Eggs"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE "eliuds-eggs" (number INT, result INT);
            INSERT INTO "eliuds-eggs" (number)
                VALUES (0), (16), (89), (2000000000);
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
            WITH counts(number, n, eggs) AS (
                SELECT number, number >> 1, number & 1 FROM "eliuds-eggs"
                UNION ALL
                SELECT number, n >> 1, eggs + (n & 1) FROM counts WHERE n > 0
            )
            UPDATE "eliuds-eggs"
            SET result = eggs
            FROM counts WHERE "eliuds-eggs".number = counts.number;
            """)
        print_query(query, filepath=sql_path / "solution.sql")
        con.execute(query)
        query = """SELECT * FROM "eliuds-eggs";"""
        res = con.execute(query)
        pprint(res.fetchall())
 
 
#eliuds_eggs()


def allergies():
    """Exercism SQLite path exercise 11, Allergies:
    https://exercism.org/tracks/sqlite/exercises/allergies"""

    data_path = DATA_PATH / "Allergies"
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
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.execute(query)
        with open(data_path / "data.csv", "r") as file:
            con.executemany(
                "INSERT INTO allergies (task, item, score) VALUES(?, ?, ?)",
                (row[:3] for row in csv.reader(file))
            )
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
                        ('eggs', 1), ('peanuts', 2), ('shellfish', 4),
                        ('strawberries', 8), ('tomatoes', 16),
                        ('chocolate', 32), ('pollen', 64), ('cats', 128)
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
                    ('brown', 'black'), ('blue', 'grey'), ('yellow', 'violet'),
                    ('white', 'red'), ('orange', 'orange'), ('black', 'brown');
            """)
        print_query(query, filepath=sql_path / "build_table.sql")
        con.executescript(query)
        query = dedent("""\
            WITH coding(color, code) AS (
                VALUES
                    ('black',  0), ('brown',  1), ('red',    2),
                    ('orange', 3), ('yellow', 4), ('green',  5),
                    ('blue',   6), ('violet', 7), ('grey',   8),
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
                    (1), (3), (5), (7), (6), (8), (9), (10), (14), (15),
                    (21), (25), (27), (35), (49), (52), (105), (3125);
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
                    (2015), (1970), (1996), (1960), (2100),
                    (1900), (2000), (2400), (1800);
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
                    ('single-square', 1), ('single-square', 2),
                    ('single-square', 3), ('single-square', 4),
                    ('single-square', 16), ('single-square', 32),
                    ('single-square', 64), ('total', 0);
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
                    ('2011-04-25'), ('1977-06-13'), ('1959-07-19'),
                    ('2015-01-24T22:00:00'), ('2015-01-24T23:59:59');
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
                    (1, 'squareOfSum'), (5, 'squareOfSum'),
                    (100, 'squareOfSum'), (1, 'sumOfSquares'),
                    (5, 'sumOfSquares'), (100, 'sumOfSquares'),
                    (1, 'differenceOfSquares'), (5, 'differenceOfSquares'),
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
                    (-9, 9), (0, 10), (-5, 0), (0, -1), (0, 0), (-0.1, -0.1),
                    (0.7, 0.7), (0.8, -0.8), (-3.5, 3.5), (-3.6, -3.6),
                    (-7.0, 7.0), (7.1, -7.1), (0.5, -4);
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
