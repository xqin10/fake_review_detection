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
from catboost import Pool, CatBoostClassifier
from lightgbm import LGBMClassifier
from flask_mysqldb import MySQL
import db
import configparser
import math
from flask_login import LoginManager, UserMixin
import requests
from bs4 import BeautifulSoup
from flask import jsonify
from flask import Flask, send_from_directory

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
                           fake_reviews_count=total_reviews_count-true_reviews_count,
                           true_reviews_count=true_reviews_count
                           )

@app.route("/download")
def download():
    return send_from_directory(r"resources",filename="extentions.zip",as_attachment=True)

@app.route('/home')
def home():
    total_reviews_count, true_reviews_count = db.get_review_stat(mysql)
    return render_template('index.html',
                           word_count=None,
                           language=None,
                           total_reviews_count=total_reviews_count,
                           true_reviews_count=true_reviews_count,
                           fake_reviews_count=total_reviews_count - true_reviews_count,
                           # calcualte percentage of true reviews.
                           perc_true_review=round(
                               float(true_reviews_count/(total_reviews_count+0.01))*100, 2),
                           perc_fake_review=round(
                               (1-float(true_reviews_count/(total_reviews_count+0.01)))*100, 2)
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


@app.route("/howitworks")
def howitworks():
    return render_template("How-It-Works.html")

@app.route("/geteducated")
def geteducated():
    return render_template("Get-Educated.html")

@app.route("/contact")
def contact():
    return render_template("contact-us.html")


@Language.factory('language_detector')
def create_lang_detector(nlp, name):
    return LanguageDetector()


@app.route('/predict', methods=['POST'])
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
            # return the labe prediction probability
            y_prob = clf.predict_proba(cv.transform(data).toarray())
            # label prediction probability in percent
            y_prob_deceptive = y_prob[:,0]*100
            db.insert_review(mysql, message, my_prediction[0])

    total_reviews_count, true_reviews_count = db.get_review_stat(mysql)
    return render_template('index.html',
                           word_count=res,
                           language=main_language,
                           prediction=my_prediction,
                           deceptive_prob=y_prob_deceptive,
                           total_reviews_count=total_reviews_count,
                           true_reviews_count=true_reviews_count,
                           fake_reviews_count=total_reviews_count - true_reviews_count,
                           # calcualte percentage of true reviews.
                           perc_true_review=round(
                               float(true_reviews_count/(total_reviews_count+0.01))*100, 2),
                           perc_fake_review=round(
                               (1-float(true_reviews_count/(total_reviews_count+0.01)))*100, 2)
                           )


@app.route('/predict/api/v1', methods=['POST'])
def predict_api():
    """
    Do prediction with one review from front-end in the style of RESTfuL.
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
        my_prediction = [0]
        y_prob_deceptive = 0
        if res >= 20 and main_language == "en":
            my_prediction = clf.predict(cv.transform(data).toarray())
            # return the labe prediction probability
            y_prob = clf.predict_proba(cv.transform(data).toarray())
            # label prediction probability in percent
            y_prob_deceptive = y_prob[:,0]*100
            print(my_prediction)
            print(y_prob_deceptive)
            db.insert_review(mysql, message, my_prediction[0])

    total_reviews_count, true_reviews_count = db.get_review_stat(mysql)
    return jsonify({
        'word_count': res,
        'language': main_language,
        'prediction': str(my_prediction[0])
    })


def extract_one_pagination(node):
    """
    """
    p = {}
    p['name'] = node.string
    if 'disabled' in node['class']:
        p['status'] = 'disable'
    else:
        p['status'] = None
    if 'href' in node.attrs:
        p['url'] = 'https://www.tripadvisor.com.au' + node['href']
    else:
        p['url'] = '#'
    print(p)
    return p


def extract_paginations(content):
    """
    """
    ps = []
    paging = content.findAll('div', attrs={"class": "ui_pagination"})
    for c in paging[0].children:
        if 'pageNumbers' in c['class']:
            for cc in c.children:
                ps.append(extract_one_pagination(cc))
        else:
            ps.append(extract_one_pagination(c))
    print(ps)
    return ps


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
    biz_type = None
    platform_type = None
    paginations = None
    if "Hotel_Review" in start_url:
        url = start_url
        # print(url)
        urls.append(url)
        # extract all reviews from all urls and store in reviewArr(json objects)
        for url in urls:
            response = requests.get(url, timeout=10)
            content = BeautifulSoup(response.content, "html.parser")
            for review in content.findAll('div', attrs={"class": "_2wrUUKlw _3hFEdNs8"}):
                reviewObject = {
                    "review_title": review.find('div', attrs={"class": "glasR4aX"}).text,
                    "review": review.find('q', attrs={"class": "IRsGHoPm"}).get_text(separator='\n'),
                    "review_rating": str(review.find('div', attrs={"class": "nf9vGX55"}).find('span'))[-11:-10],
                    "date_of_stay": review.find('span', attrs={"class": "_34Xs-BQm"}).text[14:],
                    "review_date": review.find('div', attrs={"class": "_2fxQ4TOx"}).text}
                print(reviewObject)
                reviewArr.append(reviewObject)
                biz_type = "Hotel"
                platform_type = "TripAdvisor"
            paginations = extract_paginations(content)

    elif "Restaurant_Review" in start_url:
        url = start_url
        # print(url)
        urls.append(url)
        # extract all reviews from all urls and store in reviewArr(json objects)
        for url in urls:
            response = requests.get(url, timeout=10)
            content = BeautifulSoup(response.content, "html.parser")
            for review in content.findAll('div', attrs={"class": "reviewSelector"}):
                reviewObject = {
                    "review_title": review.find('span', attrs={"class": "noQuotes"}).text,
                    "review": review.find('p', attrs={"class": "partial_entry"}).text.replace("\n", ""),
                    "review_rating": str(review.find('div', attrs={"class": "ui_column is-9"}).find('span'))[-11:-10],
                    "date_of_visit": review.find('div', attrs={"class": "prw_rup prw_reviews_stay_date_hsx"}).text[15:],
                    "review_date": review.find('span', attrs={"class": "ratingDate"}).text.strip()
                }
                print(reviewObject)
                reviewArr.append(reviewObject)
                biz_type = "Restaurant"
                platform_type = "TripAdvisor"
            paginations = extract_paginations(content)

    elif "www.yelp.com" in start_url:
        biz_type = "Biz"
        platform_type = "Yelp"
        if "?start=" not in start_url:
            # Only access the first page.
            for page in range(0, 1):
                url = start_url + '?start={}'.format(10*page)
                print(url)
                urls.append(url)
        else:
            for page in range(int(int(start_url[-2:])/10), int(int(start_url[-2:])/10 + 5)):
                url = start_url[:-9] + '?start={}'.format(10*page)
                print(url)
                urls.append(url)
        for url in urls:
            response = requests.get(url, timeout=10)
            try:
                status = response.status_code
                print(status)
            except Exception as e:
                print(e)
            content = BeautifulSoup(response.content, "html.parser")
            for review in content.findAll('div', {"class": "review__373c0__13kpL border-color--default__373c0__2oFDT"}):
                reviewObject = {
                    "review": review.find('p', attrs={"class": "comment__373c0__1M-px css-n6i4z7"}).text.replace("\xa0", ""),
                    "review_rating": review.select('[aria-label*=rating]')[0]['aria-label'][:1],
                    "review_date": review.find('span', attrs={"class": "css-e81eai"}).text
                }
                print(reviewObject)
                reviewArr.append(reviewObject)
    else:
        print("Please only paste URL of hotel or restaurant review from Trip Advisor!")
    return biz_type, platform_type, reviewArr, paginations


def extract_shopname(url, platform_type):
    """
    """
    shop_name = ''
    try:
        if platform_type == 'TripAdvisor':
            shop_names = ((url.split('-Reviews-'))[1].split('-'))
            if len(shop_names) == 2:
                shop_name = shop_names[0]
            elif len(shop_name) == 3:
                shop_name = shop_names[1]
        elif platform_type == 'Yelp':
            shop_names = ((url.split('/biz/'))[1].split('-'))
            if len(shop_names) == 2:
                shop_name = shop_names[0]
            elif len(shop_names) >= 3:
                for idx in range(len(shop_names)-1):
                    if idx != len(shop_names)-2:
                        shop_name += (shop_names[idx]+'-')
                    else:
                        shop_name += shop_names[idx]
    except BaseException:
        print("Failed to extract shop_name from url!", url)
    return shop_name


@app.route('/results', methods=['POST'])
def results():
    """
    Do prediction with one url from pront-end.
    """
    if request.method == 'POST':
        # testing
        # scrape_data = [{'review_title': 'Quality food, great service. ', 'review': 'We had a couple of pizzas and the fruitti da mare pasta. All delicious. They catered for my gluten intolerances and my fussy 6yo’s requirements. Good wine selection too. Highly recommend.', 'review_rating': '5', 'date_of_visit': 'April 2021', 'review_date': 'Reviewed 6 days ago'},{'review_title': '2 glasses of Wild Turkey $36 1 Spaghetti of the Sea $35 what a blatant ripoff.', 'review': 'Food was good, staff were nice, but to charge $12 a nip of Wild Turkey and $6 for a small bottle of coke, and pour it yourself, who the hell does that???Yes that is right $18 for a nip of Wild Turkey in a...small to medium glass and add your own coke and ice, - twice.  I asked for a Wild Turkey and coke in a tall glass with ice, go figure.More', 'review_rating': '2', 'date_of_visit': 'April 2021', 'review_date': 'Reviewed 4 weeks ago'},{'review_title': 'Supreme dinner!', 'review': 'We booked this restaurant on a Monday night and everything was amazing! We had starters, pizza and pasta and as we are Italians I can tell you that this is the best restaurant I’ve been in Melbourne! Great location and quiet spot! Be back 100%....Many thanks to the owners and all the staff.More', 'review_rating': '5', 'date_of_visit': 'March 2021', 'review_date': 'Reviewed March 22, 2021'},{'review_title': 'Disappointed', 'review': 'I booked this restaurant as they advertise freshly made pasta however what we received was chewy, bland and very disappointing.The entree focaccia with tomatoes and buffalo mozzarella was yummy though and the pizzas looked good - we should have ordered them instead.My husband...gave the feedback that he was disappointed in the quality of the pasta and instead of accepting the feedback the staff turned very defensive and aggressive with a cook coming out of the kitchen with a snap lock bag of this supposed fresh pasta to prove to us it was fresh however it made a clanking sound when dropped on the bench very much like dry/packet pasta sounds. We were also surprised that there wasn’t a manager to speak to on a Saturday night.More', 'review_rating': '2', 'date_of_visit': 'March 2021', 'review_date': 'Reviewed March 21, 2021'},{'review_title': 'Sensational ', 'review': 'Excellent night out. Pasta and pizzas was tasty, piping hot and prices quite reasonable. Tucked away down Little Collins St', 'review_rating': '5', 'date_of_visit': 'March 2021', 'review_date': 'Reviewed March 20, 2021'},{'review_title': 'Top class', 'review': 'Excellent location. Beautifully presented dining space. Excellent pizza with buffalo mozzarella and a good wine choice.Prices not cheap but reasonable for the quality.Service top notch.', 'review_rating': '5', 'date_of_visit': 'March 2021', 'review_date': 'Reviewed March 20, 2021'},{'review_title': 'Delish dinner date', 'review': 'Had a fantastic dinner date. Enjoyed the calzone with extra hot salami and a few glasses of pinot grigio.', 'review_rating': '5', 'date_of_visit': 'March 2021', 'review_date': 'Reviewed March 17, 2021'},{'review_title': 'Delicious pasta', 'review': 'I was walking by this place and thought it looked nice so I decided to try a few dishes - am so glad I did. The service was very prompt and the Matriciana and Tiramisu were very tasty. I’ll definitely return!', 'review_rating': '4', 'date_of_visit': 'March 2021', 'review_date': 'Reviewed March 15, 2021'},{'review_title': 'Venetian Gem', 'review': "Tucked away out of the busy restaurant precincts of Melbourne, Da Guido 365 is a hidden gem. My. wife and I decided to share our meal and we enjoyed every morsel.We ordered some Maccheroni all' Amatriciana, Tortellini panna, prosciutto e funghi, as well as...a Da Guido pizza, along with a glass of Chianti.Before our meals were served, we were presented with a delicious, complimentary bruschetta, which fired up our tastebuds for the main event.Let me say that this was one of the finest Italian meals I have eaten in Melbourne. The pasta was perfectly 'al dente' and the pizza, with a delicious base was outstanding. The restaurant had a pleasant, welcoming 'buzz' and the service was informative, friendly and genuine. I would not hesitate to recommend Da Guido 365 to anyone seeking a genuine, Italian experience.More", 'review_rating': '5', 'date_of_visit': 'March 2021', 'review_date': 'Reviewed March 14, 2021'},{'review_title': 'Disappointing experience, small serve, food cold', 'review': "First off, this review is for my satisfaction of how Da Guido handled my home delivery. I placed an order for ravioli and received a call from a strange mobile number a relatively short time later. The mobile number was the restaurant saying the food...was ready. The caller asked me to contact the delivery service (no restaurant has ever asked me to do this before) but anyways I did. I then still had no food an hour later so I called the restaurant's mobile number back. They assured me they would follow up and call me back but I received no call. I felt like the restaurant was again passing all of the responsibility onto me when all I did was make the order. Then to add insult to injury, a stone cold ravioli turns up. What made it worse after waiting over 2 hours was that it was about 10 squares of pasta for $35. I might be being generous. While the restaurant cannot handle what the delivery service does, I find the restaurant's poor level of customer service, pricing and serving quantity to be absolutely inadequate.More", 'review_rating': '1', 'date_of_visit': 'March 2021', 'review_date': 'Reviewed March 13, 2021'}]
        # paginations = [{'name': 'Previous', 'status': 'disable', 'url': None}, {'name': 'Next', 'status': None, 'url': 'https://www.tripadvisor.com/Restaurant_Review-g255100-d728473-Reviews-or10-Sud_Food_and_Wine-Melbourne_Victoria.html'}, {'name': '1', 'status': None, 'url': 'https://www.tripadvisor.com/Restaurant_Review-g255100-d728473-Reviews-Sud_Food_and_Wine-Melbourne_Victoria.html'}, {'name': '2', 'status': None, 'url': 'https://www.tripadvisor.com/Restaurant_Review-g255100-d728473-Reviews-or10-Sud_Food_and_Wine-Melbourne_Victoria.html'}, {'name': '3', 'status': None, 'url': '/Restaurant_Review-g255100-d728473-Reviews-or20-Sud_Food_and_Wine-Melbourne_Victoria.html'}, {'name': '4', 'status': None, 'url': '/Restaurant_Review-g255100-d728473-Reviews-or30-Sud_Food_and_Wine-Melbourne_Victoria.html'}, {'name': '5', 'status': None, 'url': '/Restaurant_Review-g255100-d728473-Reviews-or40-Sud_Food_and_Wine-Melbourne_Victoria.html'}, {'name': '6', 'status': None, 'url': '/Restaurant_Review-g255100-d728473-Reviews-or50-Sud_Food_and_Wine-Melbourne_Victoria.html'}, {'name': '…', 'status': None, 'url': None}, {'name': '21', 'status': None, 'url': '/Restaurant_Review-g255100-d728473-Reviews-or200-Sud_Food_and_Wine-Melbourne_Victoria.html'}]

        url = request.form.get('urlinput') if request.form.get(
            'urlinput') else request.form.get('urlinput_1')
        if url is None or url == '':
            return render_template('results.html',
                                   ret_code=1,
                                   msg='Url Analyser failed, please use Review Analyser'
                                   )
        print("The requested url: " + url)
        
        data = []
        try:
            biz_type, platform_type, scrape_data, paginations = scrape(url)
            data = [d['review'] for d in scrape_data]
        except BaseException:
            print("Scrape timeout!")

        # testing
        # biz_type = 'Restaurant'
        # platform_type = 'TripAdvisor'
        # data = [d['review'] for d in scrape_data]

        if len(data) >= 1:
            # 0 means authentic, 1 means fake
            my_prediction = clf.predict(cv.transform(data).toarray())
            # return the labe prediction probability
            y_prob = clf.predict_proba(cv.transform(data).toarray())
            # label prediction probability in percent
            y_prob_4_real = y_prob[:, 0]*100
            # label prediction probability in percent
            y_prob_4_fake = y_prob[:, 1]*100
            print(my_prediction)
            print(y_prob)
            # Get the shop name.
            shop_name = extract_shopname(url, platform_type)
        else:
            return render_template('results.html',
                                   ret_code=1,
                                   msg='Url Analyser failed, please use Review Analyser'
                                   )
        fake_ret = []
        real_ret = []
        fake_reviews_count = 0
        true_reviews_count = 0
        prediction = []
        # The thredhold for fake probability to tell one is a fake.
        thredhold = 60
        for i in range(len(data)):
            # Assemble return data.
            if 'review_title' in scrape_data[i]:
                ret = {
                    "review_title": scrape_data[i]["review_title"],
                    "review_rating": scrape_data[i]["review_rating"],
                    "review_date": scrape_data[i]["review_date"],
                    "review": data[i]
                }
            else:
                ret = {
                    "review_rating": scrape_data[i]["review_rating"],
                    "review_date": scrape_data[i]["review_date"],
                    "review": data[i]
                }
            # Only when prob > thredhold, it is defined as Fake.
            if y_prob_4_fake[i] > thredhold:
                ret['fake_prob'] = str(round(y_prob_4_fake[i], 2))+'%'
                fake_ret.append(ret)
                fake_reviews_count += 1
                prediction.append(1)
            else:
                ret['real_prob'] = str(round(y_prob_4_real[i], 2))+'%'
                real_ret.append(ret)
                true_reviews_count += 1
                prediction.append(0)

            db.insert_review(mysql, data[i], prediction[i])

    return render_template('results.html',
                           shop_name=shop_name,
                           ret_code=0,
                           msg='success',
                           fake_ret=fake_ret,
                           real_ret=real_ret,
                           fake_reviews_count=fake_reviews_count,
                           true_reviews_count=true_reviews_count,
                           biz_type=biz_type,
                           platform_type=platform_type,
                           paginations=paginations
                           )


if __name__ == '__main__':

    env = app.config['ENV']
    print("Loading in {} environment ....".format(env))

    # Read resources
    clf = bz2.BZ2File(open('resources/LGBM.pkl.pbz2', 'rb'))
    clf = cPickle.load(clf)

    cv = bz2.BZ2File(open('resources/cvtransform.pkl.pbz2', 'rb'))
    cv = cPickle.load(cv)

    # Read config.init
    config = configparser.ConfigParser()
    config.read("config/config.ini")

    # Change this to your secret key (can be anything, it's for extra protection)
    app.secret_key = 'LUCKY'

    # Enter your database connection details below
    if env == 'production':
        app.config['MYSQL_HOST'] = config.get("db-prod", "dbhost")
        app.config['MYSQL_USER'] = config.get("db-prod", "dbuser")
        app.config['MYSQL_PASSWORD'] = config.get(
            "db-prod", "dbpassword")  # later change it to config.ini
        app.config['MYSQL_DB'] = config.get("db-prod", "dbname")
    else:
        app.config['MYSQL_HOST'] = config.get("db-dev", "dbhost")
        app.config['MYSQL_USER'] = config.get("db-dev", "dbuser")
        app.config['MYSQL_PASSWORD'] = config.get(
            "db-dev", "dbpassword")  # later change it to config.ini
        app.config['MYSQL_DB'] = config.get("db-dev", "dbname")

    # Intialize MySQL
    mysql = MySQL(app)

    if env == 'production':
        app.run(host="0.0.0.0", port=8000)
        print("Running server in PRODUCTION mode ...")
    else:
        app.run(debug=True)
        print("Running server in DEBUG mode ...")
