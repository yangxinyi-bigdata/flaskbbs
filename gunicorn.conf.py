import multiprocessing

bind = "127.0.0.1:5000" # 这样只能在内网访问
# bind = "0.0.0.0:5000"  # 这样可以在外网访问, 但是使用nginx不需要
workers = multiprocessing.cpu_count() * 2 + 1
threads = 10
accesslog = "/var/log/pythonbbs/gunicorn_access.log"
errorlog = "/var/log/pythonbbs/gunicorn_error.log"
preload_app = True
daemon = True
