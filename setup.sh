#!/bin/bash

# Please run this

sudo apt-get update

sudo apt-get install python3-venv

mkdir -p /opt/software/server

cd /opt/software/server

python -m venv venv

source venv/bin/activate

pip install Flask

cd venv && git clone https://github.com/xqin10/fake_review_detection_backend.git .

pip install gunicorn

pip install supervisor

sudo mkdir -p /etc/supervisor/conf.d

sudo cp /opt/software/server/venv/fake_review_detection_backend/fake_review_detector_server/flaskr/config/wsgi.ini /etc/supervisor/conf.d/wsgi.ini

sudo chmod 700 /etc/supervisor/conf.d/wsgi.ini

sudo apt-get nginx

sudo systemctl start nginx

sudo systemctl enable nginx

sudo cp /opt/software/server/venv/fake_review_detection_backend/fake_review_detector_server/flaskr/config/default /etc/nginx/sites-available/default

sudo chmod 700 /etc/nginx/sites-available/default

sudo systemctl restart nginx

supervisord -c /etc/supervisor/conf.d/wsgi.ini

ps aux | grep py

