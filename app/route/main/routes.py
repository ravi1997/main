from flask import jsonify

from app.decorator import logIP
from . import main_bp
from flask import current_app

@logIP
@main_bp.route("/", methods=["GET"])
def index():
    current_app.logger.info("main route called")
    return jsonify({"message":"This is the index page of api/main route:main"}),200

@logIP
@main_bp.route('/<path:path>')
def default_path(path):
    current_app.logger.info("main route path called")
    return jsonify({"message": f"catching {path}"}), 404
