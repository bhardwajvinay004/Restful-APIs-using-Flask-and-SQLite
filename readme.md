# IMDB_Task

This project was generated on 27th September, 2020.

## Development server

Run `python app.py` for a running the dev server. Navigate to `http://localhost:5000/`. The app will automatically reload if you change any of the source files.

## Create Schema adn Insert JSON data

To clean the SQLIte database, create a fresh schema and insert the JSON dump data; run `python jsonToSqlite.py`. This is create the fresh DB tables and insert the initial IMDB data.

## Fetch All the IMDB Movies details

To fetch all the movie's records, open `http://localhost:5000/movies` on dev server.

## Fetch a particular Movie details

To fetch the details of a particular Movie, open `http://localhost:5000/movies/{int:movie_id}` on dev server. Here movie_id is an ID associated with the movie in database table.

## Add a new Movie and it's details in the database

To add the details of a new Movie, open POSTMAN and request a POST API `http://localhost:5000/movies/add` on dev server with a JSON payload as a body and `Content-Type: application/json`. The payload format is shown below:

Payload:
{
  "name": "Python Flask API development",
  "director": "Vinay",
  "genre": ["Programmer", "Developer"],
  "imdb_score": "8.0",
  "popularity": "83.78"
}

## Update an existing Movie and it's details in the database

To update the details of an existing Movie, open POSTMAN and request a PUT API `http://localhost:5000/movies/{int:movie_id}` on dev server with a JSON payload as a body and `Content-Type: application/json`. The payload format is shown below:

Payload:
{
  "name": "Python Flask API development",
  "director": "Vinay",
  "genre": ["Programmer", "Developer"],
  "imdb_score": "8.3",
  "popularity": "83.78"
}

## Delete an existing Movie and it's details from the database

To delete the details of an existing Movie, open POSTMAN and request a DELETE API `http://localhost:5000/movies/{int:movie_id}` on dev server with the `Content-Type: application/json`.

## Fetch the Movie details based on different filters

To fetch the Movie details based on a filter applied, open `http://localhost:5000/movies?searchKey={field_name}&searchvalue={value_to_be_searched}` on dev server.
Here `searchKey` is the field name, which can be among the following:
  searchKey={name} i.e., Movie name or
  searchKey={director} or
  searchKey={genre} or
  searchKey={popularity} or
  searchKey={imdb_score}
And the searchValue for "popularity" and "imdb_score" should be a range. For example:
  searchValue={0-2} or
  searchValue={0.2-2.56} or
  searchValue={2-2} or

## Further details

Feel free to contact the developer in case of any queries.
