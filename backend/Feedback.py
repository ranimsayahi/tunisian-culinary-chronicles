# from flask import request
# from flask.views import MethodView
# from flask_smorest import Blueprint, abort
# from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
# from sqlalchemy.exc import SQLAlchemyError
# from db import db
# from Models import Feedback, RecipeModel, User
# from schemas import FeedbackSchema

# blp = Blueprint("Feedback", "feedback", description="Operations on feedback")

# # post a  feedback for a recipe
# @blp.route("/feedback")
# class FeedbackList(MethodView):
#     @jwt_required()
#     @blp.arguments(FeedbackSchema)
#     @blp.response(201, FeedbackSchema)
#     def post(self, feedback_data):
#         user_id = get_jwt_identity()
#         recipe = RecipeModel.query.get_or_404(feedback_data["RecipeID"])

#         existing_feedback = Feedback.query.filter_by(UserID=user_id, RecipeID=feedback_data["RecipeID"]).first()
#         if existing_feedback:
#             abort(409, message="You have already given feedback for this recipe.")

#         if feedback_data["Rating"] is None:
#             abort(400, message="Rating is required.")

#         feedback = Feedback(
#             UserID=user_id,
#             RecipeID=feedback_data["RecipeID"],
#             Rating=feedback_data["Rating"],
#             Comment=feedback_data.get("Comment"),
#         )

#         try:
#             db.session.add(feedback)
#             db.session.commit()
#         except SQLAlchemyError:
#             db.session.rollback()
#             abort(500, message="An error occurred while creating feedback.")

#         return feedback

# # Get all feedback for a specific recipe
# @blp.route("/feedback/recipe/<int:recipe_id>")
# class FeedbackForRecipe(MethodView):
#     @jwt_required()
#     @blp.response(200, FeedbackSchema(many=True))
#     def get(self, recipe_id):
#         """
#         Get all feedback for a specific recipe.
#         """
#         recipe = RecipeModel.query.get_or_404(recipe_id)
#         feedbacks = Feedback.query.filter_by(RecipeID=recipe_id).all()
#         return feedbacks

# from flask_jwt_extended import get_jwt, get_jwt_identity

# # Update feedback for a specific recipe
# @blp.route("/feedback/<int:feedback_id>")
# class FeedbackDetailView(MethodView):
#     @jwt_required()
#     @blp.arguments(FeedbackSchema(partial=True))  # Accept partial updates
#     @blp.response(200, FeedbackSchema)
#     def put(self, feedback_data, feedback_id):
#         """
#         Update feedback for a specific recipe.
#         """
#         user_id = get_jwt_identity()
#         user_claims = get_jwt()  # Fetch additional claims (e.g., role)

#         # Fetch feedback and ensure it exists
#         feedback = Feedback.query.get_or_404(feedback_id)

#         # Ensure the user is authorized to update the feedback
#         if feedback.UserID != user_id and user_claims.get("Role") != "admin":
#             abort(403, message="You are not authorized to update this feedback.")

#         # Update feedback fields if provided
#         if "Rating" in feedback_data:
#             feedback.Rating = feedback_data["Rating"]
#         if "Comment" in feedback_data:
#             feedback.Comment = feedback_data["Comment"]

#         # Save changes to the database
#         try:
#             db.session.commit()
#         except SQLAlchemyError:
#             db.session.rollback()
#             abort(500, message="An error occurred while updating feedback.")

#         return feedback


# # Delete feedback for a specific recipe
# @blp.route("/feedback/<int:feedback_id>")
# class FeedbackDetail(MethodView):
#     @jwt_required()
#     def delete(self, feedback_id):
#         """
#         Delete feedback for a specific recipe.
#         """
#         user_id = get_jwt_identity()
#         user_claims = get_jwt()  # Fetch additional claims (e.g., role)

#         # Fetch the feedback and ensure it exists
#         feedback = Feedback.query.get_or_404(feedback_id)

#         # Check if the user is authorized to delete the feedback
#         if feedback.UserID != user_id and user_claims.get("role") != "admin":
#             abort(403, message="You are not authorized to delete this feedback.")

#         # Attempt to delete the feedback from the database
#         try:
#             db.session.delete(feedback)
#             db.session.commit()
#         except SQLAlchemyError:
#             db.session.rollback()
#             abort(500, message="An error occurred while deleting feedback.")

#         return {"message": "Feedback deleted successfully."}, 200


from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from db import db
from Models import Feedback, RecipeModel, User
from schemas import FeedbackSchema

blp = Blueprint("Feedback", "feedback", description="Operations on feedback")

# Post feedback for a recipe
@blp.route("/feedback")
class FeedbackList(MethodView):
    @jwt_required()
    @blp.arguments(FeedbackSchema)
    @blp.response(201, FeedbackSchema)
    def post(self, feedback_data):
        user_id = get_jwt_identity()
        recipe = RecipeModel.query.get_or_404(feedback_data["RecipeID"])

        existing_feedback = Feedback.query.filter_by(UserID=user_id, RecipeID=feedback_data["RecipeID"]).first()
        if existing_feedback:
            abort(409, message="You have already given feedback for this recipe.")

        if feedback_data["Rating"] is None:
            abort(400, message="Rating is required.")

        feedback = Feedback(
            UserID=user_id,
            RecipeID=feedback_data["RecipeID"],
            Rating=feedback_data["Rating"],
            Comment=feedback_data.get("Comment"),
        )

        try:
            db.session.add(feedback)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating feedback.")

        return feedback

# Get all feedback for a specific recipe
@blp.route("/feedback/recipe/<int:recipe_id>")
class FeedbackForRecipe(MethodView):
    @jwt_required()
    @blp.response(200, FeedbackSchema(many=True))
    def get(self, recipe_id):
        """
        Get all feedback for a specific recipe.
        """
        recipe = RecipeModel.query.get_or_404(recipe_id)
        feedbacks = Feedback.query.filter_by(RecipeID=recipe_id).all()
        return feedbacks

# Update feedback for a specific recipe
@blp.route("/feedback/<int:feedback_id>")
class FeedbackDetailView(MethodView):
    @jwt_required()
    @blp.arguments(FeedbackSchema(partial=True))  
    @blp.response(200, FeedbackSchema)
    def put(self, feedback_data, feedback_id):
        """
        Update feedback for a specific recipe.
        """
        user_id = get_jwt_identity()
        user_claims = get_jwt()  

        feedback = Feedback.query.get_or_404(feedback_id)

        if feedback.UserID != user_id and user_claims.get("Role") != "admin":
            abort(403, message="You are not authorized to update this feedback.")

        if "Rating" in feedback_data:
            feedback.Rating = feedback_data["Rating"]
        if "Comment" in feedback_data:
            feedback.Comment = feedback_data["Comment"]

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating feedback.")

        return feedback


# Delete feedback for a specific recipe
@blp.route("/feedback/<int:feedback_id>")
class FeedbackDetail(MethodView):
    @jwt_required()
    def delete(self, feedback_id):
        """
        Delete feedback for a specific recipe.
        """
        user_id = get_jwt_identity()
        user_claims = get_jwt()  

        feedback = Feedback.query.get_or_404(feedback_id)

        if feedback.UserID != user_id and user_claims.get("Role") != "admin":
            abort(403, message="You are not authorized to delete this feedback.")

        try:
            db.session.delete(feedback)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting feedback.")

        return {"message": "Feedback deleted successfully."}, 200



