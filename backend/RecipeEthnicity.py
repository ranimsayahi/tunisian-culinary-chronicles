from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from flask import abort
from sqlalchemy import text
from Models import RecipeEthnicity, RecipeModel, EthnicityModel  # Use EthnicityModel instead of CelebrationModel
from db import db
from schemas import RecipeEthnicitySchema, RecipeSchema
from sqlalchemy.orm import aliased
from sqlalchemy.exc import SQLAlchemyError


blp = Blueprint("recipe_ethnicities", __name__, description="Operations on Recipe Ethnicities")

# Associate a Recipe with an Ethnicity
@blp.route("/recipe-ethnicities")
class RecipeEthnicityCreateAPI(MethodView):
    @jwt_required()
    @blp.arguments(RecipeEthnicitySchema)
    @blp.response(201, RecipeEthnicitySchema)
    def post(self, data):
        """
        Associate a recipe with an ethnicity.
        """
        recipe = RecipeModel.query.get(data["RecipeID"])
        ethnicity = EthnicityModel.query.get(data["EthnicityID"])

        if not recipe or not ethnicity:
            abort(404, message="Recipe or Ethnicity not found.")

        claims = get_jwt()
        user_id = claims["sub"]
        is_admin = claims.get("is_admin", False)

        if recipe.UserID != user_id and not is_admin:
            abort(403, message="You do not have permission to associate this ethnicity with the recipe.")

        # Check if the association already exists
        existing_association = db.session.execute(
            db.select(RecipeEthnicity)
            .where(RecipeEthnicity.c.RecipeID == data["RecipeID"])
            .where(RecipeEthnicity.c.EthnicityID == data["EthnicityID"])
        ).fetchone()

        if existing_association:
            abort(400, message="This association already exists.")

        # Insert the new association
        try:
            db.session.execute(
                RecipeEthnicity.insert().values(
                    RecipeID=data["RecipeID"],
                    EthnicityID=data["EthnicityID"]
                )
            )
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while saving the association: {str(e)}")

        return data


# Retrieve all Recipe-Ethnicity associations
@blp.route("/recipe-ethnicities")
class RecipeEthnicityListAPI(MethodView):
    @jwt_required()
    @blp.response(200, RecipeEthnicitySchema(many=True))
    def get(self):
        """
        Retrieve all recipe-ethnicity associations.
        """
        associations = db.session.execute(
            db.select(RecipeEthnicity.c.RecipeID, RecipeEthnicity.c.EthnicityID)
        ).fetchall()

        if not associations:
            abort(404, message="No associations found.")

        return [{"RecipeID": assoc.RecipeID, "EthnicityID": assoc.EthnicityID} for assoc in associations]


# Retrieve all Ethnicities associated with a specific Recipe
@blp.route("/recipe-ethnicities/<int:recipe_id>")
class RecipeEthnicityByRecipeAPI(MethodView):
    @jwt_required()
    @blp.response(200, RecipeEthnicitySchema(many=True))
    def get(self, recipe_id):
        """
        Retrieve all ethnicities associated with a specific recipe.
        """
        associations = db.session.execute(
            db.select(EthnicityModel.EthnicityID, EthnicityModel.Name)
            .join(RecipeEthnicity, EthnicityModel.EthnicityID == RecipeEthnicity.c.EthnicityID)
            .where(RecipeEthnicity.c.RecipeID == recipe_id)
        ).fetchall()

        if not associations:
            abort(404, message="No associations found for this recipe.")

        return [{"EthnicityID": assoc.EthnicityID, "Name": assoc.Name} for assoc in associations]



# Update a Recipe-Ethnicity association
@blp.route("/ethnicities/<int:ethnicity_id>/recipes/<int:recipe_id>")
class RecipeEthnicityUpdateAPI(MethodView):
    @jwt_required()
    @blp.arguments(RecipeEthnicitySchema(partial=True))
    @blp.response(200, RecipeEthnicitySchema)
    def put(self, data, ethnicity_id, recipe_id):
        """
        Update the association between a recipe and an ethnicity.
        """
        claims = get_jwt()
        user_id = claims["sub"]
        is_admin = claims.get("is_admin", False)

        recipe = RecipeModel.query.get(recipe_id)
        if not recipe:
            abort(404, message="Recipe not found.")

        # if recipe.UserID != user_id and not is_admin:
        #     abort(403, message="You do not have permission to update this association.")

        # Update EthnicityID if provided
        if "EthnicityID" in data:
            try:
                db.session.execute(
                    RecipeEthnicity.update()
                    .where(RecipeEthnicity.c.RecipeID == recipe_id)
                    .where(RecipeEthnicity.c.EthnicityID == ethnicity_id)
                    .values(EthnicityID=data["EthnicityID"])
                )
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                abort(500, message=f"An error occurred while updating the association: {str(e)}")

        return {"RecipeID": recipe_id, "EthnicityID": data["EthnicityID"]}


# Remove an Ethnicity from a Recipe
@blp.route("/recipe-ethnicities/<int:recipe_id>/<int:ethnicity_id>", methods=["DELETE"])
class RecipeEthnicityDeleteAPI(MethodView):
    @jwt_required()
    @blp.response(200)
    def delete(self, recipe_id, ethnicity_id):
        """
        Remove an ethnicity from a recipe.
        """
        claims = get_jwt()
        user_id = claims["sub"]
        is_admin = claims.get("is_admin", False)

        # Fetch the recipe by its ID
        recipe = RecipeModel.query.get(recipe_id)
        if not recipe:
            abort(404, message="Recipe not found.")

        # Check if the user has permission to modify the recipe
        if recipe.UserID != user_id and not is_admin:
            abort(403, message="You do not have permission to remove this ethnicity.")

        # Check if the ethnicity association exists
        existing_association = db.session.execute(
            db.select(RecipeEthnicity)
            .where(RecipeEthnicity.c.RecipeID == recipe_id)
            .where(RecipeEthnicity.c.EthnicityID == ethnicity_id)
        ).fetchone()

        if not existing_association:
            abort(404, message="This ethnicity is not associated with the specified recipe.")

        # Delete the association
        try:
            db.session.execute(
                RecipeEthnicity.delete()
                .where(RecipeEthnicity.c.RecipeID == recipe_id)
                .where(RecipeEthnicity.c.EthnicityID == ethnicity_id)
            )
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the association: {str(e)}")

        return {"message": "Ethnicity removed from the recipe."}



# Retrieve all Recipes associated with a specific Ethnicity
@blp.route("/ethnicities/<string:ethnicity_name>/recipes")
class RecipesByEthnicityAPI(MethodView):
    @jwt_required()
    @blp.response(200, RecipeSchema(many=True))
    def get(self, ethnicity_name):
        """
        Get all recipes associated with a specific ethnicity.
        """
        recipes = db.session.query(RecipeModel).join(RecipeEthnicity).join(EthnicityModel).filter(
            EthnicityModel.Name == ethnicity_name
        ).all()

        if not recipes:
            abort(404, message=f"No recipes found for the ethnicity '{ethnicity_name}'.")

        return recipes