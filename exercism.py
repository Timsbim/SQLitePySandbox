from pathlib import Path
from pprint import pprint
from textwrap import dedent, indent
import csv
import sqlite3 as sqlite


print(f"\nSQLite version: {sqlite.sqlite_version}", end="\n\n")


# Helper functions


def print_stmt(stmt, filepath=None):
    """Print the stmt/ies formatted, and write to file if filename
    provided"""
    if isinstance(stmt, list):
        stmt = "\n\n".join(stmt)
    if filepath is not None:
        filepath.write_text(stmt)
    stmt = indent(stmt, "\t")
    print(f"Executing:\n\n{stmt}")


# Constants

DATA_PATH = Path("data/Exercsim/")
DATA_PATH.mkdir(parents=True, exist_ok=True)
SQL_PATH = Path("sql/Exercism/")
SQL_PATH.mkdir(parents=True, exist_ok=True)


# Exercism SQLite path exercises


def say():
    """Exercism SQLite path exercise Say:
    https://exercism.org/tracks/sqlite/exercises/Say"""
 
    exercise = "Say"
    data_path = DATA_PATH / exercise
    sql_path = SQL_PATH / exercise
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE say (
            	number 			INTEGER NOT NULL,
            	expected_result	TEXT,
              	expected_error 	TEXT,
            	result 			TEXT,
              	error  			TEXT
            );
            INSERT INTO say (number, expected_result, expected_error) VALUES
            	(0, 'zero', NULL),
                (1, 'one', NULL),
                (14, 'fourteen', NULL),
                (19, 'nineteen', NULL),
                (20, 'twenty', NULL),
                (22, 'twenty-two', NULL),
                (30, 'thirty', NULL),
                (99, 'ninety-nine', NULL),
                (100, 'one hundred', NULL),
                (123, 'one hundred twenty-three', NULL),
                (200, 'two hundred', NULL),
                (999, 'nine hundred ninety-nine', NULL),
                (1000, 'one thousand', NULL),
                (1234, 'one thousand two hundred thirty-four', NULL),
                (1000000, 'one million', NULL),
                (1002345, 'one million two thousand three hundred forty-five', NULL),
                (1000000000, 'one billion', NULL),
                (987654321123, 'nine hundred eighty-seven billion six hundred fifty-four million three hundred twenty-one thousand one hundred twenty-three', NULL),
                (-1, NULL, 'input out of range'),
                (1000000000000, NULL, 'input out of range');
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
            UPDATE say SET result = (
            	WITH words(n, word1, word2, word3) AS (
            		VALUES
                      (0, '',      'ten',       NULL),
                      (1, 'one',   'eleven',    NULL),
                      (2, 'two',   'twelve',    'twenty'),
                      (3, 'three', 'thirteen',  'thirty'),
                      (4, 'four',  'fourteen',  'forty'),
                      (5, 'five',  'fifteen',   'fifty'),
                      (6, 'six',   'sixteen',   'sixty'),
                      (7, 'seven', 'seventeen', 'seventy'),
                      (8, 'eight', 'eighteen',  'eighty'),
                      (9, 'nine',  'nineteen',  'ninety')
             	),
            	bs(b, rem, num) AS (
                	SELECT 0, number / 1000, number % 1000
                  	UNION
                  	SELECT b + 1, rem / 1000, rem % 1000 FROM bs WHERE rem > 0
                ),
              	ws(b, i, rem, d, word) AS (
                	SELECT b, 1, num / 10 - NOT num, num % 10, iif(number, NULL, 'zero')
                  	FROM bs
                  	UNION
                  	SELECT b, i + 1, rem / 10 - NOT rem, rem % 10, CASE
                 		   WHEN i = 1 AND rem % 10 = 1 THEN word2
                           WHEN i = 1 THEN word1
                           WHEN i = 2 AND d = 1 THEN word
                           WHEN i = 2 THEN word3 || iif(word != '', '-' || word, '')
                  		   ELSE word1 || ' hundred' || iif(word != '', ' ' || word, '')
                  		END
                  	FROM ws, words WHERE d = n AND rem >= 0
                ),
              	units(n, word) AS (
            		VALUES (0, ''), (1, ' thousand'), (2, ' million'), (3, ' billion')
                )
              	SELECT group_concat(ws.word || iif(ws.word != '', us.word, ''), ' ')
              	FROM (SELECT b, word FROM ws WHERE rem = -1 ORDER BY b DESC) ws,
                     (SELECT n, word FROM units ORDER BY n) us
                WHERE ws.b = us.n
            ) WHERE NOT error IS NOT NULL
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)

        stmt = """SELECT * FROM say WHERE result != expected_result;"""
        pprint(con.execute(stmt).fetchall())
 

#say()


def rest_api():
    """Exercism SQLite path exercise 19, REST API:
    https://exercism.org/tracks/sqlite/exercises/rest-api"""
 
    exercise = "REST-API"
    data_path = DATA_PATH / exercise
    sql_path = SQL_PATH / exercise
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE "rest-api" (database TEXT, payload TEXT, url TEXT, result TEXT);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path / "data.csv", "r") as file:
            con.executemany(
                """INSERT INTO "rest-api" VALUES(json(?), json(?), ?, ?);""",
                csv.reader(file, delimiter=";")
            )
        
        stmt = dedent("""\
            UPDATE "rest-api" SET result = CASE url
                WHEN '/users' THEN
                    (SELECT json_object('users', json_group_array(json(value)))
                     FROM (SELECT value, value ->> '$.name' AS name
                           FROM json_each(database, '$.users')
                           WHERE payload = '{}'
                                 OR name IN (SELECT value FROM json_each(payload, '$.users'))
                           ORDER BY name))
                WHEN '/add' THEN
                    json_object('name', payload ->> '$.user',
                                'owes', json('{}'),
                                'owed_by', json('{}'),
                                'balance', 0)
                WHEN '/iou' THEN (
                	WITH ds(n, m, v) AS (
                    	SELECT (us.value ->> '$.name') n, t.key m, iif(t.path GLOB '*.owes', -1, 1) * t.value
                        FROM json_each(database ->> '$.users') us, json_tree(us.value) t
                        WHERE n IN (payload ->> '$.lender', payload ->> '$.borrower')
                              AND m NOT IN ('name', 'balance') AND t.atom IS NOT NULL
                  		UNION ALL VALUES
                            ((payload ->> '$.lender'), (payload ->> '$.borrower'), (payload ->> '$.amount')),
                  			((payload ->> '$.borrower'), (payload ->> '$.lender'), -(payload ->> '$.amount'))
                    )
                  	SELECT json_object(
                        'users',
                        json_group_array(
                            json_object('name', n, 'owes', json(o), 'owed_by', json(ob), 'balance', b)
                        )
                    ) FROM (SELECT n,
                                   json_group_object(m, -v) FILTER (WHERE v < 0) o,
                                   json_group_object(m, v) FILTER (WHERE v > 0) ob,
                      		       sum(v) b
                      	    FROM (SELECT n, m, sum(v) v FROM ds GROUP BY n, m)
                            GROUP BY n)
            	)
            END
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
       
        pprint(con.execute("""SELECT * FROM "rest-api";""").fetchall())
 

#rest_api()


def tournament():
    """Exercism SQLite path exercise Tournament:
    https://exercism.org/tracks/sqlite/exercises/tournament"""
 
    exercise = "Tournament"
    data_path = DATA_PATH / exercise
    sql_path = SQL_PATH / exercise
    sql_path.mkdir(parents=True, exist_ok=True)
 
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE tournament ( input TEXT NOT NULL, result TEXT );
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        data = (data_path / "data.csv").read_text()
        stmt = f"""INSERT INTO tournament(input) VALUES('{data}');"""
        con.execute(stmt)

        stmt = dedent("""\
            UPDATE tournament SET result = (
                WITH cs(i, r, j, c) AS (
                    SELECT 2, 0, 0, substr(input, 1, 1)
                    UNION ALL
                    SELECT i + 1, r + (c = char(10)), (j + (c in (';', char(10)))) % 3, substr(input, i, 1)
                    FROM cs WHERE i <= length(input)
                ),
                ms(A, B, res) AS (
                    SELECT group_concat(c, '') FILTER (WHERE j = 0),
                           group_concat(c, '') FILTER (WHERE j = 1),
                           group_concat(c, '') FILTER (WHERE j = 2)
                    FROM cs WHERE c NOT in (';', char(10), '') GROUP BY r
                ),
                points(Team, P) AS (
                    SELECT A, CASE res WHEN 'win' THEN 3 WHEN 'draw' THEN 1 ELSE 0 END FROM ms
                    UNION ALL
                    SELECT B, CASE res WHEN 'win' THEN 0 WHEN 'draw' THEN 1 ELSE 3 END FROM ms
                ),
                results(Team, MP, W, D, L, P) AS (
                    SELECT Team,
                           count(*),
                           count(P) FILTER (WHERE P = 3),
                           count(P) FILTER (WHERE P = 1),
                           count(P) FILTER (WHERE P = 0),
                           sum(P)
                    FROM points GROUP BY Team
                ),
                rows(r) AS (
                    SELECT 'Team                           | MP |  W |  D |  L |  P'
                    UNION ALL
                    SELECT format('%-31s|% 3u |% 3u |% 3u |% 3u |% 3u', Team, MP, W, D, L, P)
                    FROM (SELECT * FROM results ORDER BY P DESC, Team)
                )
                SELECT group_concat(r, char(10)) FROM rows
            )
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
        
        res = con.execute("""SELECT * FROM tournament;""")
        pprint(res.fetchall())


#tournament()


def anagram():
    """Exercism SQLite path exercise Anagram:
    https://exercism.org/tracks/sqlite/exercises/anagram"""
 
    exercise = "Anagram"
    data_path = DATA_PATH / exercise
    sql_path = SQL_PATH / exercise
    sql_path.mkdir(parents=True, exist_ok=True)
 
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE anagram (
                subject    TEXT NOT NULL,
                candidates TEXT NOT NULL,  -- json array of strings
                result     TEXT            -- json array of strings
            );
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path / "data.csv", "r") as file:
            con.executemany(
                """INSERT INTO anagram(subject, candidates) VALUES(?, json(?));""",
                csv.reader(file, delimiter=";")
            )

        stmt = dedent("""\
            UPDATE anagram
            SET result = (
              	WITH tmp1(low, i, c) AS (
                	SELECT lower(subject), 2, substr(lower(subject), 1, 1)
                    UNION
                    SELECT low, i+1, substr(low, i, 1) FROM tmp1 WHERE i <= length(low)
                ),
                word(low, norm) AS (
                	SELECT low, group_concat(c, '')
                  	FROM (SELECT * FROM tmp1 ORDER BY c) GROUP BY low
                ),
              	tmp2(id, word, low, i, c) AS (
                	SELECT rowid, value, lower(value), 2, substr(lower(value), 1, 1)
                    FROM json_each(candidates)
                    UNION
                  	SELECT id, word, low, i+1, substr(low, i, 1) FROM tmp2 WHERE i <= length(word)
                ),
              	words(word, low, norm) AS (
                	SELECT word, low, group_concat(c, '')
                    FROM (SELECT * FROM tmp2 ORDER BY id, c) GROUP BY id
                )
            	SELECT json_group_array(word)
              	FROM words, word
                WHERE words.low != word.low AND words.norm = word.norm
            )
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
        
        res = con.execute("""SELECT * FROM anagram;""")
        pprint(res.fetchall())


#anagram()


def yacht():
    """Exercism SQLite path exercise 28, Yacht:
    https://exercism.org/tracks/sqlite/exercises/yacht"""
 
    data_path = DATA_PATH / "Yacht"
    sql_path = SQL_PATH / "Yacht"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        data_path = data_path / "data.csv"
        stmt = dedent("""\
            CREATE TABLE yacht (dice_results TEXT, category TEXT, result INT);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path, "r") as file:
            con.executemany(
                "INSERT INTO yacht(dice_results, category) VALUES(?, ?);",
                (row[:2] for row in csv.reader(file))
            )
        
        stmt = dedent("""\
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
                        WHEN 'full house' THEN
                            iif(group_concat(num, '') IN ('23', '32'), sum(score), 0)
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
        print_stmt(stmt, filepath=sql_path / "solution.sql")       
        con.execute(stmt)
        stmt = "SELECT * FROM yacht;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#yacht()


def roman_numerals():
    """Exercism SQLite path exercise 27, Roman Numerals:
    https://exercism.org/tracks/sqlite/exercises/roman-numerals"""

    exercise = "Roman-Numerals"
    data_path = DATA_PATH / exercise
    sql_path = SQL_PATH / exercise
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        data_path = data_path / "data.csv"
        stmt = dedent("""\
            CREATE TABLE "roman-numerals" (number INT, result TEXT);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path, "r") as file:
            con.executemany(
                """INSERT INTO "roman-numerals" (number, result) VALUES(?, ?);""",
                csv.reader(file)
            )

        stmt = dedent("""\
            WITH ns(i, n) AS (
            	VALUES (0, 'M'), (1, 'D'), (2, 'C'), (3, 'L'), (4, 'X'), (5, 'V'), (6, 'I')
            ),
            rms(n, i, d, r, p, rm) AS (
            	SELECT number, 0, number / 1000, number % 1000, 100, '' FROM "roman-numerals"
              	UNION
              	SELECT n, i + 2, r / p, r % p, p / 10,
                    CASE
                        WHEN d = 0 THEN ''
                        WHEN d < 4 THEN
                            printf('%.*c', d, (SELECT n FROM ns WHERE ns.i = rms.i))
                        WHEN d = 4 THEN
                            (SELECT n FROM ns WHERE ns.i = rms.i)
                              || (SELECT n FROM ns WHERE ns.i = rms.i - 1)
                        WHEN d = 5 THEN
                            (SELECT n FROM ns WHERE ns.i = rms.i - 1)
                        WHEN d < 9 THEN
                            (SELECT n FROM ns WHERE ns.i = rms.i - 1)
                              || printf('%.*c', d - 5, (SELECT n FROM ns WHERE ns.i = rms.i))
                        ELSE
                            (SELECT n FROM ns WHERE ns.i = rms.i)
                              || (SELECT n FROM ns WHERE ns.i = rms.i - 2)
                    END
              	FROM rms WHERE i < 8
            )
            UPDATE "roman-numerals"
            SET result = rm
            FROM (SELECT n, group_concat(rm, '') rm FROM rms GROUP BY n)
            WHERE number = n;
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")

        con.execute(stmt)
        stmt = """SELECT * FROM "roman-numerals";"""
        res = con.execute(stmt)
        pprint(res.fetchall())


#roman_numerals()


def pascals_triangle():
    """Exercism SQLite path exercise 26, Pascal's Triangle:
    https://exercism.org/tracks/sqlite/exercises/pascals-triangle"""

    exercise = "Pascals-Triangle"
    data_path = DATA_PATH / exercise
    sql_path = SQL_PATH / exercise
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        data_path = data_path / "data.csv"
        stmt = dedent("""\
            CREATE TABLE "pascals-triangle" (input INT, result TEXT);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path, "r") as file:
            con.executemany(
                """INSERT INTO "pascals-triangle"(input, result) VALUES(?, ?);""",
                csv.reader(file)
            )
        stmt = dedent("""\
            WITH arrays(row, ns) AS (
              	SELECT 1, '[1]'
              	UNION
              	SELECT row + 1,
                	   (SELECT json_group_array(n)
                        FROM (SELECT 1 n
                              UNION ALL
                              SELECT a.value + b.value n
                              FROM json_each(ns) a, json_each(ns) AS b
                              WHERE a.ROWID = b.ROWID - 1
                              UNION ALL
                              SELECT 1 n))
              	FROM arrays
              	LIMIT (SELECT max(input) FROM "pascals-triangle")
            ),
            rows(row, ns) AS (SELECT row, replace(trim(ns, '[]'), ',', ' ') FROM arrays)
            UPDATE "pascals-triangle"
            SET result = coalesce(trios.trio, '')
            FROM (SELECT input, group_concat(ns, char(10)) AS trio 
                  FROM "pascals-triangle" LEFT JOIN rows ON row <= input
                  GROUP BY input) trios
            WHERE "pascals-triangle".input = trios.input;
            """)
        print_stmt(stmt, filepath=sql_path / "solution_1.sql")        
        stmt = dedent("""\
            WITH rows(row, arr, ns) AS (
              	SELECT 1, '[1,1]', '1'
              	UNION
              	SELECT row + 1,
                	   (SELECT json_group_array(n)
                        FROM (SELECT 1 n
                              UNION ALL
                              SELECT a.value + b.value n
                              FROM json_each(arr) a, json_each(arr) AS b
                              WHERE a.ROWID = b.ROWID - 1
                              UNION ALL
                              SELECT 1 n)),
              			ns || char(10) || replace(trim(arr, '[]'), ',', ' ')
              	FROM rows
              	LIMIT (SELECT max(input) FROM "pascals-triangle")
            )
            UPDATE "pascals-triangle"
            SET result = coalesce(ns, '')
            FROM ("pascals-triangle" a LEFT JOIN rows ON row = input) trios
            WHERE "pascals-triangle".input = trios.input;
            """)
        print_stmt(stmt, filepath=sql_path / "solution_2.sql")
        con.execute(stmt)
        stmt = """SELECT * FROM "pascals-triangle";"""
        res = con.execute(stmt)
        pprint(res.fetchall())


#pascals_triangle()


def matching_brackets():
    """Exercism SQLite path exercise 25, Matching Brackets:
    https://exercism.org/tracks/sqlite/exercises/matching-brackets"""

    exercise = "Matching-Brackets"
    data_path = DATA_PATH / exercise
    sql_path = SQL_PATH / exercise
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        data_path = data_path / "data.csv"
        stmt = dedent("""\
            CREATE TABLE "matching-brackets" (input TEXT, result BOOLEAN);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path, "r") as file:
            con.executemany(
                """INSERT INTO "matching-brackets"(input) VALUES(?);""",
                (row[:1] for row in csv.reader(file))
            )

        stmt = dedent("""\
            WITH RECURSIVE stacks(input, pos, stack) AS (
                SELECT input, 1, "" FROM "matching-brackets"
                UNION ALL
                SELECT
                    input, pos + 1,
                    CASE substr(input, pos, 1)
                        WHEN stack = "X" THEN stack
                        WHEN "[" THEN "[" || stack
                        WHEN "{" THEN "{" || stack
                        WHEN "(" THEN "(" || stack
                        WHEN "]" THEN iif(substr(stack, 1, 1) = "[", substr(stack, 2), "X")
                        WHEN "}" THEN iif(substr(stack, 1, 1) = "{", substr(stack, 2), "X")
                        WHEN ")" THEN iif(substr(stack, 1, 1) = "(", substr(stack, 2), "X")
                        ELSE stack
                    END
                FROM stacks WHERE pos <= length(input)
            )
            UPDATE "matching-brackets"
            SET result = s.stack = ""
            FROM stacks AS s
            WHERE "matching-brackets".input = s.input AND s.pos = length(s.input) + 1;
            """)        
        print_stmt(stmt, filepath=sql_path / "solution_1.sql")

        stmt = dedent("""\
            UPDATE "matching-brackets"
            SET result = (
                WITH RECURSIVE stacks(pos, stack) AS (
                    SELECT 1, ""
                    UNION ALL
                    SELECT
                        pos + 1,
                        CASE substr(input, pos, 1)
                            WHEN stack = "X" THEN stack
                            WHEN "[" THEN "[" || stack
                            WHEN "{" THEN "{" || stack
                            WHEN "(" THEN "(" || stack
                            WHEN "]" THEN iif(substr(stack, 1, 1) = "[", substr(stack, 2), "X")
                            WHEN "}" THEN iif(substr(stack, 1, 1) = "{", substr(stack, 2), "X")
                            WHEN ")" THEN iif(substr(stack, 1, 1) = "(", substr(stack, 2), "X")
                            ELSE stack
                        END
                    FROM stacks WHERE pos <= length(input)
                )
                SELECT stack == "" FROM stacks WHERE pos = length(input) + 1
            )
            """)        
        print_stmt(stmt, filepath=sql_path / "solution_2.sql")
        con.execute(stmt)
        stmt = """SELECT * FROM "matching-brackets";"""
        res = con.execute(stmt)
        pprint(res.fetchall())
       

#matching_brackets()


def luhn():
    """Exercism SQLite path exercise 24, Luhn:
    https://exercism.org/tracks/sqlite/exercises/luhn"""
 
    data_path = DATA_PATH / "Luhn"
    sql_path = SQL_PATH / "Luhn"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        stmt = """CREATE TABLE luhn (value TEXT, result Boolean);""";
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path / "data.csv", "r") as file:
            con.executemany(
                "INSERT INTO luhn (value) VALUES (?)",
                (row[:1] for row in csv.reader(file))
            )
        
        stmt_1 = dedent("""\
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
        print_stmt(stmt_1, filepath=sql_path / "solution_1.sql")
        
        stmt_2 = dedent("""\
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
        print_stmt(stmt_2, filepath=sql_path / "solution_2.sql")
        con.executescript(stmt_2)
        stmt = "SELECT * FROM luhn;"
        res = con.execute(stmt)
        pprint(res.fetchall())
 
 
#luhn()


def isogram():
    """Exercism SQLite path exercise 23, Isogram:
    https://exercism.org/tracks/sqlite/exercises/isogram"""
 
    sql_path = SQL_PATH / "Isogram"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE isogram (phrase TEXT, is_isogram INT);
            INSERT INTO isogram (phrase)
                VALUES
                    (''), ('isogram'), ('eleven'), ('zzyzx'),
                    ('subdermatoglyphic'), ('Alphabet'), ('alphAbet'),
                    ('thumbscrew-japingly'), ('thumbscrew-jappingly'),
                    ('six-year-old'), ('Emily Jung Schwartzkopf'),
                    ('accentor'), ('angola'), ('up-to-date');
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
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
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.executescript(stmt)
        stmt = "SELECT * FROM isogram;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#isogram()


def high_scores():
    """Exercism SQLite path exercise 22, High Scores:
    https://exercism.org/tracks/sqlite/exercises/high-scores"""
 
    data_path = DATA_PATH / "High-Scores"
    sql_path = SQL_PATH / "High-Scores"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE scores (game_id TEXT, score INT);
            CREATE TABLE results (game_id TEXT, property TEXT, result TEXT);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
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
        
        stmt = dedent("""\
            CREATE TABLE base (game_id TEXT, property TEXT, score INT);
            INSERT INTO base
                SELECT game_id, property, score FROM scores RIGHT JOIN results USING (game_id);
            WITH scores_ns(game_id, n, score) AS (
                SELECT game_id, row_number() OVER (PARTITION BY game_id ORDER BY score DESC), score
                FROM base WHERE property = 'personalTopThree'
            ),
            res(game_id, property, result) AS (
                SELECT game_id, property,
                       CASE property
                            WHEN 'scores' THEN group_concat(score)
                            WHEN 'personalBest' THEN max(score)
                            ELSE score
                        END
                FROM base WHERE property IN ('scores', 'personalBest', 'latest')
                GROUP BY game_id HAVING ROWID = max(ROWID)
                UNION
                SELECT game_id, 'personalTopThree', group_concat(score) FILTER (WHERE n <= 3)
                FROM scores_ns
                GROUP BY game_id
            )
            UPDATE results
            SET result = res.result
            FROM res
            WHERE (results.game_id, results.property) = (res.game_id, res.property);
            DROP TABLE base;
            """)
        print_stmt(stmt, filepath=sql_path / "solution_1.sql")
        stmt = dedent("""\
            WITH scores_ns(game_id, n, score) AS (
                SELECT game_id, row_number() OVER (PARTITION BY game_id ORDER BY score DESC), score
                FROM scores
                WHERE game_id IN (
                    SELECT DISTINCT game_id FROM results WHERE property = 'personalTopThree'
                )
            ),
            res(game_id, property, result) AS (
                SELECT game_id, property,
                       CASE property
                            WHEN 'scores' THEN group_concat(score)
                            WHEN 'personalBest' THEN max(score)
                            ELSE score
                        END
                FROM scores RIGHT JOIN results USING (game_id)
                WHERE property IN ('scores', 'personalBest', 'latest')
                GROUP BY game_id HAVING scores.ROWID = max(scores.ROWID)
                UNION
                SELECT game_id, 'personalTopThree', group_concat(score) FILTER (WHERE n <= 3)
                FROM scores_ns
                GROUP BY game_id
            )
            UPDATE results
            SET result = res.result
            FROM res
            WHERE (results.game_id, results.property) = (res.game_id, res.property);
            """)
        print_stmt(stmt, filepath=sql_path / "solution_2.sql")
        con.executescript(stmt)
        stmt = "SELECT * FROM results;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#high_scores()


def collatz():
    """Exercism SQLite path exercise 21, Collatz Conjecture:
    https://exercism.org/tracks/sqlite/exercises/collatz-conjecture"""

    sql_path = SQL_PATH / "Collatz-Conjecture"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE collatz (number INTEGER, steps INTEGER);
            INSERT INTO collatz (number)
                VALUES (1), (16), (12), (1000000);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
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
        print_stmt(stmt, filepath=sql_path / "solution.sql")        
        con.execute(stmt)
        stmt = "SELECT * FROM collatz;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#collatz()


def armstrong_numbers():
    """Exercism SQLite path exercise 20, Armstrong Numbers:
    https://exercism.org/tracks/sqlite/exercises/armstrong-numbers"""
 
    sql_path = SQL_PATH / "Armstrong-Numbers"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE "armstrong-numbers" (number INT, result BOOLEAN);
            INSERT INTO "armstrong-numbers"(number)
               VALUES
                    (0), (5), (10), (153), (100), (9474), (9475),
                    (9926315), (9926314);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
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
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
        stmt = """SELECT * FROM "armstrong-numbers";"""
        res = con.execute(stmt)
        pprint(res.fetchall())


#armstrong_numbers()


def nucleotide_count():
    """Exercism SQLite path exercise 18, Nucleotide Count:
    https://exercism.org/tracks/sqlite/exercises/nucleotide-count"""

    data_path = DATA_PATH / "Nucleotide-Count"
    sql_path = SQL_PATH / "Nucleotide-Count"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE "nucleotide-count" (
                strand TEXT CHECK (NOT "strand" GLOB '*[^ACGT]*'),
                result TEXT
            );
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path / "data.csv", "r") as file:
            con.executemany(
                """INSERT INTO "nucleotide-count" (strand) VALUES (?);""",
                (row[:1] for row in csv.reader(file))
            )
        
        stmt_1 = dedent("""\
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
        print_stmt(stmt_1, filepath=sql_path / "solution_1.sql")       
        
        stmt_2 = dedent("""\
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
        print_stmt(stmt_2, filepath=sql_path / "solution_2.sql")
        
        stmt_3 = dedent("""\
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
        print_stmt(stmt_3, filepath=sql_path / "solution_3.sql")
        con.execute(stmt_3)
        stmt = """SELECT * FROM "nucleotide-count";"""
        res = con.execute(stmt)
        pprint(res.fetchall())
 
 
#nucleotide_count()


def meetup():
    """Exercism SQLite path exercise 17, Meetup:
    https://exercism.org/tracks/sqlite/exercises/meetup"""
    data_path = DATA_PATH / "Meetup"
    sql_path = SQL_PATH / "Meetup"
    sql_path.mkdir(parents=True, exist_ok=True)
 
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE meetup (
                year INTEGER,
                month INTEGER,
                week TEXT,
                dayofweek TEXT,
                result TEXT
            )
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path / "data.csv", "r") as file:
            con.executemany(
                dedent("""\
                INSERT INTO meetup(year, month, week, dayofweek)
                    VALUES(?, ?, ?, ?);
                """),
                (row[:4] for row in csv.reader(file))
            )
        
        stmt = dedent("""\
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
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
        stmt = "SELECT * FROM meetup;"
        res = con.execute(stmt)
        pprint(res.fetchall())
 

#meetup()


def kindergarten_garden():
    """Exercism SQLite path exercise 16, Kindergarten-Garden:
    https://exercism.org/tracks/sqlite/exercises/kindergarten-garden"""
   
    exercise = "Kindergarten-Garden"
    data_path = DATA_PATH / exercise
    sql_path = SQL_PATH / exercise
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        data_path = data_path / "data.csv"
        stmt = dedent("""\
            CREATE TABLE "kindergarten-garden" (diagram TEXT, student TEXT, result TEXT);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.txt")
        con.execute(stmt)
        with open(data_path, "r") as file:
            con.executemany(
                """INSERT INTO "kindergarten-garden"(diagram, student, result) VALUES(?, ?, ?);""",
                csv.reader(file)
            )
 
        stmt = dedent("""\
            WITH students(n, student) AS (
                VALUES (0, 'Alice'), (1, 'Bob'), (2, 'Charlie'), (3, 'David'),
                       (4, 'Eve'), (5, 'Fred'), (6, 'Ginny'), (7, 'Harriet'),
                       (8, 'Ileana'), (9, 'Joseph'), (10, 'Kincaid'), (11, 'Larry')
            ),
            plants(i, student, diagram, n, plant) AS (
                SELECT 0, s.student, diagram, 2 * n + 1, ''
                FROM "kindergarten-garden" kg, students s WHERE kg.student = s.student
                UNION
                SELECT i + 1, student, diagram,
                    CASE i WHEN 1 THEN n + length(diagram) / 2 ELSE n + 1 END,
                    plant || CASE i WHEN 0 THEN '' ELSE ',' END || CASE substr(diagram, n, 1)
                        WHEN 'G' THEN 'grass'
                        WHEN 'C' THEN 'clover'
                        WHEN 'R' THEN 'radishes'
                        ELSE 'violets'
                    END
                FROM plants WHERE i < 4
            )
            UPDATE "kindergarten-garden" AS kg
            SET result = p.plant
            FROM plants p
            WHERE kg.student = p.student AND kg.diagram = p.diagram AND p.i = 4;
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
       
        res = con.execute("""SELECT * FROM "kindergarten-garden";""")
        pprint(res.fetchall())


#kindergarten_garden()


def etl():
    """Exercism SQLite path exercise 15, ETL:
    https://exercism.org/tracks/sqlite/exercises/etl"""

    exercise = "ETL"
    data_path = DATA_PATH / exercise
    sql_path = SQL_PATH / exercise
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        data_path = data_path / "data.csv"
        stmt = dedent("""CREATE TABLE etl (input TEXT, result TEXT);""")
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path, "r") as file:
            con.executemany(
                """INSERT INTO etl(input, result) VALUES(?, ?);""",
                csv.reader(file)
            )

        stmt = dedent("""\
            WITH lists(input, points, list) AS (
                SELECT input, CAST(a.key AS INTEGER), a.value
                FROM etl, json_each(etl.input) AS a
            ),
            chars(input, letter, points) AS (
                SELECT input, lower(b.value), lists.points
                FROM lists, json_each(list) as b
                ORDER BY input, b.value
            ),
            results(input, result) AS (
                SELECT input, json_group_object(letter, points)
                FROM chars
                GROUP BY input
            )
            UPDATE etl
            SET result = results.result
            FROM results WHERE etl.input = results.input;
            """)
        print_stmt(stmt, filepath=sql_path / "solution_1.sql")
        
        stmt = dedent("""\
            UPDATE etl
            SET result = (
                WITH lists(points, list) AS (
                    SELECT CAST(key AS INTEGER), value
                    FROM json_each(input)
                ),
                chars(letter, points) AS (
                    SELECT lower(value), lists.points
                    FROM lists, json_each(list)
                    ORDER BY value
                )
                SELECT json_group_object(letter, points) FROM chars
            )
            """)
        print_stmt(stmt, filepath=sql_path / "solution_2.sql")        
        con.execute(stmt)
        stmt = """SELECT * FROM etl;"""
        res = con.execute(stmt)
        pprint(res.fetchall()) 


#etl()


def eliuds_eggs():
    """Exercism SQLite path exercise 14, Eliuds Eggs:
    https://exercism.org/tracks/sqlite/exercises/eliuds-eggs"""
 
    sql_path = SQL_PATH / "Eliuds-Eggs"
    sql_path.mkdir(parents=True, exist_ok=True)
   
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE "eliuds-eggs" (number INT, result INT);
            INSERT INTO "eliuds-eggs" (number)
                VALUES (0), (16), (89), (2000000000);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
            WITH counts(number, n, eggs) AS (
                SELECT number, number >> 1, number & 1 FROM "eliuds-eggs"
                UNION ALL
                SELECT number, n >> 1, eggs + (n & 1) FROM counts WHERE n > 0
            )
            UPDATE "eliuds-eggs"
            SET result = eggs
            FROM counts WHERE "eliuds-eggs".number = counts.number;
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
        stmt = """SELECT * FROM "eliuds-eggs";"""
        res = con.execute(stmt)
        pprint(res.fetchall())
 
 
#eliuds_eggs()


def bob():
    """Exercism SQLite path exercise 13, Bob:
    https://exercism.org/tracks/sqlite/exercises/bob"""
    data_path = DATA_PATH / "Bob"
    sql_path = SQL_PATH / "Bob"
    sql_path.mkdir(parents=True, exist_ok=True)
  
    with sqlite.connect(":memory:") as con:
        data_path = data_path / "data.csv"
        stmt = dedent("""CREATE TABLE bob (input TEXT, reply TEXT);""")
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path, "r") as file:
            con.executemany(
                "INSERT INTO bob(input) VALUES(?);",
                (row[:1] for row in csv.reader(file))
            )
        stmt = dedent("""\
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
            """)
        print_stmt(stmt, filepath=sql_path / "solution_1.sql")
        
        stmt = dedent("""\
            UPDATE bob
            SET reply = CASE
                    WHEN length(trim(input, ' \n\t')) = 0 THEN 'Fine. Be that way!'
                    WHEN rtrim(input, ' \n\t') GLOB '*[?]' THEN
                        iif(input GLOB '*[a-zA-Z]*' AND upper(input) = input,
                            'Calm down, I know what I''m doing!', 'Sure.')
                    WHEN input GLOB '*[a-zA-Z]*' AND upper(input) = input THEN
                        'Whoa, chill out!'
                    ELSE 'Whatever.'
                END;
            """)
        print_stmt(stmt, filepath=sql_path / "solution_2.sql")
        con.execute(stmt)
        stmt = "SELECT * FROM bob;"
        res = con.execute(stmt)
        pprint(res.fetchall())
 
 
#bob()


def allergies():
    """Exercism SQLite path exercise 12, Allergies:
    https://exercism.org/tracks/sqlite/exercises/allergies"""

    data_path = DATA_PATH / "Allergies"
    sql_path = SQL_PATH / "Allergies"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE allergies (
                task TEXT,
                item TEXT,
                score INT NOT NULL,
                result TEXT
            );
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path / "data.csv", "r") as file:
            con.executemany(
                "INSERT INTO allergies (task, item, score) VALUES(?, ?, ?)",
                (row[:3] for row in csv.reader(file))
            )
        
        stmt_1 = dedent("""\
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
        print_stmt(stmt_1, filepath=sql_path / "solution_1.sql") 
        
        stmt_2 = dedent("""\
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
        print_stmt(stmt_2, filepath=sql_path / "solution_2.sql")   
        
        stmt_3 = dedent("""\
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
        print_stmt(stmt_3, filepath=sql_path / "solution_3.sql")   
        con.executescript(stmt_3)
        stmt = "SELECT * FROM allergies;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#allergies()


def rna_transcription():
    """Exercism SQLite path exercise 11, RNA-Transcription:
    https://exercism.org/tracks/sqlite/exercises/rna-transcription"""

    exercise = "RNA-Transcription"
    data_path = DATA_PATH / exercise
    sql_path = SQL_PATH / exercise
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        data_path = data_path / "data.csv"
        stmt = dedent("""\
            CREATE TABLE "rna-transcription" (dna TEXT, result TEXT);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.execute(stmt)
        with open(data_path, "r") as file:
            con.executemany(
                """INSERT INTO "rna-transcription"(dna, result) VALUES(?, ?);""",
                csv.reader(file)
            )

        stmt = dedent("""\
            UPDATE "rna-transcription"
            SET result = replace(replace(replace(replace(replace(dna, 'A', 'U'), 'T', 'A'), 'G', 'X'), 'C', 'G'), 'X', 'C')
            """)
        print_stmt(stmt, filepath=sql_path / "solution_1.sql")

        stmt = dedent("""\
            WITH RECURSIVE comps(dna, comp, pos) AS (
                SELECT dna, "", 1 FROM "rna-transcription"
                UNION
                SELECT
                    dna,
                    comp || CASE substring(dna, pos, 1)
                        WHEN "G" THEN "C"
                        WHEN "C" THEN "G"
                        WHEN "T" THEN "A"
                        WHEN "A" THEN "U"
                    END,
                    pos + 1
                FROM comps
                WHERE pos <= length(dna) + 1
            )
            UPDATE "rna-transcription"
            SET result = comp
            FROM comps WHERE comps.dna = "rna-transcription".dna
            """)
        print_stmt(stmt, filepath=sql_path / "solution_2.sql")
        con.execute(stmt)
        stmt = """SELECT * FROM "rna-transcription";"""
        res = con.execute(stmt)
        pprint(res.fetchall())


#rna_transcription()


def resistor_color_duo():
    """Exercism SQLite path exercise 10, Resistor Color Duo:
    https://exercism.org/tracks/sqlite/exercises/resistor-color-duo"""

    sql_path = SQL_PATH / "Resistor-Color-Duo"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE color_code (color1 TEXT, color2 TEXT, result INT);
            INSERT INTO color_code (color1, color2)
                VALUES
                    ('brown', 'black'), ('blue', 'grey'), ('yellow', 'violet'),
                    ('white', 'red'), ('orange', 'orange'), ('black', 'brown');
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
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
        print_stmt(stmt, filepath=sql_path / "solution.sql")        
        con.execute(stmt)
        stmt = "SELECT * FROM color_code;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#resistor_color_duo()


def resistor_color():
    """Exercism SQLite path exercise 9, Resistor Color:
    https://exercism.org/tracks/sqlite/exercises/resistor-color"""

    sql_path = SQL_PATH / "Resistor-Color"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE color_code (color TEXT, result INT);
            INSERT INTO color_code (color)
                VALUES ('black'), ('white'), ('orange');
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
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
        print_stmt(stmt, filepath=sql_path / "solution_1.sql")
        
        stmt = dedent("""\
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
        print_stmt(stmt, filepath=sql_path / "solution_2.sql")        
        con.execute(stmt)
        stmt = "SELECT * FROM color_code;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#resistor_color()


def raindrops():
    """Exercism SQLite path exercise 8, Raindrops:
    https://exercism.org/tracks/sqlite/exercises/raindrops"""

    sql_path = SQL_PATH / "Raindrops"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE raindrops (number INT, sound TEXT);
            INSERT INTO raindrops (number)
                VALUES
                    (1), (3), (5), (7), (6), (8), (9), (10), (14), (15),
                    (21), (25), (27), (35), (49), (52), (105), (3125);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
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
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
        stmt = "SELECT * FROM raindrops;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#raindrops()


def leap():
    """Exercism SQLite path exercise 7, Leap:
    https://exercism.org/tracks/sqlite/exercises/leap"""

    sql_path = SQL_PATH / "Leap"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE leap (year INT, is_leap BOOL);
            INSERT INTO leap (year)
                VALUES
                    (2015), (1970), (1996), (1960), (2100),
                    (1900), (2000), (2400), (1800);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
            UPDATE leap
            SET is_leap = CASE
                    WHEN year % 100 = 0 THEN year % 400 = 0
                    ELSE year % 4 = 0
                END;
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
        stmt = "SELECT * FROM leap;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#leap()


def grains():
    """Exercism SQLite path exercise 6, Grains:
    https://exercism.org/tracks/sqlite/exercises/grains"""

    sql_path = SQL_PATH / "Grains"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE grains (task TEXT, square INT, result INT);
            INSERT INTO grains (task, square)
                VALUES
                    ('single-square', 1), ('single-square', 2),
                    ('single-square', 3), ('single-square', 4),
                    ('single-square', 16), ('single-square', 32),
                    ('single-square', 64), ('total', 0);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
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
        print_stmt(stmt, filepath=sql_path / "solution_with_rec.sql")
        
        stmt = dedent("""\
            UPDATE grains
            SET result = CASE task
                    WHEN 'single-square' THEN power(2, square - 1)
                    ELSE power(2, 64) - 1
                END;
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
        stmt = "SELECT * FROM grains;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#grains()


def gigasecond():
    """Exercism SQLite path exercise 5, Gigasecond:
    https://exercism.org/tracks/sqlite/exercises/gigasecond"""

    sql_path = SQL_PATH / "Gigasecond"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE gigasecond (moment TEXT, result TEXT);
            INSERT INTO gigasecond (moment)
                VALUES
                    ('2011-04-25'), ('1977-06-13'), ('1959-07-19'),
                    ('2015-01-24T22:00:00'), ('2015-01-24T23:59:59');
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
            UPDATE gigasecond
            SET result = strftime('%Y-%m-%dT%H:%M:%S', moment, '1000000000 seconds');
            --SET result = strftime('%FT%T', moment, '1000000000 seconds');
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
        stmt = "SELECT * FROM gigasecond;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#gigasecond()


def difference_of_squares():
    """Exercism SQLite path exercise 4, Difference-of-Squares:
    https://exercism.org/tracks/sqlite/exercises/difference-of-squares"""

    sql_path = SQL_PATH / "Difference-of-Squares"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
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
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
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
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
        stmt = '''SELECT * FROM "difference-of-squares";'''
        res = con.execute(stmt)
        pprint(res.fetchall())


#difference_of_squares()


def darts():
    """Exercism SQLite path exercise 3, Darts:
    https://exercism.org/tracks/sqlite/exercises/darts"""

    sql_path = SQL_PATH / "Darts"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""
            CREATE TABLE darts (x REAL, y REAL, score INT);
            INSERT INTO darts (x, y)
                VALUES
                    (-9, 9), (0, 10), (-5, 0), (0, -1), (0, 0), (-0.1, -0.1),
                    (0.7, 0.7), (0.8, -0.8), (-3.5, 3.5), (-3.6, -3.6),
                    (-7.0, 7.0), (7.1, -7.1), (0.5, -4);
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
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
        print_stmt(stmt, filepath=sql_path / "solution.sql")
        con.execute(stmt)
        stmt = "SELECT * FROM darts;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#darts()


def two_fer():
    """Exercism SQLite path exercise 2, Two-Fer:
    https://exercism.org/tracks/sqlite/exercises/two-fer"""

    sql_path = SQL_PATH / "Two-Fer"
    sql_path.mkdir(parents=True, exist_ok=True)
    
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE twofer (input TEXT, response TEXT);
            INSERT INTO twofer (input)
                VALUES (''), ('Alice'), ('Bob');
            """)
        print_stmt(stmt, filepath=sql_path / "build_table.sql")
        con.executescript(stmt)
        
        stmt = dedent("""\
            UPDATE twofer
            SET response =
                'One for ' || coalesce(nullif(input, ''), 'you') || ', one for me.';
            """)
        print_stmt(stmt, filepath=sql_path / "solution.sql")        
        con.execute(stmt)
        stmt = "SELECT * FROM twofer;"
        res = con.execute(stmt)
        pprint(res.fetchall())


#two_fer()