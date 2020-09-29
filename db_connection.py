import sqlite3

def get_db_connection():
  """ This method is used to establish a connection with SQLite database.
      Returns:
        [sqlite3.Connection]: returns the sqlite3 connection object
  """
  conn = sqlite3.connect('imdb.db')
  return conn
