# Shamelessly copied from http://flask.pocoo.org/docs/quickstart/
import os 

from flask import Flask
from flask_restful import Api

from fsapi_utils import *
from fsapi_musicextract import MusicExtract


app = Flask(__name__)
api = Api(app)
        
def initialize():
    # Generate token
    if ADMIN_USER is None or ADMIN_PASSWD is None or SECRET is None:
        print('[ERROR]: Information to generate token is missing')
        os.abort()
    else:
        token = jwt.encode({'ADMIN_USER': ADMIN_USER, 'ADMIN_PASSWD': ADMIN_PASSWD}, SECRET, algorithm=JWT_ALGO)
        print(f'[IMPORTANT]: Token: {token}')

initialize()

api.add_resource(MusicExtract, '/musicextract', '/musicextract/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=DEBUG)

