from flask import Flask,render_template,url_for,request
import pandas as pd
import numpy as np
import pickle
import xgboost as xgb
from catboost import Pool,CatBoostClassifier
from text_clearning import text_cleaning

from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.externals import joblib

filename = 'CatBoostClassifier.pkl'
clf = pickle.load(open(filename,'rb'))
cv = pickle.load(open('transform.pkl','rb'))

app = Flask(__name__)


@app.route('/')
def home():
	return render_template('index.html')

@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/about")
def about():
    return render_template("about-us.html")

@app.route("/howtouse")
def howtouse():
    return render_template("how-to-use.html")

@app.route('/predict',methods=['POST'])
def predict():
    #cv = CountVectorizer(ngram_range=(1, 2))

    if request.method == 'POST':
        message = request.form['message']
        data = [message]
        #data = [text_cleaning(data)]
        #vect = cv.transform(data).toarray()
        my_prediction = clf.predict(cv.transform(data).toarray())
    return render_template('index.html',prediction = my_prediction)


if __name__ == '__main__':
	app.run(debug=True)
    #app.run(host = "0.0.0.0", port = 5000)
