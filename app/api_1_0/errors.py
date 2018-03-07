from flask import jsonify
from . import api

@api.app_errorhandler(404)
def route_not_found(e):
    response = jsonify({"error":"route not found"})
    response.status_code = 404
    return response

@api.app_errorhandler(500)
def server_error(e):
    response = jsonify({"error":"server error"})
    response.status_code = 500
    return response
