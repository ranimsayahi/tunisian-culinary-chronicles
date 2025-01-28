from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from Models import SeasonalRecipe, RecipeModel, Season, db
from schemas import RecipeSchema, SeasonalRecipeSchema

blp = Blueprint("SeasonalRecipes", "seasonal_recipes", description="Manage seasonal recipes")

#Get all recipes for a specific season, with recipe details and corresponding season information.
@blp.route("/seasons/<int:season_id>/recipes")
class SeasonalRecipeList(MethodView):
    @jwt_required()
    @blp.response(200, RecipeSchema(many=True))
    def get(self, season_id):
        """
        Get all recipes for a specific season, with recipe details and corresponding season information.
        """
        season = Season.query.get_or_404(season_id, description="Season not found.")

        recipes = (
            db.session.query(RecipeModel)
            .join(SeasonalRecipe, RecipeModel.RecipeID == SeasonalRecipe.c.RecipeID)  
            .filter(SeasonalRecipe.c.SeasonID == season_id)  
            .all()
        )

        claims = get_jwt()
        if not claims.get("is_admin", False):
            recipes = [recipe for recipe in recipes if recipe.Status == "Approved"]

        for recipe in recipes:
            recipe.Season = season 

        return recipes


#add recipe to a season 
@blp.route("/seasons/<int:season_id>/recipes")
class SeasonalRecipeList(MethodView):
    @jwt_required()
    @blp.arguments(SeasonalRecipeSchema)
    @blp.response(201, SeasonalRecipeSchema)
    def post(self, data, season_id):
        """
        Add a recipe to a season.
        """
        claims = get_jwt()
        if not claims.get("is_admin", False): 
            abort(403, message="Admins only can add seasonal recipes.")
        
        season = Season.query.get_or_404(season_id, description="Season not found.")
        recipe = RecipeModel.query.get_or_404(data["RecipeID"], description="Recipe not found.")

        existing = db.session.execute(
            db.select(SeasonalRecipe).filter_by(SeasonID=season_id, RecipeID=data["RecipeID"])
        ).scalar()

        if existing:
            abort(409, message="Recipe already added to this season.")

        db.session.execute(
            SeasonalRecipe.insert().values(SeasonID=season_id, RecipeID=data["RecipeID"])
        )
        db.session.commit()
        return data


#remove a recipe from a season
@blp.route("/seasons/<int:season_id>/recipes/<int:recipe_id>")
class SeasonalRecipeDeleteAPI(MethodView):
    @jwt_required()
    @blp.response(204)
    def delete(self, season_id, recipe_id):
        """
        Remove a recipe from a season.
        """
        claims = get_jwt()
        if not claims.get("is_admin", False):  
            abort(403, message="Admins only can remove seasonal recipes.")

        print(f"SeasonID: {season_id}, RecipeID: {recipe_id}")

        seasonal_recipe = db.session.execute(
            db.select(SeasonalRecipe)
            .filter_by(SeasonID=season_id, RecipeID=recipe_id)
        ).scalar()

        print(f"Found seasonal recipe: {seasonal_recipe}")

        if not seasonal_recipe:
            abort(404, message="Seasonal recipe not found.")

        db.session.execute(
            SeasonalRecipe.delete().where(SeasonalRecipe.c.SeasonID == season_id)
            .where(SeasonalRecipe.c.RecipeID == recipe_id)
        )
        db.session.commit()

        return {"message": "Recipe removed from the season."}





#search for a recipe by name or season
@blp.route("/recipes/search")
class RecipeSearch(MethodView):
    @jwt_required()
    @blp.response(200, RecipeSchema(many=True))
    def get(self):
        """
        Search recipes by name or associated season.
        """
        name = request.args.get("name", "").strip()
        season = request.args.get("season", "").strip()

        query = db.session.query(RecipeModel).join(SeasonalRecipe, RecipeModel.RecipeID == SeasonalRecipe.c.RecipeID)

        if name:
            query = query.filter(RecipeModel.Name.ilike(f"%{name}%"))

        if season:
            query = query.join(Season, SeasonalRecipe.c.SeasonID == Season.SeasonID).filter(Season.Season.ilike(f"%{season}%"))

        claims = get_jwt()
        is_admin = claims.get("is_admin", False)

        if not is_admin:
            query = query.filter(RecipeModel.Status == "Approved")

        recipes = query.all()

        return recipes
