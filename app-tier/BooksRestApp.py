#!/usr/bin/python3
##
# Flask/Python server providing a REST API to access book data
#
# For usage run first ensure the '.py' script is executable and then run:
#  $ ./BooksRestApp.py
#
# Prerequisites:
# * Change the MongoDB ULR in the .env file to point to a running MongoDB database, e.g.:
#  MONGODB_URL="mongodb://localhost:27017"
# * Install Python library depedencies
#  $ pip3 install --user pymongo dnspython python-dotenv Flask Flask-Cors
##
import logging
from os import environ
from os.path import join, dirname
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import uuid
from BooksMgr import BooksMgr


#
# Constants
#
ENV_FILE = '.env'
DEFAULT_MONGODB_URL = 'mongodb://localhost:27017'
DB_NAME = 'bookdata'
COLL_NAME = 'books'
FLASK_ENV_VAR = 'FLASK_ENV'
FLASK_PROD_MODE = 'production'
FLASK_DEV_MODE = 'development'


##
# Initialise Flask with appropriate log level, plus cross-origin resource sharing (CORS) support if
# in debug mode to enable Vue JavaScript app to be served from a different server from the REST ap
# without the browser prevented (not needed in production as both will be served from the same
# nginx server/port.
##
def init_app():
    app = Flask(__name__)
    load_dotenv(join(dirname(__file__), ENV_FILE))
    app.config.from_object(__name__)
    mode = environ.get(FLASK_ENV_VAR, FLASK_PROD_MODE)

    if mode == FLASK_DEV_MODE:
        CORS(app, resources={r'/*': {'origins': '*'}})  # Set if client+app tier on different hosts

    if app.debug:
        logging.getLogger('werkzeug').setLevel(logging.INFO)
    else:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

        if mode == FLASK_DEV_MODE:
            logging.warning(f"App has been started in '{FLASK_PROD_MODE}' mode but local '.env' "
                            f"file's 'FLASK_ENV_VAR' variable is set to '{FLASK_DEV_MODE}' mode - "
                            f"this is fine for a Development environment, to support cross-origin "
                            f"resource sharing (CORS) but be sure to change the variable's value "
                            f"before running this in a Production environment")

    return app


#
# Global variables for use in the app.route REST decorators (Gunicorn will also look for the
# 'app' variable too, if this Flask script is started with Gunicorn)
#
app = init_app()
mongodb_url = environ.get('MONGODB_URL', DEFAULT_MONGODB_URL)
print(f"Running Flask server connected to MongoDB at: '{mongodb_url}'")
books_mgr = BooksMgr(mongodb_url, DB_NAME, COLL_NAME)


##
# BOOKS REST API
##
@app.route('/books', methods=['GET', 'POST'])
def all_books():
    try:
        if request.method == 'POST':
            data = request.get_json()

            if not data:
                return 'No data provided in client request', 400

            data['id'] = uuid.uuid4().hex

            if books_mgr.create(data):
                response_object = {'Inserted': {'id': data['id']}}
            else:
                return 'Record was not inserted', 304
        else:
            response_object = books_mgr.list(request.args.get('skip'), request.args.get('limit'),
                                             request.args.get('sortdesc'),
                                             request.args.get('sortasc'))

        return jsonify(response_object)
    except ValueError as ve:
        logging.info(f'Issue with client request: "{ve}"')
        return f'Issue with client request: "{ve}"', 400
    except Exception as ex:
        logging.exception('Internal error processing REST request')
        return f'Internal error on server', 500


##
# BOOK REST API
##
@app.route('/books/<book_id>', methods=['GET', 'PUT', 'DELETE'])
def single_book(book_id):
    try:
        if request.method == 'PUT':
            data = request.get_json()

            if not data:
                return 'No data provided in client request', 400

            if books_mgr.update(book_id, data):
                response_object = {'Updated': {'id': book_id}}
            else:
                return 'Record was not updated', 304
        elif request.method == 'DELETE':
            if books_mgr.delete(book_id):
                response_object = {'Deleted': {'id': book_id}}
            else:
                return 'Record was not deleted', 304
        else:
            response_object = books_mgr.read(book_id)

        return jsonify(response_object)
    except ValueError as ve:
        logging.info(f'Issue with client request: "{ve}"')
        return f'Issue with client request: "{ve}"', 400
    except Exception as ex:
        logging.exception('Internal error processing REST request')
        return f'Internal error on server', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
