import flask_login
import re
import spacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language
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
import requests             
from bs4 import BeautifulSoup

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

@app.route('/charts', methods=['GET', 'POST'])
def charts():
  total_reviews_count, true_reviews_count = db.get_review_stat(mysql)
  return render_template('charts.html',
                          fake_reviews_count = total_reviews_count-true_reviews_count,
                          true_reviews_count = true_reviews_count
                        )

@app.route('/home')
def home():
    total_reviews_count, true_reviews_count = db.get_review_stat(mysql)
    return render_template('index.html',
                            word_count = None,
                            language = None,
                            total_reviews_count = total_reviews_count,
                            true_reviews_count = true_reviews_count,
                            fake_reviews_count = total_reviews_count - true_reviews_count,
                            perc_true_review = round(float(true_reviews_count/(total_reviews_count+0.01))*100,2), # calcualte percentage of true reviews.
                            perc_fake_review = round((1-float(true_reviews_count/(total_reviews_count+0.01)))*100,2)
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

@Language.factory('language_detector')
def create_lang_detector(nlp, name):
    return LanguageDetector()

@app.route('/predict',methods=['POST'])
def predict(y_prob=None):
    """
    Do prediction with one review from front-end.
    """
    if request.method == 'POST':
        message = request.form['message']
        data = [message]
        # to count words in string
        print(message)
        res = len(re.findall(r'\w+', message))

        # document level language detection. Think of it like average language of the document!
        nlp = spacy.load('resources/en_core_web_sm')
        # nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
        nlp.add_pipe('language_detector', last=True)
        doc = nlp(message)
        main_language = doc._.language["language"]
        print(main_language)

        # the word limitation
        my_prediction = 0
        y_prob_deceptive = 0
        if res >= 20 and main_language == "en":
            my_prediction = clf.predict(cv.transform(data).toarray())
            y_prob = clf.predict_proba(cv.transform(data).toarray()) #return the labe prediction probability
            y_prob_deceptive = y_prob[:,1]*100 #label prediction probability in percent
            db.insert_review(mysql,message, my_prediction[0])
    
    total_reviews_count, true_reviews_count = db.get_review_stat(mysql)
    return render_template('index.html',
                           word_count = res,
                           language = main_language,
                           prediction = my_prediction,
                           deceptive_prob = y_prob_deceptive,
                           total_reviews_count = total_reviews_count,
                           true_reviews_count = true_reviews_count,
                           fake_reviews_count = total_reviews_count - true_reviews_count,
                           perc_true_review = round(float(true_reviews_count/(total_reviews_count+0.01))*100,2), # calcualte percentage of true reviews.
                           perc_fake_review = round((1-float(true_reviews_count/(total_reviews_count+0.01)))*100,2)
                           )

def scrape(start_url):
  """
  Crawl the given start_url.
  This function has inner ability to extend to do vertical search.

  Param: 
    start_url
  Return:
    List of review objects.
  """
  # start_url = 'https://www.tripadvisor.com.au/Restaurant_Review-g255100-d728473-Reviews-Sud_Food_and_Wine-Melbourne_Victoria.html'
  # split the url to different parts
  url_parts = start_url.split('-Reviews-')
  urls = []
  reviewArr = []
  if "Hotel_Review" in start_url:
      url = start_url
      # print(url)
      urls.append(url)
      # extract all reviews from all urls and store in reviewArr(json objects)
      for url in urls:
          response = requests.get(url,timeout=10)
          content = BeautifulSoup(response.content,"html.parser")
          for review in content.findAll('div', attrs={"class": "_2wrUUKlw _3hFEdNs8"}):
              reviewObject = {
                  "review_title": review.find('div', attrs={"class": "glasR4aX"}).text,
                  "review": review.find('q', attrs={"class": "IRsGHoPm"}).get_text(separator='\n'),
                  "review_rating":str(review.find('div', attrs={"class": "nf9vGX55"}).find('span'))[-11:-10],
                  "date_of_stay":review.find('span', attrs={"class": "_34Xs-BQm"}).text[14:],
                  "review_date": review.find('div', attrs={"class": "_2fxQ4TOx"}).text}
              print(reviewObject)
              reviewArr.append(reviewObject)

  elif "Restaurant_Review" in start_url:
      url = start_url
      # print(url)
      urls.append(url)
      # extract all reviews from all urls and store in reviewArr(json objects)
      for url in urls:
          response = requests.get(url,timeout=10)
          content = BeautifulSoup(response.content,"html.parser")
          for review in content.findAll('div', attrs={"class": "reviewSelector"}):
              reviewObject = {
                  "review_title": review.find('span', attrs={"class": "noQuotes"}).text,
                  "review": review.find('p', attrs={"class": "partial_entry"}).text.replace("\n", ""),
                  "review_rating":str(review.find('div',attrs={"class": "ui_column is-9"}).find('span'))[-11:-10],
                  "date_of_visit":review.find('div', attrs={"class": "prw_rup prw_reviews_stay_date_hsx"}).text[15:],
                  "review_date": review.find('span', attrs={"class": "ratingDate"}).text.strip()
              }
              print(reviewObject)
              reviewArr.append(reviewObject)
  else: 
      print("Please only paste URL of hotel or restaurant review from Trip Advisor!")
  return reviewArr


@app.route('/results',methods=['POST'])
def results():
    """
    Do prediction with one url from pront-end.
    """
    if request.method == 'POST':

      url = request.form['urlinput']
      print("The requested url: " + url)
      data = []
      try:
        scrape_data = scrape(url)
        data = [d['review'] for d in scrape_data]
      except BaseException:
        print("Scrape timeout!")
      # print(data)

      shop_name = ''
      if len(data) >= 1:
        my_prediction = clf.predict(cv.transform(data).toarray())
        y_prob = clf.predict_proba(cv.transform(data).toarray()) #return the labe prediction probability
        y_prob_deceptive_4_real = y_prob[:,1]*100 #label prediction probability in percent
        y_prob_deceptive_4_fake = y_prob[:,0]*100 #label prediction probability in percent
        print(y_prob)
        try:
          shop_names = ((url.split('-Reviews-'))[1].split('-'))
          if len(shop_names) == 2:
            shop_name = shop_names[0]
          elif len(shop_name) == 3:
            shop_name = shop_names[1]
        except BaseException:
          print("Failed to extract shop_name from url!", url)
      else:
        return render_template('results.html',
                                ret_code = 1,
                                msg = 'Url Analyser failed, please use Review Analyser'
                              )

      fake_ret = []
      not_fake_ret = []
      fake_reviews_count = 0
      true_reviews_count = 0
      # The thredhold for fake probability to tell one is a fake.
      thredhold = 65
      for i in range(len(data)):
        ret = {
                "review_title":scrape_data[i]["review_title"],
                "review_rating":scrape_data[i]["review_rating"],
                "review_date":scrape_data[i]["review_date"],
                "review":data[i]
                # "deceptive_prob":str(round(y_prob_deceptive[i],2))+'%'
              }
        # if my_prediction[i] == 0:
        if y_prob_deceptive_4_fake[i] > thredhold:
          ret['deceptive_prob'] = str(round(y_prob_deceptive_4_fake[i],2))+'%'
          fake_ret.append(ret)
          fake_reviews_count += 1
        else:
          ret['real_prob'] = str(round(y_prob_deceptive_4_real[i],2))+'%'
          not_fake_ret.append(ret)
          true_reviews_count += 1
        
        db.insert_review(mysql,data[i], my_prediction[i])

    return render_template('results.html',
                            shop_name = shop_name,
                            ret_code = 0,
                            msg = 'success',
                            fake_ret = fake_ret,
                            not_fake_ret = not_fake_ret,
                            fake_reviews_count = fake_reviews_count,
                            true_reviews_count = true_reviews_count
                          )


if __name__ == '__main__':

    env = app.config['ENV']
    print("Loading in {} environment ....".format(env))

    # Read resources
    filename = 'resources/CatBoostClassifier.pkl'
    # filename = 'resources/lightBGM.pkl'
    clf = pickle.load(open(filename,'rb'))

    # cv = bz2.BZ2File(open('resources/cvtransform.pkl.pbz2', 'rb'))
    # cv = cPickle.load(cv)
    cv = pickle.load(open('resources/transform.pkl', 'rb'))

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
