from flask import jsonify

from app.decorator import logIP
from app.util import list_routes_by_blueprint
from . import superadmin_bp
from flask import current_app

@logIP
@superadmin_bp.route("/", methods=["GET"])
def index():
    current_app.logger.info("super admin index route called")
    return jsonify({"message":"This is the index page of api/superadmin route:superadmin"}),200


@logIP
@superadmin_bp.route("/routes", methods=["GET"])
def routes_path():
    current_app.logger.info("super admin routes route called")
    return jsonify(list_routes_by_blueprint(current_app)),200

