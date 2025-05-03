from flask import Flask

def register_routes(app):
    from routes.web import register_web_routes
    from routes.api import register_api_routes
    
    register_web_routes(app)
    register_api_routes(app)
