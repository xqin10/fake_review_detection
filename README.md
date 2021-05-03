# Smartacus V1

http://smartacus.ml/

## Detect fake reviews of restaurants, cafes and bars

Smartacus is a free website to identify fake reviews from hotels, restaurants, cafes, and bars.
Online reviews may be fake, but their effects are real. 

## Target Audience
   Smartacus intends to be useful for travellers coming to Australia and businesses like hotels, restaurants and cafes in Australia, who are listed on the website like Trip Advisor.
## Background
   Smartacus is a web application with a chrome extension that would help travellers distinguish spam reviews when choosing products or services from a website like Tripadvisor. Smartacus also helps small businesses filter spam comments on TripAdvisor.

## Get up and running in 5 mins


### Deploy Server on AWS EC2

After we start and login to our EC2 instance, we can do the following steps in order to make our server run.

**Note:** we use python 3.8.5 on Ubuntu 20.04.2 LTS.

#### 1. Clone Flask app inside EC2

- Create directory for our service.

> cd /opt & mkdir -p software/server

- Install Python Virtualenv.

> sudo apt-get update
>
> sudo apt-get install python3-venv

- Create and activate the new virtual environment.

> python3 -m venv venv
>
> source venv/bin/activate

- Install Flask.

> pip install Flask

- Clone git repository.

> https://github.com/xqin10/fake_review_detection_backend.git

- Install required packages.

> cd fake_review_detector_server & pip install -r requirements.txt

**Note:** In the progress, if the pip reports permission errors, you need to give higher permission for user `ubuntu`. Please go to the `opt/sofware/server` folder and run:

>chown -R ubuntu:ubuntu venv/bin & chown -R ubuntu:ubuntu venv/lib

If there are other install error such as 

> error: invalid command 'bdist_wheel'

Check if there's some basic python dev-tool packages were missing and try to install them at first.

```
sudo apt-get install gcc libpq-dev -y
sudo apt-get install python-dev  python-pip -y
sudo apt-get install python3-dev python3-pip python3-venv python3-wheel -y
```

Our project organization may look something like:

```
.
└── fake_review_detector_server
    └── flaskr
        ├── __pycache__
        ├── config
        ├── resources
        ├── static
        │   ├── bootstrap
        │   │   ├── css
        │   │   └── js
        │   ├── css
        │   ├── fonts
        │   ├── img
        │   │   └── avatars
        │   └── js
        └── templates
```



#### 2. Run the Flask Application

Just go to the project root directory and run 

> python fake_review_detector_server/flaskr/fakereview.py 1>/dev/null 2>/dev/null &

After running, you can check it out on calling 

> curl localhost:8000

And if you can see the index.html content, then it means you nailed it.



#### 3. Run Nginx Webserver to accept and route request to Gunicorn

And then, we set up Nginx as a reverse-proxy to accept the requests from the user and route it our server.

- Install Nginx.

> sudo apt-get nginx

- Start Nginx service and enable it.

> sudo systemctl start nginx
>
> sudo systemctl enable nginx

- Edit the `sites-available/default` file.

> sudo vim /etc/nginx/sites-available/default

- Add following code.

> upstream flaskhelloworld {
>     server 127.0.0.1:8000;
> }

- Add a `proxy_pass` at `location /`.

```
# some code abovelocation / {
    proxy_pass http://flaskhelloworld;
}
# some code below
```

- Restart Nginx.

> sudo systemctl restart nginx

And finally, you can visit your site via public IP of your EC2 on Browser!



### Binding Domain to EC2 public IP


