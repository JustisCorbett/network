import os
from waitress import serve

from project4.wsgi import application

# Get port from env variable.
port = os.environ["PORT"]

# Serve django application with waitress.
if __name__ == '__main__':
    serve(application, port=port)