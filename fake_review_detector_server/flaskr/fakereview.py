import configparser
import os
import pickle

import flask_login
from flask_login import LoginManager, UserMixin

from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
import db
import configparser
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

import db

app = Flask(__name__)
login_manager = LoginManager()

app.secret_key = 'team_mp12'

login_manager.init_app(app)

users = {'test':{'pw':'team_mp12'}}

class User(UserMixin):
  pass

@login_manager.user_loader
def user_loader(username):
  if username not in users:
    return

  user = User()
  user.id = username
  return user

@login_manager.request_loader
def request_loader(request):
  username = request.form.get('username')
  if username not in users:
    return
<<<<<<< Updated upstream
<<<<<<< Updated upstream

  user = User()
  user.id = username

  user.is_authenticated = request.form['pw'] == users[username]['pw']

=======

  user = User()
  user.id = username

  user.is_authenticated = request.form['pw'] == users[username]['pw']

>>>>>>> Stashed changes
=======

  user = User()
  user.id = username

  user.is_authenticated = request.form['pw'] == users[username]['pw']

>>>>>>> Stashed changes
  return user



@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    username = request.form.get('username')
    if request.form.get('pw') == users[username]['pw']:
      user = User()
      user.id = username
      flask_login.login_user(user)
      return redirect(url_for('home'))
  return render_template('login.html')

@app.route('/home')
@flask_login.login_required
def home():
    total_reviews_count, true_reviews_count = db.get_review_stat(mysql)
    return render_template('index.html',
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
                            total_reviews_coun = total_reviews_count,
                            perc_true_review = float(true_reviews_count/(total_reviews_count+0.01)) # calcualte percentage of true reviews.
                          )
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                           total_reviews_count=total_reviews_count,
                           perc_true_review=round(float(true_reviews_count / (total_reviews_count + 0.01)) * 100, 2)
                           # calcualte percentage of true reviews.
                           )

<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

@app.route("/features")
def features():
    return render_template("features.html")


@app.route("/about")
def about():
    return render_template("about-us.html")


@app.route("/howtouse")
def howtouse():
    return render_template("how-to-use.html")


@app.route("/contact")
def contact():
    return render_template("contact-us.html")


@app.route('/predict', methods=['POST'])
def predict():
<<<<<<< Updated upstream
    #cv = CountVectorizer(ngram_range=(1, 2))

=======
    """
    Do prediction with one review from pront-end.
    """
    global total_reviews_count, my_prediction, true_reviews_count
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    if request.method == 'POST':
        message = request.form['message']
        data = [message]
        my_prediction = clf.predict(cv.transform(data).toarray())
        db.insert_review(mysql, message, my_prediction[0])
        total_reviews_count, true_reviews_count = db.get_review_stat(mysql)

    return render_template('index.html',
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
                           prediction = my_prediction,
                           total_reviews_coun = total_reviews_count,
                           perc_true_review = float(true_reviews_count/(total_reviews_count+0.01)) # calcualte percentage of true reviews.
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                           prediction=my_prediction,
                           total_reviews_count=total_reviews_count,
                           perc_true_review=round(float(true_reviews_count / (total_reviews_count + 0.01)) * 100, 2)
                           # calcualte percentage of true reviews.
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                           )


if __name__ == '__main__':

<<<<<<< Updated upstream
=======
    env = app.config['ENV']
    print("Loading in {} environment ....".format(env))
    print("pwd: ", os.getcwd())
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    # Read resources
    filename = 'resources/CatBoostClassifier.pkl'
    clf = pickle.load(open(filename, 'rb'))
    cv = pickle.load(open('resources/transform.pkl', 'rb'))

    # Read config.init
    config = configparser.ConfigParser()
    config.read("config/config.ini")

    # Change this to your secret key (can be anything, it's for extra protection)
    app.secret_key = 'LUCKY'

    # Enter your database connection details below
<<<<<<< Updated upstream
    app.config['MYSQL_HOST'] = config.get("db", "dbhost")
    app.config['MYSQL_USER'] = config.get("db", "dbuser")
    app.config['MYSQL_PASSWORD'] = config.get("db", "dbpassword") # later change it to config.ini
    app.config['MYSQL_DB'] = config.get("db", "dbname")
=======
    if env == 'production':
        app.config['MYSQL_HOST'] = config.get("db-prod", "dbhost")
        app.config['MYSQL_USER'] = config.get("db-prod", "dbuser")
        app.config['MYSQL_PASSWORD'] = config.get("db-prod", "dbpassword")  # later change it to config.ini
        app.config['MYSQL_DB'] = config.get("db-prod", "dbname")
    else:
        app.config['MYSQL_HOST'] = config.get("db-dev", "dbhost")
        app.config['MYSQL_USER'] = config.get("db-dev", "dbuser")
        app.config['MYSQL_PASSWORD'] = config.get("db-dev", "dbpassword")  # later change it to config.ini
        app.config['MYSQL_DB'] = config.get("db-dev", "dbname")
>>>>>>> Stashed changes

    # Intialize MySQL
    mysql = MySQL(app)

<<<<<<< Updated upstream
    app.run(debug=True)

    #app.run(host = "0.0.0.0", port = 5000)
=======
    if env == 'production':
        app.run(host="0.0.0.0", port=8000)
        print("Running server in PRODUCTION mode ...")
    else:
        app.run(debug=True)
        print("Running server in DEBUG mode ...")
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
