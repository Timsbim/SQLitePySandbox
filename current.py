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

DATA_PATH = Path("data/Misc/")
DATA_PATH.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_PATH / "chinook.db"
SQL_PATH = Path("sql/Misc/")
SQL_PATH.mkdir(parents=True, exist_ok=True)


# Experiments
 

with sqlite.connect(DB_PATH) as con:
    stmt = dedent("""\
        SELECT sql FROM sqlite_schema WHERE type = 'table';
        """)
    res = con.execute(stmt)
    for sql in res.fetchall():
        print(sql[0])


with sqlite.connect(":memory:") as con:
    stmt = dedent("""\
        CREATE TABLE foo (
            [id] INTEGER PRIMARY KEY NOT NULL,
            [bar] TEXT
        );
        INSERT INTO foo VALUES (1, 'foo'), (2, 'bar');
        """)
    con.executescript(stmt)
    stmt = dedent("""\
        SELECT id, bar FROM foo;
        """)
    pprint(con.execute(stmt).fetchall())

