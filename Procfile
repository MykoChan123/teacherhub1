web: flask --app main.py db upgrade && gunicorn -w 1 -k eventlet -b 0.0.0.0:8000 main:app
