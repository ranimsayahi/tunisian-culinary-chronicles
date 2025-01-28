from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from flask import abort
from Models import RecipeCelebration, RecipeModel, CelebrationModel
from db import db
from schemas import RecipeCelebrationSchema, RecipeSchema

blp = Blueprint("recipe_celebrations", __name__, description="Operations on Recipe Celebrations")

#create
from sqlalchemy import text

@blp.route("/recipe-celebrations")
class RecipeCelebrations(MethodView):
    @jwt_required()
    @blp.response(200, RecipeCelebrationSchema(many=True))
    def get(self):
        """
        Retrieve all recipe-celebration associations with full details.
        """
        claims = get_jwt()
        is_admin = claims.get("is_admin", False)

        # Build the query for recipe-celebration associations
        if is_admin:
            # For admin users, retrieve all associations
            associations = db.session.execute(
                text("""
                    SELECT RecipeCelebrations.RecipeID, RecipeCelebrations.CelebrationID
                    FROM RecipeCelebrations
                    JOIN Recipe ON Recipe.RecipeID = RecipeCelebrations.RecipeID
                    JOIN Celebration ON Celebration.CelebrationID = RecipeCelebrations.CelebrationID
                """)
            ).fetchall()
        else:
            # For non-admin users, filter by approved recipe and celebration statuses
            associations = db.session.execute(
                text("""
                    SELECT RecipeCelebrations.RecipeID, RecipeCelebrations.CelebrationID
                    FROM RecipeCelebrations
                    JOIN Recipe ON Recipe.RecipeID = RecipeCelebrations.RecipeID
                    JOIN Celebration ON Celebration.CelebrationID = RecipeCelebrations.CelebrationID
                    WHERE Recipe.Status = 'Approved' AND Celebration.Status = 'Approved'
                """)
            ).fetchall()

        if not associations:
            abort(404, message="No associations found.")

        # Convert the query results into a dictionary format or objects
        result = [
            {
                "RecipeID": association[0],
                "CelebrationID": association[1]
            }
            for association in associations
        ]

        return result



#get all
    @jwt_required()
    @blp.response(200, RecipeCelebrationSchema(many=True))
    def get(self):
        """
        Retrieve all recipe-celebration associations with full details.
        """
        claims = get_jwt()
        is_admin = claims.get("is_admin", False)

        # Build the query for recipe-celebration associations
        if is_admin:
            # For admin users, retrieve all associations
            associations = db.session.execute(
                text("""
                    SELECT RecipeCelebrations.RecipeID, RecipeCelebrations.CelebrationID
                    FROM RecipeCelebrations
                    JOIN Recipe ON Recipe.RecipeID = RecipeCelebrations.RecipeID
                    JOIN Celebration ON Celebration.CelebrationID = RecipeCelebrations.CelebrationID
                """)
            ).fetchall()
        else:
            # For non-admin users, filter by approved recipe and celebration statuses
            associations = db.session.execute(
                text("""
                    SELECT RecipeCelebrations.RecipeID, RecipeCelebrations.CelebrationID
                    FROM RecipeCelebrations
                    JOIN Recipe ON Recipe.RecipeID = RecipeCelebrations.RecipeID
                    JOIN Celebration ON Celebration.CelebrationID = RecipeCelebrations.CelebrationID
                    WHERE Recipe.Status = 'Approved' AND Celebration.Status = 'Approved'
                """)
            ).fetchall()

        if not associations:
            abort(404, message="No associations found.")

        # Represent associations using the custom function
        result = [
            get_representation(association.RecipeID, association.CelebrationID)
            for association in associations
        ]

        return result

# Helper function for representation
def get_representation(recipe_id, celebration_id):
    return f"<RecipeCelebration RecipeID={recipe_id} CelebrationID={celebration_id}>"



#by id
@blp.route("/recipe-celebrations/<int:recipe_id>")
class RecipeCelebrationView(MethodView):
    @jwt_required()
    @blp.response(200, RecipeCelebrationSchema(many=True))
    def get(self, recipe_id):
        """
        Retrieve all celebrations associated with a specific recipe.
        """
        celebrations = db.session.query(CelebrationModel).join(
            RecipeCelebration, RecipeCelebration.c.CelebrationID == CelebrationModel.CelebrationID
        ).filter(RecipeCelebration.c.RecipeID == recipe_id).all()

        if not celebrations:
            abort(404, message="No celebrations found for this recipe.")

        return celebrations

#update
@blp.route("/celebrations/<int:celebration_id>/recipes/<int:recipe_id>")
class RecipeCelebrationUpdate(MethodView):
    @jwt_required()
    @blp.arguments(RecipeCelebrationSchema(partial=True))
    @blp.response(200, RecipeCelebrationSchema)
    def put(self, data):
        """
        Update the association between a recipe and a celebration.
        """
        association = RecipeCelebration.query.filter_by(
            RecipeID=data["RecipeID"], CelebrationID=data["CelebrationID"]
        ).first()

        if not association:
            abort(404, message="Association not found.")

        recipe = RecipeModel.query.get(data["RecipeID"])
        claims = get_jwt()
        user_id = claims["sub"]
        is_admin = claims.get("is_admin", False)

        if recipe.SubmittedBy != user_id and not is_admin:
            abort(403, message="You do not have permission to update this association.")

        if "CelebrationID" in data:
            association.CelebrationID = data["CelebrationID"]

        db.session.commit()
        return association

#delete
    @jwt_required()
    @blp.response(200)
    def delete(self):
        """
        Remove a celebration from a recipe.
        """
        data = request.get_json()

        if "RecipeID" not in data or "CelebrationID" not in data:
            abort(400, message="RecipeID and CelebrationID are required")

        association = RecipeCelebration.query.filter_by(
            RecipeID=data["RecipeID"], CelebrationID=data["CelebrationID"]
        ).first()

        if not association:
            abort(404, message="Association not found.")

        recipe = RecipeModel.query.get(data["RecipeID"])
        claims = get_jwt()
        user_id = claims["sub"]
        is_admin = claims.get("is_admin", False)

        if recipe.SubmittedBy != user_id and not is_admin:
            abort(403, message="You do not have permission to remove this association.")

        db.session.delete(association)
        db.session.commit()

        return {"message": "Celebration removed from the recipe."}, 200

#see all recipes associated with a celebration
@blp.route("/celebrations/<string:celebration_name>/recipes")
class RecipeCelebrationsView(MethodView):
    @jwt_required()
    @blp.response(200, RecipeSchema(many=True))
    def get(self, celebration_name):
        """
        Get all recipes associated with a specific celebration.
        """
        recipes = db.session.query(RecipeModel).join(
            RecipeCelebration, RecipeCelebration.c.RecipeID == RecipeModel.RecipeID
        ).join(
            CelebrationModel, RecipeCelebration.c.CelebrationID == CelebrationModel.CelebrationID
        ).filter(CelebrationModel.Name == celebration_name).all()

        if not recipes:
            abort(404, message=f"No recipes found for the celebration '{celebration_name}'.")

        return recipes
