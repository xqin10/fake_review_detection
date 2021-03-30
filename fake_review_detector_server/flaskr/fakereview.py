from flask import Flask, render_template, url_for, request, session
import pandas as pd
import numpy as np
import pickle
from catboost import Pool,CatBoostClassifier
from flask_mysqldb import MySQL
import db
import configparser


app = Flask(__name__)

@app.route('/')
def home():
    total_reviews_count, true_reviews_count = db.get_review_stat(mysql)
    return render_template('index.html',
                            total_reviews_coun = total_reviews_count,
                            perc_true_review = float(true_reviews_count/(total_reviews_count+0.01)) # calcualte percentage of true reviews.
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
def predict():
    #cv = CountVectorizer(ngram_range=(1, 2))

    if request.method == 'POST':
        message = request.form['message']
        data = [message]
        my_prediction = clf.predict(cv.transform(data).toarray())
        db.insert_review(mysql,message, my_prediction[0])
        total_reviews_count, true_reviews_count = db.get_review_stat(mysql)

    return render_template('index.html',
                           prediction = my_prediction,
                           total_reviews_coun = total_reviews_count,
                           perc_true_review = float(true_reviews_count/(total_reviews_count+0.01)) # calcualte percentage of true reviews.
                           )


if __name__ == '__main__':

    # Read resources
    filename = 'resources/CatBoostClassifier.pkl'
    clf = pickle.load(open(filename,'rb'))
    cv = pickle.load(open('resources/transform.pkl','rb'))

    # Read config.init
    config = configparser.ConfigParser()
    config.read("config/config.ini")

    # Change this to your secret key (can be anything, it's for extra protection)
    app.secret_key = 'LUCKY'

    # Enter your database connection details below
    app.config['MYSQL_HOST'] = config.get("db", "dbhost")
    app.config['MYSQL_USER'] = config.get("db", "dbuser")
    app.config['MYSQL_PASSWORD'] = config.get("db", "dbpassword") # later change it to config.ini
    app.config['MYSQL_DB'] = config.get("db", "dbname")

    # Intialize MySQL
    mysql = MySQL(app)

    app.run(debug=True)

    #app.run(host = "0.0.0.0", port = 5000)
