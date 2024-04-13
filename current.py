from pathlib import Path
from pprint import pprint
from textwrap import dedent, indent
import sqlite3 as sqlite


def print_query(query, filename=None):
    """Print the query/ies formatted, and write to file if filename
    provided"""
    if isinstance(query, list):
        query = "\n\n".join(query)
    if filename is not None:
        (SQL_PATH / f"{filename}.sql").write_text(query)
    query = indent(query, "\t")
    print(f"Executing:\n\n{query}")


#DB_PATH = "ch03.db"
#DATA_PATH = "data/ch03"
SQL_PATH = Path("sql/")
SQL_PATH.mkdir(parents=True, exist_ok=True)


def difference_of_squares():
    with sqlite.connect(":memory:") as con:
        query = dedent("""\
            CREATE TABLE "difference-of-squares"
                (number INT, property TEXT, result INT);
            """)
        con.execute(query)
        query = dedent("""\
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
        con.execute(query)
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
        con.execute(query)
        query = '''SELECT * FROM "difference-of-squares";'''
        res = con.execute(query)
        pprint(res.fetchall())


#differences_of_squares()
