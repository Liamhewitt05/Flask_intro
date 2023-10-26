from flask import Flask, flask_login, redirect, url_for, make_response, request
from dotenv import load_dotenv
from utils import auth_required
import os


load_dotenv()

app = Flask(__name__)

app.config['SITE_USER'] = os.getenv('FLASK_SITE_USER')
app.config['SITE_PASS'] = os.getenv('FLASK_SITE_PASS')

@app.route("/")
@auth_required
def home():
    return "<h1>Welcome<h1>"

@app.route("/<name>")
def user(name):
    return f"Hello {name}!"

@app.route("/<name>/admin")
def admin(name):
    if name != "liam":
        return redirect(url_for("home"))
    else:
        return f"Hei {name}"



if __name__ == "__main__":
    app.run()

