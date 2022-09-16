from flask import Flask, request, Response, abort
import json
from flask_restful import Resource
from flask_restful import Api
# from flasgger import Swagger, swag_from
from flask_cors import CORS
from promo_scheduling.app import promo_scheduling
from promo_scheduling.settings import APP_NAME

app = Flask(APP_NAME)
CORS(app)
api = Api(app=app, prefix='/v1')
# swagger = Swagger(app, template_file='open_api/template.yaml')


def swag_error_handler(exception_error, data, schema):
    exception_message = str(exception_error).split('\n')
    exception_response = (f"Open API schema validation error. {exception_message[0]}. {exception_message[2][:-1]}. "
                          "See log for more information.")
    response = {
        'status': 'ERROR',
        'message': exception_response

    }
    abort(Response(json.dumps(response), status=400))


class PromoScheduler(Resource):
    # @swag_from('open_api/promo_scheduling.yaml', definition='PromoScheduler',
    #            validation=True,
    #            validation_error_handler=swag_error_handler)
    def post(self):
        input_json = request.json
        solution = promo_scheduling(input_json)
        return solution, 200


api.add_resource(PromoScheduler, '/promo_scheduling')
