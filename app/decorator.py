#decorator
from functools import wraps

from flask import jsonify, request,current_app


def logIP(f):
	@wraps(f)
	def decorated_function(*args,**kwargs):
		url =  request.url
		if request.headers.getlist("X-Forwarded-For"):
			ip_address = request.headers.getlist("X-Forwarded-For")[0]
		else:
			ip_address = request.remote_addr
		current_app.logger.info(f"{ip_address} trying to access {url}")
		return f(*args, **kwargs)
	return decorated_function


def verify_body(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		request_data = request.json
		
		if request_data is None:
			return jsonify({"message":"Invalid request data format"}),400
		
		return f(request_data,*args, **kwargs)
	return decorated_function

