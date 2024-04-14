from pathlib import Path
from pprint import pprint
from textwrap import dedent, indent
import sqlite3 as sqlite


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
            SET result = c1.code * 10 + c2.code
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
                VALUES
                    ('black'),
                    ('white'),
                    ('orange');
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
