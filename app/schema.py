from app.extension import ma
from app.models import *
from marshmallow import fields

# SCHEMAS
class ApplicationSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Application
		include_fk = True
		include_relationships = True
		load_instance = True