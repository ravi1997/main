from flask import send_from_directory

from app.decorator import logIP
from . import main_bp
from flask import current_app

@logIP
@main_bp.route("/", methods=["GET"])
def index():
    current_app.logger.info("main route called")
    return send_from_directory(current_app.static_folder, 'index.html')

