from flask import Flask, render_template,request, jsonify
from flask_mysqldb import MySQL
import requests
import traceback
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'popcorn'
mysql = MySQL(app)

print('App started ...')

global theaters_data, date, day, time

# Replace 'your_api_endpoint' with the actual API endpoint URL
API_URL = "https://api.themoviedb.org/3/movie/upcoming/"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZGJjZDU4ZDY5MWMyZDk0ODdkZWNkZDNmODJmOWUxZCIsInN1YiI6IjY0YzFmMjdjZGY4NmE4MDBjOGU4Y2Y0OCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.OAG-Dd8prt9FMwnYIa2vVESIatI882HR1zhfBgzzLa8"  # Replace with your actual bearer token
global movies, movieTitle
movies = []
movieTitle = 'Oppenhiemer'


# Sample ticket prices (replace with actual prices)
ticket_prices = {
    'adult': 10,
    'child': 7,
    'senior': 8,
}



show_timing_json = app.root_path+'/data.json'
with open(show_timing_json, "r") as json_file:
    movie_schedule_dict = json.load(json_file)


# Path to the JSON data for movies file
json_file_path = os.path.join(app.root_path, 'static', 'json', 'show_timings.json')

def load_json_data(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

@app.route('/show-timings/<int:movie_id>')
def show_timings(movie_id):
    global theaters_data, date, day, time
    theaters_data = load_json_data(json_file_path)
    
    return render_template('show_timings.html', movie_id=movie_id, movie_data = theaters_data)


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


@app.route('/about_movie/<int:movie_id>')
def about_movie(movie_id):
    global movies, movieTitle
    try:
            API_URL = f"https://api.themoviedb.org/3/movie/{movie_id}"

            headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZGJjZDU4ZDY5MWMyZDk0ODdkZWNkZDNmODJmOWUxZCIsInN1YiI6IjY0YzFmMjdjZGY4NmE4MDBjOGU4Y2Y0OCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.OAG-Dd8prt9FMwnYIa2vVESIatI882HR1zhfBgzzLa8"
                        }
            response = requests.get(API_URL, headers=headers)
            movie_data = response.json()
            movieTitle = movie_data["title"]
        #print(data)
        # Check if 'data' is an array, or if the movie data is under a different property name
        #movies = data if isinstance(data, list) else data.get("movies", [])
            
            return render_template('about_movie.html', movie_data=movie_data)

    except Exception as e:
        traceback.print_exc()
        return f"Error fetching data: {e}"



@app.route('/order_tickets/<int:movie_id>/<string:movie_title>/<string:show_timings>/<string:date>/<string:day>', methods=['GET', 'POST'])
def order_tickets(movie_id, movie_title, show_timings, date,day):
    global movies, movieTitle

    # Retrieve movie details and show timings based on movie_id and show_timing
    # You would need to implement this based on your data structure

    if request.method == 'POST':
        # Get form data
        adult_tickets = int(request.form.get('adult_tickets',2))
        child_tickets = int(request.form.get('child_tickets',2))
        senior_tickets = int(request.form.get('senior_tickets',1))
        
        # Calculate total price
        total_price = (adult_tickets * ticket_prices['adult'] +
                      child_tickets * ticket_prices['child'] +
                      senior_tickets * ticket_prices['senior'])

        all_prices = [adult_tickets,child_tickets, senior_tickets, total_price]

        movie = find_movie_by_id(movie_id)
        print("movie", movie)
        summary_deatail = {
            'movie_title' : movieTitle,
            'movie_id' : movie_id,
            'timing': show_timings,
            'date' : date,
            'day': day,
            'adult_tickets' : adult_tickets,
            'child_tickets' : child_tickets,
            'senior_tickets' : senior_tickets,
            'adult_tickets_price' : ticket_prices['adult'],
            'child_tickets_price' : ticket_prices['child'],
            'senior_tickets_price' : ticket_prices['child'],
            'total_price' : total_price,
            'movie_image_path' : 'https://image.tmdb.org/t/p/original'+ movie["poster_path"]
        }



        return render_template('order_summary.html', summary=summary_deatail)
    
    return render_template('order_ticket.html', movie_id=movie_id,movie_title = movie_title, show_timings=show_timings, movie_data = movies,date=date, day=day, ticket_prices=ticket_prices)



@app.route('/place_order/<int:movie_id>/<string:date>/<string:day>/<string:show_timings>', methods=['GET', 'POST'])
def place_order(movie_id, date, day, show_timings):
    global movies, movieTitle

    # Retrieve movie details and show timings based on movie_id and show_timing
    # You would need to implement this based on your data structure
    if request.method == 'POST':
        # Calculate total price
        total_price = request.form.get('total')
        print('Heeloooooo total  ',total_price)
        movie = find_movie_by_id(movie_id)
        
        summary_deatail = {
            'movie_title' : movieTitle,
            'movie_id' : movie_id,
            'timing': show_timings,
            'date' : date,
            'day': day,
            'total_price' : total_price,
            'movie_image_path' : 'https://image.tmdb.org/t/p/original'+ movie["poster_path"]
        }

        return render_template('order_summary.html', summary=summary_deatail)
    return render_template('seat_selection.html', movie=movie, summary = summary_deatail)


@app.route('/seat_selection/<int:movie_id>/<string:date>/<string:day>/<string:show_timings>', methods=['GET', 'POST'])
def seat_selection(movie_id,date,day,show_timings):
    
    
    total = 45
    movie = find_movie_by_id(movie_id)
  
    summary_deatail = {
        'movie_title' : movie['original_title'],
        'movie_id' : movie_id,
        'timing': show_timings,
        'date' : date,
        'day': day,
        'total_price' : total,
        'movie_image_path' : 'https://image.tmdb.org/t/p/original'+ movie["poster_path"]
    }

    if request.method == 'POST': 
        total = request.form['total']
        summary_deatail['total_price'] = total
        print("Total From Form ", total)
        print("Total test ", summary_deatail)
        return render_template('order_summary.html',summary = summary_deatail)

    return render_template('seat_selection.html', summary = summary_deatail)



@app.route('/payment_success')
def payment_success():
    return render_template('payment_sucess.html')

def find_movie_by_id(movie_id):
    for movie in movies:
        if movie['id'] == movie_id:
            return movie
    return None

if __name__ == '__main__':
    app.run(debug=True)