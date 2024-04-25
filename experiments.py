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

DATA_PATH = Path("data/Experiments/")
DATA_PATH.mkdir(parents=True, exist_ok=True)
SQL_PATH = Path("sql/Experiments/")
SQL_PATH.mkdir(parents=True, exist_ok=True)


# Experiments


def test_over_partition():
    with sqlite.connect(":memory:") as con:
        stmt = dedent("""\
            CREATE TABLE test (id INT, part INT, value INT);
            INSERT INTO test
                VALUES (1, 1, 2), (2, 1, 1), (3, 2, 3), (4, 2, 1), (5, 2, 2);
            """)
        Path("part1.sql").write_text(stmt)
        con.executescript(stmt)
        #pprint(con.execute("SELECT * FROM test;").fetchall())
        stmt = dedent("""\
            SELECT id,
                   part,
                   row_number() OVER(PARTITION BY part ORDER BY value),
                   row_number() OVER(PARTITION BY part),
                   value
            FROM test;
            """)
        Path("part2.sql").write_text(stmt)
        #print("\n".join(map(repr, con.execute(stmt).fetchall())))
        stmt = dedent("""\
            SELECT id,
                   part,
                   row_number() OVER(PARTITION BY part),
                   row_number() OVER(PARTITION BY part ORDER BY value),
                   value
            FROM test;
            """)
        Path("part3.sql").write_text(stmt)
        #print("\n".join(map(repr, con.execute(stmt).fetchall())))


test_over_partition()
