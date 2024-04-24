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

DATA_PATH = Path("data/Experiments/")
DATA_PATH.mkdir(parents=True, exist_ok=True)
SQL_PATH = Path("sql/Experiments/")
SQL_PATH.mkdir(parents=True, exist_ok=True)


# Experiments
 
 
