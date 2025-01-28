from datetime import timedelta
from flask import Flask 
from flask_smorest import Api 
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_cors import CORS
from db import db 
from seed import seed_data
import os
from Models import *
from Resources.Feedback import blp as feedback_blueprint 
from Resources.Celebration import blp as celebration_blueprint 
from Resources.User import blp as user_blueprint
from Resources.Recipe import blp as recipe_blueprint
from Resources.RecipeCelebration import blp as recipe_celebration_blueprint 
from Resources.RecipeEthnicity import blp as recipe_ethnicity_blueprint 
from Resources.RecipeIngredient import blp as recipe_ingredient_blueprint 
from Resources.RecipeStep import blp as recipe_step_blueprint 
from Resources.SeasonalRecipe import blp as seasonal_recipe_blueprint 
from Resources.Season import blp as season_blueprint 
from Resources.Tip import blp as tip_blueprint 
from Resources.Ethnicity import blp as ethnicity_blueprint 
from Resources.Ingredient import blp as ingredient_blueprint 
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec


load_dotenv()
BLOCKLIST = set()

def schema_name_resolver(schema):
    return f"{schema.__module__}.{schema.__class__.__name__}"

def create_app(db_url=None):
    app = Flask(__name__)
    CORS(app)
    #application configuration
    app.config["PROPAGATE_EXCEPTIONS"]= True
    app.config["API_TITLE"]= "Tunisian Culinary Chronicles"
    app.config["API_VERSION"]= "RELEASE 1"
    app.config["OPENAPI_VERSION"]= "3.0.3"
    app.config["OPENAPI_URL_PREFIX"]= "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"]= "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"]= "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    #app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL" , "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY","ranim2002")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2) 
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)   
    #initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        """
        Callback function to check if a token is in the blocklist.
        """
        return jwt_payload["jti"] in BLOCKLIST
    
    # Initialize API with schema resolver
    api = Api(app)
    api.spec.components.schema_name_resolver = schema_name_resolver

    
    #Register Blueprints
    api.register_blueprint(feedback_blueprint)
    api.register_blueprint(celebration_blueprint) 
    api.register_blueprint(user_blueprint)
    api.register_blueprint(recipe_blueprint)
    api.register_blueprint(recipe_celebration_blueprint) 
    api.register_blueprint(recipe_ethnicity_blueprint)
    api.register_blueprint(recipe_ingredient_blueprint) 
    api.register_blueprint(recipe_step_blueprint) 
    api.register_blueprint(seasonal_recipe_blueprint) 
    api.register_blueprint(season_blueprint) 
    api.register_blueprint(tip_blueprint) 
    api.register_blueprint(ethnicity_blueprint) 
    api.register_blueprint(ingredient_blueprint) 
    

    with app.app_context():
        db.create_all()
        seed_data()    

        # Check if the admin already exists and create a predefined admin
        if not User.query.filter_by(Email="sayahi.ranim@gmail.com").first():

            admin = User(
                Username="RanimSA",
                Email="sayahi.ranim@gmail.com",
                Role="admin"
            )
            admin.set_password("ranim2002")  
            db.session.add(admin)
            db.session.commit()
            print("Admin account created successfully!")
        else:
            print("Admin account already exists.")

    return app

