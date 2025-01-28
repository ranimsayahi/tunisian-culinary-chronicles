from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from db import db
from Models import RecipeStep, RecipeModel
from schemas import RecipeStepSchema

blp = Blueprint("RecipeSteps", "recipe_steps", description="Operations on recipe steps")

# Create a recipe step for a recipe
@blp.route("/recipe/<int:recipe_id>/steps")
class RecipeStepCreateAPI(MethodView):  
    @jwt_required()
    @blp.arguments(RecipeStepSchema)
    @blp.response(201, RecipeStepSchema)
    def post(self, recipe_data, recipe_id):
        """
        Create a new step for a specific recipe.
        """
        user_id = get_jwt_identity()  
        recipe = RecipeModel.query.get_or_404(recipe_id)

        step = RecipeStep(
            RecipeID=recipe_id,
            StepOrder=recipe_data["StepOrder"],
            Content=recipe_data["Content"]
        )

        try:
            db.session.add(step)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the recipe step.")
        
        return step


# Get all steps for a specific recipe
@blp.route("/recipe/<int:recipe_id>/steps")
class RecipeStepListAPI(MethodView):  
    @jwt_required()
    @blp.response(200, RecipeStepSchema(many=True))
    def get(self, recipe_id):
        """
        Get all steps for a specific recipe.
        """
        recipe = RecipeModel.query.get_or_404(recipe_id)
        steps = RecipeStep.query.filter_by(RecipeID=recipe_id).order_by(RecipeStep.StepOrder).all()
        return steps


# Get a specific step for a specific recipe
@blp.route("/recipe/<int:recipe_id>/steps/<int:step_id>")
class RecipeStepDetailAPI(MethodView):  
    @jwt_required()
    @blp.response(200, RecipeStepSchema)
    def get(self, recipe_id, step_id):
        """
        Get a specific step for a recipe.
        """
        recipe = RecipeModel.query.get_or_404(recipe_id)
        step = RecipeStep.query.filter_by(RecipeID=recipe_id, StepID=step_id).first_or_404()
        return step


# Update a specific recipe step
@blp.route("/recipe/<int:recipe_id>/steps/<int:step_id>")
class RecipeStepUpdateAPI(MethodView):  
    @jwt_required()
    @blp.arguments(RecipeStepSchema(partial=True)) 
    @blp.response(200, RecipeStepSchema)
    def put(self, recipe_data, recipe_id, step_id):
        """
        Update a specific step for a recipe.
        """
        user_id = get_jwt_identity()  
        claims = get_jwt()  
        role = claims.get("role") 

        recipe = RecipeModel.query.get_or_404(recipe_id)
        step = RecipeStep.query.filter_by(RecipeID=recipe_id, StepID=step_id).first_or_404()

        # Ensure only the recipe owner or an admin can update the step
        # if recipe.UserID != user_id and role != "admin":
        #     abort(403, message="You are not authorized to update this recipe step.")

        if "StepOrder" in recipe_data:
            step.StepOrder = recipe_data["StepOrder"]
        if "Content" in recipe_data:
            step.Content = recipe_data["Content"]

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the recipe step.")
        
        return step


# Delete a specific recipe step
@blp.route("/recipe/<int:recipe_id>/steps/<int:step_id>")
class RecipeStepDeleteAPI(MethodView):  
    @jwt_required()
    def delete(self, recipe_id, step_id):
        """
        Delete a specific step for a recipe.
        """
        user_id = get_jwt_identity()  
        claims = get_jwt()  
        role = claims.get("role") 

        recipe = RecipeModel.query.get_or_404(recipe_id)
        step = RecipeStep.query.filter_by(RecipeID=recipe_id, StepID=step_id).first_or_404()

        # Ensure only the recipe owner or an admin can delete the step
        # if recipe.UserID != user_id and role != "admin":
        #     abort(403, message="You are not authorized to delete this recipe step.")
        
        try:
            db.session.delete(step)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the recipe step.")
        
        return {"message": "Recipe step deleted successfully."}, 200
