# Python standard libraries
import json
import os
import sqlite3
from dotenv import load_dotenv
from werkzeug.exceptions import abort

# Third-party libraries
from flask import Flask, redirect, request, url_for, render_template, flash
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
from MinFlaskApp.database import SQL_to_csv, get_all_books, get_book, get_book_by_title, get_db_connection

# Internal imports
from db import init_db_command
from user_google import User


load_dotenv()

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

print(GOOGLE_CLIENT_ID)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)

try:
    init_db_command()
except sqlite3.OperationalError:
    pass

# Set up a client for loging in to google
client = WebApplicationClient(GOOGLE_CLIENT_ID)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/")
def index():
    books = get_all_books()
    if current_user.is_authenticated:
        return render_template('index.html', books=books, current_user=current_user)
    else:
        return '<a class="button" href="/login">Google Login</a>'


@app.route("/redirect")
def redirect_to_index():
    return render_template('redirect_to_index.html', current_user=current_user)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    """Show a google login page"""
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    print(request.base_url + "/callback")

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    print(request_uri)

    # Redirect to url
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code

    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]


    else:
        return "User email not available or not verified by Google.", 400

    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    login_user(user)

    return redirect(url_for("redirect_to_index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/<int:book_id>')
def book(book_id):
    book = get_book(book_id)
    if book is None:
        abort(404)

    return render_template('book.html', book=book)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        count = request.form['count']

        if not title:
            flash('Title is required!')
        elif not count or int(count) < 0:
            flash('Antall må være 1 eller høyere')
        elif not content:
            flash('Content is required!')
        else:
            book = get_book_by_title(title)
            if book:
                flash('Title already exists!')
            else:
                conn = get_db_connection()
                conn.execute('INSERT INTO books (title, content, count) VALUES (?, ?, ?)',
                             (title, content, count))
                conn.commit()
                conn.close()
                return redirect(url_for('index'))

    return render_template('create.html'), SQL_to_csv(edit)


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    book = get_book(id)
    if book is None:
        abort(404)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['summary']
        count = request.form['count']

        conn = get_db_connection()
        conn.execute('UPDATE books SET title = ?, content = ?, count = ?'
                     ' WHERE id = ?',
                     (title, content, count, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('edit.html', book=book), SQL_to_csv(edit)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_book(id)
    if post is None:
        abort(404)
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index')), SQL_to_csv(edit)


if __name__ == "__main__":
    app.run(ssl_context="adhoc", host="0.0.0.0")
