from dataclasses import dataclass
import sqlite3


def get_db_connection():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


def get_book_by_title(title):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE title = ?',
                        (title,)).fetchone()
    conn.close()
    return book


def get_book(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?',
                        (book_id,)).fetchone()
    conn.close()
    return book


def get_all_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return books


@dataclass
class Bok:
    """klasse som holder bok navn og antall"""

    navn: str
    antall: int


def SQL_to_csv(edit):
    return SQL_to_csv