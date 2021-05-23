# gunicorn.conf.py
import multiprocessing

bind = '0.0.0.0:8000'
backlog = 512
# chdir = '/home/python/PycharmProjects/News-Information'
timeout = 30
debug = False
pidfile = './gunicorn.pid'
worker_class = 'gevent'

workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
keepalive = 75
loglevel = 'info'
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'

"""
h          remote address
l          '-'
u          currently '-', may be user name in future releases
t          date of the request
r          status line (e.g. ``GET / HTTP/1.1``)
s          status
b          response length or '-'
f          referer
a          user agent
T          request time in seconds
D          request time in microseconds
L          request time in decimal seconds
p          process ID
"""
accesslog = "/opt/logs/gunicorn_access.log"
errorlog = "/opt/logs/gunicorn_error.log"

# x_forwarded_for_header = 'X-FORWARDED-FOR'