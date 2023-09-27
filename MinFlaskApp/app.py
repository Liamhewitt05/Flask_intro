from flask import Flask, redirect, url_for, make_response, request

from utils import auth_required

app = Flask(__name__)

app.config.from_prefixed_env()
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

