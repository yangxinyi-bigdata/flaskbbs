import multiprocessing

bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 10
accesslog = "/var/log/pythonbbs/gunicorn_access.log"
errorlog = "/var/log/pythonbbs/gunicorn_error.log"
preload_app = True
daemon = True
