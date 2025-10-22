from typing import List, Dict, Union
from .database_connection import DatabaseConnection

db = "data.db"

Book = Dict[str, Union[str, int]]

def create_db_table():
    with DatabaseConnection(db) as connection:
        cursor = connection.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS books(name text primary key, author text, read integer)")


def add_string_properties(name: str, author: str) -> None:
    with DatabaseConnection(db) as connection:
        cursor = connection.cursor()

        cursor.execute(f'INSERT INTO books VALUES(?, ?, 0)', (name, author))

    print("book added successfully")


def get_string_properties() -> List[Book]:
    with DatabaseConnection(db) as connection:
        cursor = connection.cursor()

        data = cursor.execute("SELECT * FROM books").fetchall()
        books = [
            {'name': title, 'author': author, 'read': read}
            for title, author, read in data
        ]
        print("Books:", books)

    return books


def delete_string_properties(name: str) -> None:
     with DatabaseConnection(db) as connection:
         cursor = connection.cursor()
         cursor.execute('Delete FROM books WHERE name = ?', (name,))

         if cursor.rowcount == 0:
             print("Book not found")
             return

     print("Book deleted")




