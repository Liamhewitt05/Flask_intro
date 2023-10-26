from functools import wraps

from flask import Flask, redirect, url_for, make_response, request, current_app


def check_user(username, password):
    data = {
        'liam': {
            'password': '123'
        },
        'sondre': {
            'password': '456'
        }
    }
    if username.lower() in data:
        return password == data[username.lower()]['password']
    return False

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and check_user(auth.username, auth.password):
            return f(*args, **kwargs)
        #if auth and auth.username == current_app.config["SITE_USER"] and auth.password == current_app.config["SITE_PASS"]:
        #    return f(*args, **kwargs)
        return make_response("<h1>Access denied!!!!!<h1>", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    return decorated