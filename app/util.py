		
# UTILS
from .extension import db
from datetime import datetime, timedelta
import random
import string
import requests


def list_routes_by_blueprint(app):
	# app.logger.info("Routes by Blueprint:")
	result = {}
	for blueprint_name, blueprint in app.blueprints.items():
		# app.logger.info(f"Blueprint: {blueprint_name}")
		result[blueprint_name] = []
		for rule in app.url_map.iter_rules():
			if rule.endpoint.startswith(f"{blueprint_name}."):
				methods = rule.methods
				methods.discard('OPTIONS')
				methods.discard('HEAD')
				result[blueprint_name].append({
					"URL":f"{rule}",
					"Endpoint": f"{rule.endpoint}",
					"Methods" : f"{methods}"
				})
				
				# app.logger.info(f"  URL: {rule}, Endpoint: {rule.endpoint}, Methods: {rule.methods}")
	return result


def get_default_instance(cls):
	"""
	Returns a default instance of the specified class with default attribute values.
	Provides default values based on column types if no default is defined.

	Args:
		cls: The class for which the default instance is to be created.

	Returns:
		An instance of the specified class with default values.
	"""
	default_values = {}

	# Define default values based on column type
	type_defaults = {
		db.Integer: 0,
		db.String: '',        # Default for VARCHAR (String)
		db.Float: 0.0,
		db.Boolean: False,
		db.DateTime: None,
		db.Date: None,
		db.Time: None,
	}

	# Inspect the class's columns and their default values
	for column in cls.__table__.columns:
		# Use the default value from the model if defined
		if column.default:
			if callable(column.default.arg):
				default_values[column.name] = column.default.arg()
			else:
				default_values[column.name] = column.default.arg
		# Provide a default value based on the column type if no default is defined
		elif isinstance(column.type, db.String):  # Handle VARCHAR specifically
			default_values[column.name] = ''
		elif isinstance(column.type, db.Integer):  # Handle INTEGER specifically
			default_values[column.name] = 0
		elif isinstance(column.type, db.Float):  # Handle FLOAT specifically
			default_values[column.name] = 0.0
		elif isinstance(column.type, db.Boolean):  # Handle BOOLEAN specifically
			default_values[column.name] = False
		elif isinstance(column.type, db.DateTime):  # Handle DATETIME specifically
			default_values[column.name] = None
		elif isinstance(column.type, db.Date):  # Handle DATE specifically
			default_values[column.name] = None
		elif isinstance(column.type, db.Time):  # Handle TIME specifically
			default_values[column.name] = None
		# If a column is required and no default value is set, raise an error
		elif not column.nullable:
			raise ValueError(f"Required field '{column.name}' is missing a default value and is not nullable.")

	# Create an instance using the provided class with the default values
	default_instance = cls(**default_values)
	
	return default_instance


def get_blueprint(cls):
	return get_default_instance(cls).blueprint


def send_sms(mobile,password):
	# Data for the POST request
	data = {
		'username': 'Aiims',
		'password': 'Aiims@123',
		'senderid': 'AIIMSD',
		'mobileNos': mobile,
		'message': f'your new password is {password}. Login to RPC waitinglist',
		'templateid1': '1307161579789431013'
	}

	# Headers for the POST request
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded'
	}

	# URL of the service
	url = 'http://192.168.14.30/sms_service/Service.asmx/sendSingleSMS'

	# Send the POST request
	response = requests.post(url, data=data, headers=headers)

	# Return the response from the SMS service
	return response.status_code


def send_ehospital_init():
	# Data for the POST request
	data = {
		'username': 'rpcapi',
		'password': 'Rpcapi@123',
	}

	# Headers for the POST request
	headers = {
		'Content-Type': 'application/json'
	}

	# URL of the service
	url = 'http://ehospitalapi.aiims.edu/patient/init'

	# Send the POST request
	response = requests.post(url, data=data, headers=headers)

	if response.status_code == 200 or response.status_code == 201:
		response_data = response.json()
		# Get the token from the response
		token = response_data.get('token')
		# Return the response from the SMS service
		return token

	else:
		return ""

def send_ehospital_uhid(uhid):

	token = send_ehospital_init()

	if token == "":
		return None

	# Data for the POST request
	data = {
		'hospital_id': 4,
		'reg_no': uhid,
	}

	# Headers for the POST request
	headers = {
		'Content-Type': 'application/json',
		'Authorization': f'Bearer {token}'
	}

	# URL of the service
	url = 'http://ehospitalapi.aiims.edu/patient/fetchPatientFullDetails'

	# Send the POST request
	response = requests.post(url, data=data, headers=headers)

	if response.status_code == 200 or response.status_code == 201:
		response_data = response.json()
		# Get the token from the response
		patientDetails = response_data.get('patientDetails')
		# Return the response from the SMS service
		return patientDetails

	else:
		return ""

def to_date(date_string): 
	try:
		return datetime.strptime(date_string, "%Y-%m-%d").date()
	except ValueError:
		raise ValueError('{} is not valid date in the format YYYY-MM-DD'.format(date_string))

def randomword(length):
	letters = 'abcdefghijklmnopqrstuvwxyz'
	return ''.join(random.choice(letters) for i in range(length))

def generate_random_phone_number():
	# Generate a random 10-digit number (excluding any specific formatting)
	number = ''.join(random.choices('0123456789', k=10))
	
	# Format the number as a typical phone number (e.g., ###-###-####)
	formatted_number = f'{number[:3]}-{number[3:6]}-{number[6:]}'
	
	return formatted_number

def generate_random_dob(start_date='1970-01-01', end_date='2005-12-31'):
	# Convert start_date and end_date to datetime objects
	start_date = datetime.strptime(start_date, '%Y-%m-%d')
	end_date = datetime.strptime(end_date, '%Y-%m-%d')
	
	# Calculate the range in days
	delta = end_date - start_date
	random_days = random.randint(0, delta.days)
	
	# Generate a random date within the specified range
	random_dob = start_date + timedelta(days=random_days)
	
	return random_dob.date()

def generate_strong_password(length=10):
	# Define characters to use in the password
	characters = string.ascii_letters + string.digits + string.punctuation
	
	# Generate password
	password = ''.join(random.choice(characters) for _ in range(length))
	
	return password

