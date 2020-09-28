"""This module is required to be used once for the first time,
to create the SQLIte database schema/tables and insert data into the tables from the JSON file
containing the IMDB data in JSON format.
"""
import json
from db_connection import get_db_connection
import queries as q

connection = get_db_connection()
"""Execute the scripts from the schema.sql file.
"""
with open('schema.sql') as f:
  connection.executescript(f.read())

cur = connection.cursor()

"""Load the JSON dump data here from the JSON file.
"""
data = json.load(open('imdb.json'))

"""Loop through the loaded JSON data to insert it into the tables created above.
"""
for movie in data:
  director_id = None
  movie_id = None
  genre_ids = []

  """Insert all the new Director name in DIRECTOR table.
  """
  get_director = cur.execute(q.GET_DIRECTOR_ID_BY_NAME, (movie["director"],)).fetchone()
  if get_director != None:
    director_id = get_director[0]
  else:
    cur.execute(q.INSERT_NEW_DIRECTOR_NAME, (movie["director"],))
    get_director = cur.execute(q.GET_DIRECTOR_ID_BY_NAME, (movie["director"],)).fetchone()
    director_id = get_director[0]

  """Insert all the new Genre in GENRE table.
  """
  for genre in movie['genre']:
    get_genre = cur.execute(q.GET_GENRE_ID_BY_NAME, (genre,)).fetchone()
    if get_genre != None:
      genre_ids.append(get_genre[0])
    else:
      cur.execute("INSERT INTO GENRE (name) VALUES (?)", (genre,))
      get_genre = cur.execute(q.GET_GENRE_ID_BY_NAME, (genre,)).fetchone()
      genre_ids.append(get_genre[0])

  """Insert all the movie's details in MOVIE table.
  """
  cur.execute(q.INSERT_NEW_MOVIE, (movie["name"], movie["imdb_score"], movie["99popularity"], director_id))
  get_movie = cur.execute(q.GET_MOVIE_ID_BY_NAME_AND_DIRECTOR_ID, (movie["name"], director_id)).fetchone()
  movie_id = get_movie[0]

  """Insert data in MOVIE_GENRE table considering the many-to-many relationship.
  """
  for genre_id in genre_ids:
    cur.execute(q.INSERT_INTO_MOVIE_GENRE, (movie_id, genre_id))

connection.commit()
connection.close()
