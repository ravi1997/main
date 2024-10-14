import json
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from app.config import ProdConfig
from app.logger import SQLAlchemyHandler
from app.util import get_blueprint, get_default_instance, list_routes_by_blueprint
from .extension import db, migrate, bcrypt, scheduler
from .route.main import main_bp
from .route.superadmin import superadmin_bp
from app.extra import job_listener
from apscheduler.events import EVENT_JOB_EXECUTED
from app.db_initializer import empty_db_command
from .models import Account, Application,Role

def create_app():
	app = Flask(__name__)
	app.config.from_object(ProdConfig)
	db.init_app(app)
	migrate.init_app(app, db)
	bcrypt.init_app(app)
	scheduler.init_app(app)
	scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED)
	CORS(app)
	scheduler.start()


	app.cli.add_command(empty_db_command)

	sql_handler = SQLAlchemyHandler()
	sql_handler.setLevel(logging.INFO)
	formatter = logging.Formatter(
		"%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
	)
	sql_handler.setFormatter(formatter)
	app.logger.addHandler(sql_handler)
	app.logger.setLevel(logging.INFO)
	app.logger.info("Flask app startup")

	baseurl = "/api/main"

	app.register_blueprint(main_bp, url_prefix=baseurl)		
	app.register_blueprint(superadmin_bp, url_prefix=f"{baseurl}/superadmin")
	
	role_bp = get_blueprint(Role)
	application_bp = get_blueprint(Application)
	account_bp = get_blueprint(Account)
	
	app.register_blueprint(role_bp, url_prefix=f"{baseurl}/roles")
	app.register_blueprint(application_bp, url_prefix=f"{baseurl}/application")
	app.register_blueprint(account_bp, url_prefix=f"{baseurl}/account")


	return app
