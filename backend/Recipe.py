from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from db import db
from Models import Celebration, Ethnicity, Ingredient, RecipeCelebration, RecipeEthnicity, RecipeIngredient, RecipeModel, RecipeStep, Season, SeasonalRecipe, Tip, User
from schemas import RecipeSchema, TipSchema, EthnicitySchema, IngredientSchema, RecipeStepSchema, RecipeCelebrationSchema
from Models import TipModel, EthnicityModel,CelebrationModel
from translator import translate_text

blp = Blueprint("Recipes", "recipes", description="Operations on recipes")

def is_admin(current_user_id):
    user = User.query.filter_by(UserID=current_user_id).first()
    return user.Role == "admin" if user else False

# Create a new recipe
@blp.route("/recipes")
class RecipeList(MethodView):
    @jwt_required()
    @blp.arguments(RecipeSchema)
    @blp.response(201, RecipeSchema)
    def post(self, recipe_data):
        """
        Create a new recipe.
        """
        user_id = get_jwt_identity()
        existing_recipe = RecipeModel.query.filter(
            RecipeModel.Name.ilike(recipe_data["Name"]),
        ).first()

        if existing_recipe:
            abort(409, message="A recipe with the same name already exists.")

        recipe = RecipeModel(
            Name=recipe_data["Name"],
            Description=recipe_data.get("Description"),
            Difficulty=recipe_data.get("Difficulty"),
            CookingTime=recipe_data.get("CookingTime"),
            Category=recipe_data.get("Category"),
            UserID=user_id,
            Status='Pending',  
        )

        try:
            db.session.add(recipe)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the recipe.")

        return recipe

#get a list of all recipes
    @jwt_required()
    @blp.response(200, RecipeSchema(many=True))
    def get(self):
        """
        Get a list of all recipes.
        """
        current_user = int(get_jwt_identity())
        is_admin_user = is_admin(current_user)

        query = RecipeModel.query

        if not is_admin_user:
            query = query.filter(RecipeModel.Status == "approved")

        recipes = query.all()
        return recipes

# Get recipe by ID
@blp.route("/recipes/<int:recipe_id>")
class RecipeDetail(MethodView):
    @jwt_required()
    @blp.response(200, RecipeSchema)
    def get(self, recipe_id):
        """
        Get details of a specific recipe by ID, including its story, tips, ethnicity, ingredients, and steps.
        """
        user_id = get_jwt_identity()
        jwt_payload = get_jwt()
        current_role = jwt_payload.get("Role", None)

        recipe = (
            RecipeModel.query
            .filter_by(RecipeID=recipe_id)
            .options(
                db.joinedload(RecipeModel.Tips),
                db.joinedload(RecipeModel.ethnicities),
                db.joinedload(RecipeModel.ingredients),
                db.joinedload(RecipeModel.steps),
                db.joinedload(RecipeModel.celebrations),
            )
            .first_or_404()
        )

        if current_role != "admin" and recipe.Status != "approved":
            abort(403, message="You are not authorized to view this recipe.")
        
        return recipe

#update a recipe
    @jwt_required()
    @blp.arguments(RecipeSchema(partial=True))
    @blp.response(200, RecipeSchema)
    def put(self, recipe_data, recipe_id):
        """
        Update an existing recipe.
        """
        user_id = get_jwt_identity()
        jwt_payload = get_jwt()
        current_role = jwt_payload.get("Role", None)

        recipe = RecipeModel.query.get_or_404(recipe_id)

        if recipe.UserID != user_id and current_role != "admin":
            abort(403, message="You are not authorized to update this recipe.")

        for key, value in recipe_data.items():
            setattr(recipe, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the recipe.")

        return recipe

    @jwt_required()
    def delete(self, recipe_id):
        """
        Delete a specific recipe.
        """
        user_id = get_jwt_identity()
        jwt_payload = get_jwt()
        current_role = jwt_payload.get("Role", None)
        recipe = RecipeModel.query.get_or_404(recipe_id)

        if recipe.UserID != user_id and current_role != "admin":
            abort(403, message="You are not authorized to delete this recipe.")

        try:
            db.session.delete(recipe)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the recipe.")

        return {"message": "Recipe deleted successfully."}, 200

# Search for recipes
@blp.route("/recipe/search")
class RecipeSearch(MethodView):
    @jwt_required()
    @blp.response(200, RecipeSchema(many=True))
    def get(self):
        """
        Search for a specific recipe.
        """
        current_user = get_jwt_identity()
        is_admin_user = is_admin(current_user)

        keyword = request.args.get("keyword", "").strip()
        difficulty = request.args.get("Difficulty", "").strip()
        cooking_time = request.args.get("CookingTime", "").strip()
        category = request.args.get("category", "").strip()

        query = RecipeModel.query

        if keyword:
            query = query.filter(RecipeModel.Name.ilike(f"%{keyword}%"))
        if difficulty:
            query = query.filter(RecipeModel.Difficulty.ilike(f"%{difficulty}%"))
        if cooking_time:
            query = query.filter(RecipeModel.CookingTime.ilike(f"%{cooking_time}%"))
        if category:
            query = query.filter(RecipeModel.Category.ilike(f"%{category}%"))

        if not is_admin_user:
            query = query.filter(RecipeModel.Status == "approved")

        recipes = query.all()
        if not recipes:
            return [], 200        
        return recipes

# Approve and Reject Recipe
@blp.route("/recipe/<int:recipe_id>/approve")
class ApproveRecipe(MethodView):
    @jwt_required()
    def put(self, recipe_id):
        """
        Admin approves a recipe.
        """
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            abort(403, message="You are not authorized to approve recipes.")

        recipe = RecipeModel.query.get_or_404(recipe_id)
        recipe.Status = "approved"

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while approving the recipe.")

        return {"message": "Recipe approved successfully.", "recipe_id": recipe.RecipeID, "status": recipe.Status}, 200

@blp.route("/recipe/<int:recipe_id>/reject")
class RejectRecipe(MethodView):
    @jwt_required()
    def put(self, recipe_id):
        """
        Admin rejects a recipe.
        """
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            abort(403, message="You are not authorized to reject recipes.")

        recipe = RecipeModel.query.get_or_404(recipe_id)
        recipe.Status = "rejected"

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while rejecting the recipe.")

        return {"message": "Recipe rejected successfully.", "recipe_id": recipe.RecipeID, "status": recipe.Status}, 200

@blp.route("/users/<int:user_id>/recipes")
class UserRecipes(MethodView):
    @jwt_required()
    @blp.response(200, RecipeSchema(many=True))
    def get(self, user_id):
        """
        Get all recipes created by a specific user.
        """
        current_user_id = get_jwt_identity()

        if int(current_user_id) != int(user_id) and not is_admin(current_user_id):
            abort(403, message="You are not authorized to view these recipes.")

        recipes = RecipeModel.query.filter_by(UserID=user_id).all()
        return recipes




#see alll details related to a recipe
@blp.route("/recipe/<int:recipe_id>/details")
class RecipeDetails(MethodView):
    @jwt_required()
    @blp.response(200)
    def get(self, recipe_id):
        """
        Get all details of a specific recipe including ingredients, steps, tips, ethnicities, celebrations, and seasonal associations.
        """
        recipe = RecipeModel.query.get_or_404(recipe_id, description="Recipe not found.")

        steps = RecipeStep.query.filter_by(RecipeID=recipe_id).order_by(RecipeStep.StepOrder).all()

        ingredients = db.session.query(Ingredient).join(RecipeIngredient).filter(RecipeIngredient.RecipeID == recipe_id).all()
        recipe_ingredients = RecipeIngredient.query.filter_by(RecipeID=recipe_id).all()

        tips = TipModel.query.filter_by(RecipeID=recipe_id).all()

        ethnicities = db.session.query(EthnicityModel).join(RecipeEthnicity, RecipeEthnicity.c.RecipeID == recipe_id).filter(RecipeEthnicity.c.EthnicityID == EthnicityModel.EthnicityID).all()

        celebrations = db.session.query(CelebrationModel).join(RecipeCelebration).filter(RecipeCelebration.c.RecipeID == recipe_id).all()

        seasons = db.session.query(Season).join(SeasonalRecipe).filter(SeasonalRecipe.c.RecipeID == recipe_id).all()

        recipe_details = {
            "RecipeID": recipe.RecipeID,
            "Name": recipe.Name,
            "Description": recipe.Description,
            "Difficulty": recipe.Difficulty,
            "CookingTime": recipe.CookingTime,
            "Category": recipe.Category,
            "Status": recipe.Status,
            "Steps": [{"StepOrder": step.StepOrder, "Content": step.Content} for step in steps],
            "Ingredients": [{"Name": ingredient.Name, "Unit": ingredient.Unit, "Quantity": next((ri.Quantity for ri in recipe_ingredients if ri.IngredientID == ingredient.IngredientID), None)}
                            for ingredient in ingredients],
            "Tips": [{"Content": tip.Content} for tip in tips],
            "Ethnicities": [{"Name": ethnicity.Name, "Description": ethnicity.Description} for ethnicity in ethnicities],
            "Celebrations": [{"Name": celebration.Name, "Description": celebration.Description} for celebration in celebrations],
            "Seasons": [{"Season": season.Season, "Description": season.Description} for season in seasons]
        }

        return recipe_details


#endpoint to translate the recipe data
@blp.route("/recipe/<int:recipe_id>/translate")
class TranslateRecipe(MethodView):
    @jwt_required()  
    def post(self, recipe_id):
        """
        Translate recipe details to a specified target language.
        """
        data = request.get_json()
        target_lang = data.get("target_lang")
        source_lang = data.get("source_lang", "auto")  

        if not target_lang:
            abort(400, message="Target language ('target_lang') must be specified.")
        
        recipe = RecipeModel.query.get_or_404(recipe_id, description="Recipe not found.")

        recipe_details = {
            "Name": recipe.Name,
            "Description": recipe.Description,
            "Difficulty": recipe.Difficulty,
            "CookingTime": recipe.CookingTime,
            "Category": recipe.Category
        }

        try:
            translated_details = {
                key: translate_text(value, source_lang, target_lang)
                for key, value in recipe_details.items()
                if value  
            }
        except Exception as e:
            abort(500, message=f"Translation failed: {str(e)}")

        return {
            "original_details": recipe_details,
            "translated_details": translated_details,
            "target_language": target_lang
        }, 200