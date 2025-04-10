from flask import Flask, render_template, request, jsonify, redirect, session, url_for, flash
import requests
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash  

app = Flask(__name__)
app.secret_key = 'e231d9a33a6ec821cabbddac3af1facb'

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB = 'insta_detection'

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        return conn
    except Error as e:
        print(f"Database Connection Error: {e}")
        return None

@app.route("/")
def home():
    return render_template("index.html")

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('signup.html', message="Passwords do not match.")

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            if conn is None:
                return render_template('signup.html', message="Database connection failed.")

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return render_template('signup.html', message="Email already exists.")

            cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
            conn.commit()

            return render_template('signup.html', success=True)

        except Error as e:
            conn.rollback()
            return render_template('signup.html', message=f"Error: {str(e)}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('signup.html')

# Login Route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        message = None

        try:
            conn = get_db_connection()
            if conn is None:
                message = "Database connection failed."
            else:
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()

                if user and check_password_hash(user[0], password):
                    session['user'] = email
                    return redirect(url_for('analyze'))
                else:
                    message = "Invalid email or password."

        except Error as e:
            message = f"Error: {str(e)}"

        finally:
            if conn:
                conn.close()

        return render_template("login.html", message=message, request=request)

    return render_template("login.html", request=request)

def get_instagram_profile_info(username):
    url = f'https://www.instagram.com/{username}/'
    response = requests.get(url)

    if response.status_code != 200:
        return {"exists": False}

    soup = BeautifulSoup(response.text, 'html.parser')

    profile_pic = soup.find('meta', property='og:image')
    profile_pic_url = profile_pic['content'] if profile_pic else None

    bio_meta = soup.find('meta', property='og:description')
    bio = bio_meta['content'].split('-')[0].strip() if bio_meta else None

    if not bio:
        return {"exists": False}

    return {
        "exists": True,
        "profile_picture": profile_pic_url,
        "bio": bio
    }

# Analyze Page
@app.route('/intro')
def analyze():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_email = session['user']
    return render_template("intro.html", user_email=user_email)

@app.route('/check_profile', methods=['POST'])
def check_profile():
    username = request.form.get("username", "").strip()
    result = get_instagram_profile_info(username) if username else {"exists": False}

    # Re-render the intro page with profile result
    return render_template("intro.html", result=result, username=username, user_email=session.get('user'))


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)

