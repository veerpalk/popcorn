from flask import Flask, abort, render_template,request,session, url_for,flash
from flask_mysqldb import MySQL
from flask import redirect
from flask_dance.contrib.google import make_google_blueprint, google
from flask import Flask, render_template,request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import requests
import traceback
import json
import bcrypt
import re
import os
from flask_mail import Mail, Message
import random
import string
import smtplib,ssl

app = Flask(__name__)

app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'popcorn'
mysql = MySQL(app)

# Configure Flask-Mail for sending emails
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] =  5000
app.config['MAIL_USE_TLS'] = False
#app.config['MAIL_USERNAME'] = 'your_username'
#app.config['MAIL_PASSWORD'] = 'your_password'

mail = Mail(app)



port = 587  # For starttls
smtp_server = "smtp.gmail.com"
sender_email = "himanusharma18@gmail.com"
receiver_email = "tapasyasangrai700@gmail.com"
password = 'hbozrccholqzcusf'







print('App started ...')

# Replace 'your_api_endpoint' with the actual API endpoint URL
API_URL = "https://api.themoviedb.org/3/movie/upcoming/"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZGJjZDU4ZDY5MWMyZDk0ODdkZWNkZDNmODJmOWUxZCIsInN1YiI6IjY0YzFmMjdjZGY4NmE4MDBjOGU4Y2Y0OCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.OAG-Dd8prt9FMwnYIa2vVESIatI882HR1zhfBgzzLa8"  # Replace with your actual bearer token
# Regular expression for password validation
#PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$")

global movies
movies = []
show_timing_json = app.root_path+'/data.json'
with open(show_timing_json, "r") as json_file:
    movie_schedule_dict = json.load(json_file)

##### Google login requirements #########    
GOOGLE_CLIENT_ID = "721590602279-ioe8de3us1fmipcjh86pl02e143ivm8m.apps.googleusercontent.com"
script_dir = os.path.dirname(__file__) 
script_dir=os.path.join(script_dir,'static')
script_dir=os.path.join(script_dir,'json')
client_secrets_file = os.path.join(script_dir, "client_secrets.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://localhost:5000/google/callback",

)
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper
# Route to start the Google Sign-In process
@app.route('/google/login')
def google_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    #print(authorization_url)
    return redirect(authorization_url)


# Callback route after successful Google Sign-In
@app.route('/google/callback')
def callback():
    
    flow.fetch_token(authorization_response=request.url)
    #print(request.url)
    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    print(credentials)
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    print(id_info)
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/")
    






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



@app.route('/login', methods=['GET', 'POST'])  
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        print('After encoding : ---- ',password)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
        user = cursor.fetchone()
        print(user)
        if user and bcrypt.checkpw(password, user[3].encode('utf-8')):
            #session['user_id'] = user[0]
            #session['username'] = user[1]
            return redirect('/')
        else:
            error = 'Invalid username or password.'
            return render_template('login_page.html', error=error)

    return render_template('login_page.html')



@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        confirm_password = request.form['confirm_password'].encode('utf-8')


        if password != confirm_password:
            error = "Passwords do not match."
            return render_template('signup.html', error=error)
        
          # Validate email format
        if not validate_email_format(email):
            error = "Invalid email format."
            return render_template('signup.html', error=error)
        
        # minimum length, uppercase letters, lowercase letters, numbers, and special characters.
        #if not PASSWORD_PATTERN.match(password):
        #    error = "Password must be at least 8 characters long"
        #    return render_template('signup.html', error=error)
    
        if len(username) < 3:
            error = "username must be at least 3 characters long"
            return render_template('signup.html', error=error)


        # # Check for unique username
        # if username in registered_usernames:
        #     error = "Username is already taken."
        #     return render_template('signup.html', error=error)

         # Hash the password
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # Store the user in the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name, password,email) VALUES (%s, %s,%s)",(username, hashed_password,email))

        
        
        
        mysql.connection.commit()

        # Here, you would typically perform database operations to store the user data.
        # For this example, we'll just print the data.
        print(f"Username: {username}, Email: {email}, Password: {password}")
        return redirect('login')
    return render_template('signup.html')

def validate_email_format(email):
      # Simple email format validation using a regular expression
         pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
         return re.match(pattern, email)
def check_email(email):
    try:
        # Sample route to test the database connection
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        result = cursor.fetchall()
        
        cursor.close()
        #mysql.connection.close()
        print(f"SQL Result: {result}")

        return result

    
    except Exception as e:
        # In case of any error, print the error message and return an error response
        print(f"Error: {e}")
      
        
def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        print(email)
        user = check_email(email)
        print("veera email")

        email=user[0][2]
        print(email)
        if user:
            reset_token = generate_token()
            print(reset_token)
            #user['reset_token'] = reset_token

            msg = Message('Password Reset', sender='tapasyasangrai700@gmail.com', recipients=[email])
            msg.body = f"Click the link to reset your password: {url_for('reset_password', token=reset_token,email=email,_external=True)}"
            print(msg,'-----------',msg.body)
            message = f"""\
            Subject:Password Reset

            {msg.body}."""
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, port) as server:
                server.ehlo()  
                server.starttls(context=context)
                server.ehlo()  
                server.login(sender_email, password)
                server.sendmail(sender_email, email, message)
            
            #mail.send(msg)

            flash('Password reset link sent to your email', 'success')
            return redirect('login_page.html')
        else:
            flash('Email address not found', 'error')

    return render_template('forgot_password.html')



@app.route('/reset/<token>/<email>', methods=['GET', 'POST'])
def reset_password(token,email):
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password == confirm_password:
            #user['reset_token'] = None
            # Update the user's password (replace with your database update)
            user = check_email(email)
            print(user)
            old_password=user[0][3]
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            req_user = cursor.fetchone()
            new_password=new_password.encode('utf-8')
            changed_password= bcrypt.hashpw(new_password, bcrypt.gensalt()) 
            cursor.execute("update users set password=%s where email=%s",(changed_password,email))
            mysql.connection.commit()
            flash('Password reset successful', 'success')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match', 'error')

    return render_template('reset_password.html')
@app.route('/logout', methods=['GET', 'POST'])  
def logout():
    return render_template("login_page.html")
if __name__ == '__main__':
    app.run(debug=True)

