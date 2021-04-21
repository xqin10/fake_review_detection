import flask_login
import re
import spacy
from spacy_langdetect import LanguageDetector
from flask import Flask, render_template, url_for, request, session, redirect
import pandas as pd
import numpy as np
import pickle
import _pickle as cPickle
import bz2
from catboost import Pool,CatBoostClassifier
from lightgbm import LGBMClassifier
from flask_mysqldb import MySQL
import db
import configparser
import math
from flask_login import LoginManager, UserMixin

app = Flask(__name__)

login_manager = LoginManager()

app.secret_key = 'team_mp12'

login_manager.init_app(app)

users = {'test': {'pw': 'team_mp12'}}


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

  user = User()
  user.id = username

  user.is_authenticated = request.form['pw'] == users[username]['pw']

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
def home():
    total_reviews_count, true_reviews_count = db.get_review_stat(mysql)
    return render_template('index.html',
                            total_reviews_count = total_reviews_count,
                            perc_true_review = round(float(true_reviews_count/(total_reviews_count+0.01))*100,2) # calcualte percentage of true reviews.
                          )

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

@app.route('/predict',methods=['POST'])
def predict(y_prob=None):
    """
    Do prediction with one review from front-end.
    """
    if request.method == 'POST':
        message = request.form['message']
        data = [message]
        # to count words in string
        res = len(re.findall(r'\w+', data))

        # document level language detection. Think of it like average language of the document!
        nlp = spacy.load('en_core_web_sm')
        nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
        doc = nlp(data)
        main_language = doc._.language["language"]
        #print(doc._.language)

        # the word limitation
        if res >= 200 and main_language == "en":
            my_prediction = clf.predict(cv.transform(data).toarray())
            y_prob = clf.predict_proba(cv.transform(data).toarray()) #return the labe prediction probability
            y_prob_deceptive = y_prob[:,1]*100 #label prediction probability in percent
            db.insert_review(mysql,message, my_prediction[0])
            total_reviews_count, true_reviews_count = db.get_review_stat(mysql)
            #answer = "The minimum of word is 200, please input more"
    return render_template('index.html',
                           word_count = res,
                           language = main_language,
                           prediction = my_prediction,
                           deceptive_prob = y_prob_deceptive,
                           total_reviews_count = total_reviews_count,
                           perc_true_review = round(float(true_reviews_count/(total_reviews_count+0.01))*100,2) # calcualte percentage of true reviews.
                           )


if __name__ == '__main__':

    env = app.config['ENV']
    print("Loading in {} environment ....".format(env))

    # Read resources
    #filename = 'resources/CatBoostClassifier.pkl'
    filename = 'resources/lightBGM.pkl'
    clf = pickle.load(open(filename,'rb'))
   
    cv = bz2.BZ2File(open('resources/cvtransform.pkl', ‘rb’) #decompress the compressed pickle
    cv = cPickle.load(cv)
     
    #cv = pickle.load(open('resources/cvtransform.pkl','rb'))

    # Read config.init
    config = configparser.ConfigParser()
    config.read("config/config.ini")

    # Change this to your secret key (can be anything, it's for extra protection)
    app.secret_key = 'LUCKY'

    # Enter your database connection details below
    if env == 'production':
        app.config['MYSQL_HOST'] = config.get("db-prod", "dbhost")
        app.config['MYSQL_USER'] = config.get("db-prod", "dbuser")
        app.config['MYSQL_PASSWORD'] = config.get("db-prod", "dbpassword") # later change it to config.ini
        app.config['MYSQL_DB'] = config.get("db-prod", "dbname")
    else:
        app.config['MYSQL_HOST'] = config.get("db-dev", "dbhost")
        app.config['MYSQL_USER'] = config.get("db-dev", "dbuser")
        app.config['MYSQL_PASSWORD'] = config.get("db-dev", "dbpassword") # later change it to config.ini
        app.config['MYSQL_DB'] = config.get("db-dev", "dbname")

    # Intialize MySQL
    mysql = MySQL(app)

    if env == 'production':
        app.run(host = "0.0.0.0", port = 8000)
        print("Running server in PRODUCTION mode ...")
    else:
        app.run(debug=True)
        print("Running server in DEBUG mode ...")
