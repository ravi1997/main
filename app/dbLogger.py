from datetime import datetime
from app.extension import db


class Log(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	level = db.Column(db.String(50), nullable=False)
	message = db.Column(db.String(500), nullable=False)
	pathname = db.Column(db.String(500), nullable=False)
	lineno = db.Column(db.Integer, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
