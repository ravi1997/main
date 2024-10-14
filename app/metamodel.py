import traceback
from flask import Blueprint, current_app, jsonify, request
from flask_sqlalchemy.model import DefaultMeta
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.decorator import logIP
from app.extension import db



class RouteMeta(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    _custom_routes = []

    def __init__(self, derived,id=None):
        self.model = derived
        if id is not None:
            self.id = id
        derived.blueprint = self.create_blueprint()
        derived.Schema = self.create_schema()
        derived._custom_routes = []
        self.register_routes()

    def create_schema(self):
        from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
        
        class ModelSchema(SQLAlchemyAutoSchema):
            class Meta:
                model = self.model
                load_instance = True
                sqla_session = db.session
        return ModelSchema

    def create_blueprint(self):
        blueprint = Blueprint(self.model.__class__.__name__, __name__)

        @blueprint.route('/', methods=['GET'])
        def index_instance():
            return jsonify({"message": f"This is the index route for the {self.model.__class__.__name__}"}), 200

        @blueprint.route('/', methods=['POST'])
        def create_instance():
            data = request.json
            try:
                new_instance = self.create(**data)
                return jsonify(self.model.Schema().dump(new_instance)), 201
            except ValueError as e:
                current_app.logger.info(traceback.format_exc())
                return jsonify({'error': str(e)}), 400

        @blueprint.route('/<int:id>', methods=['GET'])
        def get_instance(id):
            try:
                instance = self.read(id)
                return jsonify(instance), 200
            except ValueError as e:
                return jsonify({'error': str(e)}), 404

        @blueprint.route('/<int:id>', methods=['PUT'])
        def update_instance(id):
            data = request.json
            try:
                updated_instance = self.update(id, **data)
                return jsonify(updated_instance), 200
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

        @blueprint.route('/<int:id>', methods=['DELETE'])
        def delete_instance(id):
            try:
                message = self.delete(id)
                return jsonify(message), 200
            except ValueError as e:
                return jsonify({'error': str(e)}), 404

        @blueprint.route('/list', methods=['GET'])
        def list_instances():
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            instances = self.list(page=page, per_page=per_page)
            return jsonify(instances), 200

        @blueprint.route('/search', methods=['GET'])
        def search_instances():
            criteria = request.args.to_dict()
            instances = self.search(**criteria)
            return jsonify(instances), 200

        @blueprint.route('/count', methods=['GET'])
        def count_instances():
            criteria = request.args.to_dict()
            count = self.count(**criteria)
            return jsonify({'count': count}), 200

        @blueprint.route('/exists', methods=['GET'])
        def exists_instances():
            criteria = request.args.to_dict()
            exists = self.exists(**criteria)
            return jsonify({'exists': exists}), 200

        @blueprint.route('/all', methods=['GET'])
        def read_all_instances():
            instances = self.read_all()
            return jsonify(instances), 200

        return blueprint

    def create(self, **kwargs):
        schema = self.model.Schema()
        errors = schema.validate(kwargs,session=db.session)
        if errors:
            raise ValueError(f"Validation errors: {errors}")
    
        instance = schema.load(kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def read(self, id):
        instance = self.model.__class__.query.get(id)
        if instance is None:
            raise ValueError(f"{self.model.__class__.__name__} with id {id} not found.")
        
        schema = self.model.Schema()
        return schema.dump(instance)

    def update(self, id, **kwargs):
        instance = self.model.__class__.query.get(id)
        if instance is None:
            raise ValueError(f"{self.model.__class__.__name__} with id {id} not found.")
        
        schema = self.model.Schema()
        errors = schema.validate(kwargs)
        if errors:
            raise ValueError(f"Validation errors: {errors}")
        
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.session.commit()
        return schema.dump(instance)

    def delete(self, id):
        instance = self.model.__class__.query.get(id)
        if instance is None:
            raise ValueError(f"{self.model.__class__.__name__} with id {id} not found.")
        
        db.session.delete(instance)
        db.session.commit()
        return {'message': f"{self.model.__class__.__name__} with id {id} deleted."}

    def list(self, page=1, per_page=10):
        instances = self.model.__class__.query.paginate(page, per_page, False)
        schema = self.model.__class__.Schema(many=True)
        return schema.dump(instances.items)

    def search(self, **criteria):
        instances = self.model.__class__.query.filter_by(**criteria).all()
        schema = self.model.Schema(many=True)
        return schema.dump(instances)

    def count(self, **criteria):
        return self.model.__class__.query.filter_by(**criteria).count()

    def exists(self, **criteria):
        return self.model.__class__.query.filter_by(**criteria).first() is not None

    def read_all(self):
        instances = self.model.__class__.query.all()
        schema = self.model.Schema(many=True)
        return schema.dump(instances)

    def register_routes(self):
        for name, func in self.model.__class__.__dict__.items():
            if callable(func) and hasattr(func, '_route'):
                route_info = getattr(func, '_route')
                self.model.blueprint.add_url_rule(route_info['rule'], endpoint=name, view_func=func, **route_info['options'])

        for name, rule, endpoint, view_func, options in self.model._custom_routes:
            if self.model.__tablename__ == name:
                self.model.blueprint.add_url_rule(rule, endpoint, view_func, **options)

        for name, rule, endpoint, view_func, options in RouteMeta._custom_routes:
            if self.model.__tablename__ == name:
                route_info = getattr(view_func, '_route')
                defaults = route_info.get('defaults', {})
                defaults['cls']=globals().get(self.model.__class__.__name__)
                self.model.blueprint.add_url_rule(rule, endpoint, view_func,defaults=defaults, **options)

    @classmethod
    def add_custom_route(cls, rule, endpoint=None, view_func=None, **options):
        if not endpoint and view_func is not None:
            endpoint = view_func.__name__
        cls._custom_routes.append((rule, endpoint, view_func, options))
        cls.blueprint.add_url_rule(rule, endpoint, view_func, **options)

    @classmethod
    def route(cls, name, rule, endpoint=None, **options):
        def decorator(func):
            if not hasattr(func, '_route'):
                func._route = {'rule': rule, 'options': options}
            cls._custom_routes.append((name, rule, endpoint, func, options))
            return func
        return decorator
