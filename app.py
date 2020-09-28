""" app.py file
This is main application file to be executed to run the application.
"""
from flask import Flask, request, jsonify
import re
from db_connection import get_db_connection
import queries as q

app = Flask(__name__)
app.config["DEBUG"] = True

"""This is the route to the Home page of the Flask application.
Simply welcomes the user on the application.
Returns:
    [str]: renders the HTML h1 tag with a mesage.
"""
@app.route('/', methods=['GET'])
def home():
  if len(request.args.to_dict()):
    return '<h1> Please remove query parameter(s) and try again. </h1>', 400

  return '<h1> Welcome to IMDB Task Flask Application !! </h1>', 200


"""This is a common function to retrieve the searched records from the database tables.
Returns:
    [list]: returns the list of records fetched from the db tables.
"""
def generateSearchResult(movie_details, cur):
  result = []
  for movie in movie_details:
    tmpDict = {}
    tmpDict['id'] = movie[0]
    tmpDict['name'] = movie[1]
    tmpDict['imdb_score'] = movie[2]
    tmpDict['popularity'] = movie[3]
    tmpDict['genre'] = []

    director_name = cur.execute(q.GET_DIRECTOR_NAME_BY_ID, (movie[4],)).fetchone()
    tmpDict['director'] = director_name[0]

    genre_ids = cur.execute(q.GET_GENRE_IDS_BY_MOVIE_ID, (movie[0],)).fetchall()
    flat_list_genre_ids = [id for sublist in genre_ids for id in sublist]
    genre_names = cur.execute(q.GET_GENRE_NAMES_BY_IDS.format(', '.join('?' for _ in flat_list_genre_ids)), flat_list_genre_ids).fetchall()
    tmpDict['genre'] = [name for sublist in genre_names for name in sublist]

    result.append(tmpDict)

  return result


"""Fetches all the movies and their details completed.
Returns:
    [list]: returns the json list of records fetched from the db tables.
"""
def fetchAll():
  conn = get_db_connection()
  cur = conn.cursor()
  result = None
  movie_details = None

  movie_details = cur.execute(q.GET_ALL_FROM_MOVIE).fetchall()

  result = generateSearchResult(movie_details, cur)
  conn.close()
  return jsonify(result)


"""This is a common function to fetch the details of the searched field with exact match.
Returns:
    [list]: returns the json list of records fetched from the db tables.
"""
def searchByExactValue(key, value):
  conn = get_db_connection()
  cur = conn.cursor()
  result = None
  movie_details = None

  if key == 'movie_id':
    movie_details = cur.execute(q.GET_MOVIE_DETAILS_BY_MOVIE_ID, (value,)).fetchall()
  elif key == 'name':
    movie_details = cur.execute(q.GET_ALL_FROM_MOVIE_BY_NAME, (value,)).fetchall()
  elif key == 'genre':
    genre_id = cur.execute(q.GET_GENRE_ID_BY_NAME, (value,)).fetchone()
    if genre_id != None:
      movie_ids = cur.execute(q.GET_MOVIE_IDS_BY_GENRE_ID, (genre_id[0],)).fetchall()
      flat_list_movie_ids = [id for sublist in movie_ids for id in sublist]
      movie_details = cur.execute(q.GET_ALL_FROM_MOVIE_BY_MOVIE_IDS.format(', '.join('?' for _ in flat_list_movie_ids)), flat_list_movie_ids).fetchall()
    else:
      return jsonify([])
  elif key == 'director':
    director_id = cur.execute(q.GET_DIRECTOR_ID_BY_NAME, (value,)).fetchone()
    if director_id != None:
      movie_details = cur.execute(q.GET_ALL_FROM_MOVIE_BY_DIRECTOR_ID, (director_id[0],)).fetchall()
    else:
      return jsonify([])

  result = generateSearchResult(movie_details, cur)
  conn.close()
  return jsonify(result)


"""This is a common function to fetch the details of the searched field
between a range of values (integer or float).
Returns:
    [list]: returns the json list of records fetched from the db tables.
"""
def searchByRange(key, start, end):
  conn = get_db_connection()
  cur = conn.cursor()
  result = None
  movie_details = None

  if key == 'imdb_score':
    movie_details = cur.execute(q.GET_ALL_FROM_MOVIE_BY_SCORE, (start, end)).fetchall()
  elif key == 'popularity':
    movie_details = cur.execute(q.GET_ALL_FROM_MOVIE_BY_POPULARITY, (start, end)).fetchall()

  result = generateSearchResult(movie_details, cur)
  conn.close()
  return jsonify(result)


"""This function route provides the ability to search from the IMDB data
through Query Parameter filter options.
Returns:
    [list or string]: returns the json list of records fetched from the db tables
    or displays the HTML tag with some message.
"""
@app.route('/movies', methods=['GET'])
@app.route('/movies/', methods=['GET'])
def get_movies():
  query_params = request.args.to_dict()

  if len(query_params):
    keys = set(query_params.keys())

    if 'searchKey' in keys and 'searchValue' in keys:
      param_list = list(query_params.items())

      if param_list[0][1] == 'name' or param_list[0][1] == 'director' or param_list[0][1] == 'genre':
          return searchByExactValue(param_list[0][1], param_list[1][1]), 200
      elif param_list[0][1] == 'popularity' or param_list[0][1] == 'imdb_score':
        if re.search(r'^\d+(\.\d+)?-\d+(\.\d+)?$', param_list[1][1]):
          values = param_list[1][1].split('-')
          return searchByRange(param_list[0][1], float(values[0]), float(values[1])), 200
        else:
          return 'Provide the value in range format, something like 2-6.', 400
      else:
        return jsonify([]), 200
    else:
      return '<h1> Please either provide none or all the valid and required Query parameter(s). </h1>', 400
  else:
    return fetchAll(), 200


"""This function route provides an ability to view, update or delete an existing Movie Details.
It uses movie_id to refer to the record in the database.
Returns:
    [dict or string]: returns the API successful or failure response.
"""
@app.route('/movies/<int:movie_id>', methods=['GET', 'PUT', 'DELETE'])
def get_update_delete_movie(movie_id):
  if request.method == 'DELETE':
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(q.DELETE_MOVIE_ID_FROM_MOVIE_GENRE, (movie_id,))
    cur.execute(q.DELETE_MOVIE_BY_ID, (movie_id,))

    conn.commit()
    conn.close()

    return '', 204
  elif request.method == 'PUT':
    payload = request.get_json()
    try:
      if payload["name"] and payload["director"] and payload["genre"] and payload["imdb_score"] and payload["popularity"]:
        pass
      else:
        pass
    except Exception as e:
      return 'Bad or Incomplete request payload', 400

    conn = get_db_connection()
    cur = conn.cursor()

    get_movie_details = cur.execute(q.GET_IDS_FROM_MOVIE_BY_NAME, (payload["name"],)).fetchall()
    for m in get_movie_details:
      if m[0] != movie_id:
        get_director_name = cur.execute(q.GET_DIRECTOR_NAME_BY_ID, (m[1],)).fetchone()
        if get_director_name!= None and get_director_name[0] == payload["director"]:
          conn.close()
          return 'Data already exists for Movie <b>' + payload["name"] +  '</b> directed by <b>' + \
            payload["director"] + '</b>.', 400

    director_id = None
    genre_ids = []

    get_director = cur.execute(q.GET_DIRECTOR_ID_BY_NAME, (payload["director"],)).fetchone()
    if get_director != None:
      director_id = get_director[0]
    else:
      cur.execute(q.INSERT_NEW_DIRECTOR_NAME, (payload["director"],))
      get_director = cur.execute(q.GET_DIRECTOR_ID_BY_NAME, (payload["director"],)).fetchone()
      director_id = get_director[0]

    cur.execute(q.UPDATE_FIELDS_IN_MOVIE, (payload["name"], payload["imdb_score"], payload["popularity"], director_id, movie_id))

    for genre in payload['genre']:
      get_genre = cur.execute(q.GET_GENRE_ID_BY_NAME, (genre,)).fetchone()
      if get_genre != None:
        genre_ids.append(get_genre[0])
      else:
        cur.execute("INSERT INTO GENRE (name) VALUES (?)", (genre,))
        get_genre = cur.execute(q.GET_GENRE_ID_BY_NAME, (genre,)).fetchone()
        genre_ids.append(get_genre[0])

    cur.execute(q.DELETE_MOVIE_ID_FROM_MOVIE_GENRE, (movie_id,))

    for genre_id in genre_ids:
      cur.execute(q.INSERT_INTO_MOVIE_GENRE, (movie_id, genre_id))

    conn.commit()
    conn.close()

    return jsonify({ "movie_id": movie_id, "message": "Successfully updated a movie." }), 200
  elif request.method == 'GET':
    return searchByExactValue('movie_id', movie_id), 200


"""This function route provides an ability to add a new movie and it's details into the database.
Returns:
    [dict or string]: returns the API successful or failure response.
"""
@app.route('/movies/add', methods=['POST'])
def add_new_movie():
  payload = request.get_json()
  try:
    if payload["name"] and payload["director"] and payload["genre"] and payload["imdb_score"] and payload["popularity"]:
      pass
    else:
      pass
  except Exception as e:
    return 'Bad or Incomplete request payload', 400

  conn = get_db_connection()
  cur = conn.cursor()

  get_movie_details = cur.execute(q.GET_DIRECTOR_ID_FROM_MOVIE, (payload["name"],)).fetchall()
  for m in get_movie_details:
    get_director_name = cur.execute(q.GET_DIRECTOR_NAME_BY_ID, (m[0],)).fetchone()
    if get_director_name != None and get_director_name[0] == payload["director"]:
      conn.close()
      return 'Data already exists for Movie <b>' + payload["name"] +  '</b> directed by <b>' + \
        payload["director"] + '</b>.', 400

  director_id = None
  movie_id = None
  genre_ids = []

  get_director = cur.execute(q.GET_DIRECTOR_ID_BY_NAME, (payload["director"],)).fetchone()
  if get_director != None:
    director_id = get_director[0]
  else:
    cur.execute(q.INSERT_NEW_DIRECTOR_NAME, (payload["director"],))
    get_director = cur.execute(q.GET_DIRECTOR_ID_BY_NAME, (payload["director"],)).fetchone()
    director_id = get_director[0]

  for genre in payload['genre']:
    get_genre = cur.execute(q.GET_GENRE_ID_BY_NAME, (genre,)).fetchone()
    if get_genre != None:
      genre_ids.append(get_genre[0])
    else:
      cur.execute("INSERT INTO GENRE (name) VALUES (?)", (genre,))
      get_genre = cur.execute(q.GET_GENRE_ID_BY_NAME, (genre,)).fetchone()
      genre_ids.append(get_genre[0])

  cur.execute(q.INSERT_NEW_MOVIE, (payload["name"], payload["imdb_score"], payload["popularity"], director_id))
  get_movie = cur.execute(q.GET_MOVIE_ID_BY_NAME_AND_DIRECTOR_ID, (payload["name"], director_id)).fetchone()
  movie_id = get_movie[0]

  for genre_id in genre_ids:
    cur.execute(q.INSERT_INTO_MOVIE_GENRE, (movie_id, genre_id))

  conn.commit()
  conn.close()

  return jsonify({ "movie_id": movie_id, "message": "Successfully added a new movie." }), 200


if __name__ == '__main__':
  # Threaded option to enable multiple instances for multiple user access support
  app.run(threaded=True, port=5000)
