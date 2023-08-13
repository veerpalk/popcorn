from flask import Flask, render_template,request, jsonify
from flask_mysqldb import MySQL
import requests
import traceback
import json

app = Flask(__name__)

app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'popcorn'
mysql = MySQL(app)

print('App started ...')

# Replace 'your_api_endpoint' with the actual API endpoint URL
API_URL = "https://api.themoviedb.org/3/movie/upcoming/"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZGJjZDU4ZDY5MWMyZDk0ODdkZWNkZDNmODJmOWUxZCIsInN1YiI6IjY0YzFmMjdjZGY4NmE4MDBjOGU4Y2Y0OCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.OAG-Dd8prt9FMwnYIa2vVESIatI882HR1zhfBgzzLa8"  # Replace with your actual bearer token
global movies
movies = []
show_timing_json = app.root_path+'/data.json'
with open(show_timing_json, "r") as json_file:
    movie_schedule_dict = json.load(json_file)



@app.route('/users')
def users():
    try:
        # Sample route to test the database connection
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM USERS')
        result = cursor.fetchall()
        
        cursor.close()
        mysql.connection.close()
        print(f"SQL Result: {result}")

        return render_template('index.html', movies=movies, allMovies=allMovies, search_query=search_query)

    
    except Exception as e:
        # In case of any error, print the error message and return an error response
        print(f"Error: {e}")
       # return jsonify(error="Failed to fetch users."), 500
        return render_template('index.html', movies=movies, allMovies=allMovies, search_query=search_query)




@app.route('/')
def movie_list():
    global movies, allMovies
    try:
        search_query = request.args.get('search_query', '').lower()
        show_all = request.args.get('show_all', False)

        
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            # Add any other custom headers required by the API
        }
        response = requests.get(API_URL, headers=headers)
        data = response.json()
        # Check if 'data' is an array, or if the movie data is under a different property name
        # movies = data if isinstance(data, list) else data.get("movies", [])
        movies = data['results']
        allMovies = movies


        if search_query:
            movies = [movie for movie in movies if search_query in movie['title'].lower()]
        elif show_all:
            # If 'show_all' is True, display all movies
            # You can set the value of 'show_all' to True when the "All" button is clicked
            movies = data['results']
        
        return render_template('index.html', movies=movies, allMovies=allMovies, search_query=search_query)

    except Exception as e:
        traceback.print_exc()
        return f"Error fetching data: {e}"

        


@app.route('/movielisting')
def theater_list():
    try:
        API_URL = 'https://www.cineplex.com/api/v1/theatres?language=en-us&range=10&skip=0&take=10'
        response = requests.get(API_URL)
        data = response.json()
        theaters = data.get("data", [])
        #print(movies)
        print('\n\n\n')
        '''
        for theatre in theaters:
            for movie in movies:
                theatre['movie'] = movie
                theatre['movie']['show_timings'] = movie_schedule_dict
        '''
        #with open('C:\\Users\\rohan.nirmul\\Documents\\New folder\\Programming for big data\\project\\show_timing.json', "w") as json_file:
        #    json.dump(theaters, json_file)
        #    print('data dumped')
        
        return render_template('show_timing.html', theaters=theaters)

    except Exception as e:
        return f"Error fetching data: {e}"


@app.route('/book-ticket/<int:movie_id>')
def book_ticket(movie_id):
    # Here you can implement the logic for booking a ticket for the specified movie_id
    # For this example, we'll just display a simple message
    movie = next((movie for movie in movies if movie["id"] == movie_id), None)
    if movie:
        return f"Booking ticket for '{movie['title']}' (ID: {movie['id']})"
    else:
        return "Movie not found."

@app.route('/about_movie/<int:movie_id>')
def about_movie(movie_id):
    global movies
    try:
            API_URL = f"https://api.themoviedb.org/3/movie/{movie_id}"

            headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZGJjZDU4ZDY5MWMyZDk0ODdkZWNkZDNmODJmOWUxZCIsInN1YiI6IjY0YzFmMjdjZGY4NmE4MDBjOGU4Y2Y0OCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.OAG-Dd8prt9FMwnYIa2vVESIatI882HR1zhfBgzzLa8"
}
            response = requests.get(API_URL, headers=headers)
            movie_data = response.json()
        #print(data)
        # Check if 'data' is an array, or if the movie data is under a different property name
        #movies = data if isinstance(data, list) else data.get("movies", [])
            
            return render_template('about_movie.html', movie_data=movie_data)

    except Exception as e:
        traceback.print_exc()
        return f"Error fetching data: {e}"

if __name__ == '__main__':
    app.run(debug=True)





@app.route('/showtimings')
def theater_list():
    try:
        filename = 'static/json/show_timings.json'
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        theaters = data
        print('\n\n\n')
    
        
        return render_template('show_timing.html', theaters=theaters)

    except Exception as e:
        return f"Error fetching data: {e}"