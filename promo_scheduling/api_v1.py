from flask import request
from flask_restful import Resource
from flask_restful import Api
from promo_scheduling.promo_scheduling import promo_scheduling


class PromoScheduler(Resource):
    def post(self):
        input_json = request.json
        solution = promo_scheduling(input_json, ret_type='str')
        return solution, 200


def create_api(app):
    api = Api(app=app, prefix='/v1')
    api.add_resource(PromoScheduler, '/promo_scheduling')
