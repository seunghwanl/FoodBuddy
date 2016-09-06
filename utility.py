from functools import wraps
from flask import flash, session, request, redirect, url_for
import requests

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session.keys() or not session['logged_in']:
            flash("log in required")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def send_text(numstring, message):
    message = {"number": numstring, "message": message}
    r = requests.post("http://textbelt.com/text", data = message)
    return r.status_code, r.text

