from flask_restful import Api
from controllers.api_controllers import UserAPI, UserDetailAPI, AuthAPI, NotFound
from flasgger import Swagger

def register_api_routes(app):
    # 設置 API 和 Swagger
    api = Api(app, prefix='/api', catch_all_404s=True, errors={404: "not found"})
    api.add_resource(UserAPI, '/users', endpoint='user', methods=['POST', 'GET'])
    api.add_resource(UserDetailAPI, '/users/<int:id>', endpoint='user_detail', methods=['GET', 'PUT', 'DELETE'])
    api.add_resource(AuthAPI, '/auth')
    api.add_resource(NotFound, '/404')
    
    # Swagger 配置
    swagger_config = {
        'title': 'User API',
        'uiversion': 3,
        'specs': [
            {
                'endpoint': 'apispec_1',
                'route': '/apispec_1.json',
                'rule_filter': lambda rule: True,
                'model_filter': lambda tag: True,
            }
        ],
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'specs_route': '/apidocs/',
        'headers': []
    }
    
    Swagger(app, config=swagger_config)