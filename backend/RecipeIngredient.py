from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from Models import RecipeIngredient, RecipeModel, Ingredient, User, db
from schemas import RecipeIngredientSchema

blp = Blueprint("RecipeIngredient", "recipe_ingredient", description="Manage ingredients of recipes")

def is_admin():
    user_id = get_jwt_identity()  
    user = User.query.get_or_404(int(user_id))  
    return user.Role == 'admin'

# Get all recipe-ingredients
@blp.route("/recipe-ingredients")
class RecipeIngredientList(MethodView):
    @jwt_required()
    @blp.response(200, RecipeIngredientSchema(many=True))
    def get(self):
        """
        Retrieve all recipes with their associated ingredients.
        """
        query = db.session.query(RecipeIngredient).join(RecipeModel, RecipeModel.RecipeID == RecipeIngredient.RecipeID).join(
            Ingredient, Ingredient.IngredientID == RecipeIngredient.IngredientID
        )

        claims = get_jwt()
        is_admin = claims.get("is_admin", False)

        if not is_admin:
            query = query.filter(RecipeModel.Status == "Approved", Ingredient.Status == "Approved")

        return query.all()

# Get ingredients for a specific recipe
@blp.route("/recipe-ingredients/<int:recipe_id>")
class RecipeIngredientByRecipe(MethodView):
    @jwt_required()
    @blp.response(200, RecipeIngredientSchema(many=True))
    def get(self, recipe_id):
        """
        Retrieve ingredients for a specific recipe by RecipeID.
        """
        query = db.session.query(RecipeIngredient).filter(RecipeIngredient.RecipeID == recipe_id).join(
            RecipeModel, RecipeModel.RecipeID == RecipeIngredient.RecipeID
        ).join(Ingredient, Ingredient.IngredientID == RecipeIngredient.IngredientID)

        claims = get_jwt()
        is_admin = claims.get("is_admin", False)

        if not is_admin:
            query = query.filter(RecipeModel.Status == "Approved", Ingredient.Status == "Approved")

        return query.all()

# Search recipe ingredients by recipe name or ingredient name
@blp.route("/recipe-ingredients/search")
class RecipeIngredientSearch(MethodView):
    @jwt_required()
    @blp.response(200, RecipeIngredientSchema(many=True))
    def get(self):
        """
        Search recipe ingredients by recipe name or ingredient name.
        """
        recipe_name = request.args.get("recipe_name", "").strip()
        ingredient_name = request.args.get("ingredient_name", "").strip()

        query = db.session.query(RecipeIngredient).join(RecipeModel, RecipeModel.RecipeID == RecipeIngredient.RecipeID).join(
            Ingredient, Ingredient.IngredientID == RecipeIngredient.IngredientID
        )

        if recipe_name:
            query = query.filter(RecipeModel.Name.ilike(f"%{recipe_name}%"))
        if ingredient_name:
            query = query.filter(Ingredient.Name.ilike(f"%{ingredient_name}%"))

        claims = get_jwt()
        is_admin = claims.get("is_admin", False)

        if not is_admin:
            query = query.filter(RecipeModel.Status == "Approved", Ingredient.Status == "Approved")

        return query.all()

# Associate a recipe with an ingredient
@blp.route("/recipe-ingredients")
class RecipeIngredientCreate(MethodView):
    @jwt_required()
    @blp.arguments(RecipeIngredientSchema)
    @blp.response(201, RecipeIngredientSchema)
    def post(self, data):
        """
        Associate a recipe with an ingredient (create a new RecipeIngredient entry).
        """
        recipe = RecipeModel.query.filter_by(RecipeID=data["RecipeID"]).first()
        ingredient = Ingredient.query.filter_by(IngredientID=data["IngredientID"]).first()

        if not recipe:
            abort(404, message="Recipe not found.")
        if not ingredient:
            abort(404, message="Ingredient not found.")

        claims = get_jwt()
        user_id = claims["sub"]
        is_admin = claims.get("is_admin", False)

        # if recipe.UserID != user_id and not is_admin:
        #     abort(403, message="You do not have permission to associate ingredients with this recipe.")

        # if recipe.Status != "Approved" or ingredient.Status != "Approved":
        #     abort(400, message="Both the recipe and ingredient must be approved to associate them.")

        if RecipeIngredient.query.filter_by(
            RecipeID=data["RecipeID"], IngredientID=data["IngredientID"]
        ).first():
            abort(400, message="This association already exists.")

        recipe_ingredient = RecipeIngredient(**data)
        db.session.add(recipe_ingredient)
        db.session.commit()

        return recipe_ingredient

# Update the quantity of an ingredient in a recipe
@blp.route("/recipe-ingredients/<int:recipe_id>/<int:ingredient_id>")
class RecipeIngredientDetail(MethodView):
    @jwt_required()
    @blp.arguments(RecipeIngredientSchema(partial=True))
    @blp.response(200, RecipeIngredientSchema)
    def put(self, data, recipe_id, ingredient_id):
        """
        Update the quantity of an ingredient in a recipe.
        """
        recipe_ingredient = RecipeIngredient.query.filter_by(
            RecipeID=recipe_id, IngredientID=ingredient_id
        ).first()

        if not recipe_ingredient:
            abort(404, message="Recipe-ingredient association not found.")

        recipe = RecipeModel.query.filter_by(RecipeID=recipe_id).first()
        claims = get_jwt()
        user_id = claims["sub"]
        is_admin = claims.get("is_admin", False)

        # if recipe.UserID != user_id and not is_admin:
        #     abort(403, message="You do not have permission to update this association.")

        if "Quantity" in data:
            recipe_ingredient.Quantity = data["Quantity"]

        db.session.commit()
        return recipe_ingredient

# Remove an ingredient from a recipe
@blp.route("/recipe-ingredients/<int:recipe_id>/<int:ingredient_id>")
class RecipeIngredientDelete(MethodView):
    @jwt_required()
    @blp.response(200)
    def delete(self, recipe_id, ingredient_id):
        """
        Remove an ingredient from a recipe.
        """
        recipe_ingredient = RecipeIngredient.query.filter_by(
            RecipeID=recipe_id, IngredientID=ingredient_id
        ).first()

        if not recipe_ingredient:
            abort(404, message="Recipe-ingredient association not found.")

        recipe = RecipeModel.query.filter_by(RecipeID=recipe_id).first()
        claims = get_jwt()
        user_id = claims["sub"]
        is_admin = claims.get("is_admin", False)

        # if recipe.UserID != user_id and not is_admin:
        #     abort(403, message="You do not have permission to remove this association.")

        db.session.delete(recipe_ingredient)
        db.session.commit()

        return {"message": "Ingredient removed from the recipe."}, 200
