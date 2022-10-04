from flask import Flask
from flask_cors import CORS
from promo_scheduling.settings import APP_NAME
from promo_scheduling.api_v1 import create_api as create_api_v1
from promo_scheduling.api_v2 import create_api as create_api_v2

app = Flask(APP_NAME)
CORS(app)
create_api_v1(app)
create_api_v2(app)
