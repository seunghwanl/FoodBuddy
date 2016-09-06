from flask import Flask, render_template, request, url_for, flash, session, redirect
from flask.ext.bootstrap import Bootstrap

from forms import LoginForm, RegistrationForm, SearchForm
from dbconnect import connection
from utility import login_required, send_text

import os
import gc
import requests

import oauth2

from passlib.hash import sha256_crypt
from pymysql import escape_string as thwart


app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

def set_params(search_key):
    params = {}
    params['term'] = search_key
    params['location'] = "New+York"
    params['limit'] = "10"

    return params

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.route('/')
def main():
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
  form = LoginForm()

  if form.validate_on_submit():
    username = form.username.data
    passwd = form.passwd.data
    c, conn = connection()

    c.execute("SELECT * FROM users WHERE username = (%s)",
                      thwart(username))

    row = c.fetchone()

    if row is not None and sha256_crypt.verify(passwd, row[2]):
      session['logged_in'] = True
      session['username'] = username

      flash("Welcome!")
      return redirect(url_for('main'))

    else:
      flash('Incorrect username or password')

  return render_template('login.html', form = form)


@app.route('/logout')
@login_required
def logout():
  session.clear()
  flash('logged out!')
  return redirect(url_for('main'))



@app.route('/signup/', methods=['GET', 'POST'])
def signup():
  form = RegistrationForm()

  if form.validate_on_submit():
    username = form.username.data
    password = sha256_crypt.encrypt(str(form.passwd.data))
    c, conn = connection()

    query = c.execute("SELECT * FROM users WHERE username = (%s)",
              thwart(username))

    if int(query) > 0:
      flash("Username is already taken")
      return render_template('signup.html', form = form)
    else:
      c.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
        (thwart(username), thwart(password)))

      conn.commit()

      flash("Registration complete!")
      c.close()
      conn.close()

      gc.collect()
      session['logged_in'] = True

      return redirect(url_for('main'))


  return render_template('signup.html', form = form)


@app.route('/search/', methods=["GET", "POST"])
@login_required
def search():
  form = SearchForm()

  if form.validate_on_submit():
      menu = form.search.data
      url = "https://api.yelp.com/v2/search"
      CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
      CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
      ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
      ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

      consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
      oauth_request = oauth2.Request('GET', url, set_params(menu))
      oauth_request.update(
          {
              'oauth_nonce': oauth2.generate_nonce(),
              'oauth_timestamp': oauth2.generate_timestamp(),
              'oauth_token': ACCESS_TOKEN,
              'oauth_consumer_key': CONSUMER_KEY
          }
      )
      token = oauth2.Token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
      oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
      signed_url = oauth_request.to_url()

      response = requests.get(signed_url)

      return render_template("results.html", results = response.json())
  else:
      return render_template("search.html", form = form)


@app.route('/text', methods=["GET", "POST"])
@login_required
def text():
    if request.method == "POST":
        r = send_text(request.form['phone'],
          request.form['content'] + " " + request.form['img_url'])

        if r[0]:
          flash('Text Successfully Sent!')
        else:
          flash('Sorry, an error has occurred.')

    return redirect(url_for('search'))

if __name__ == "__main__":
  app.run(debug = True)



