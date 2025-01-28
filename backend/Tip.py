from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from Models.Tip import TipModel
from Models.User import User
from schemas import TipSchema
from db import db

blp = Blueprint("RecipeTips", "tips", description="Operations on tips")

# Create a tip
@blp.route("/tips")
class TipList(MethodView):
    @jwt_required()
    @blp.arguments(TipSchema)
    @blp.response(201, TipSchema)
    def post(self, tip_data):
        """
        Create a new tip for a recipe.
        """
        user_id = get_jwt_identity()
        tip = TipModel(
            RecipeID=tip_data["RecipeID"],
            Content=tip_data["Content"],
            Status="Pending",  
            UserID=user_id
        )

        try:
            db.session.add(tip)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the tip.")

        return tip

# Get all tips for a recipe
@blp.route("/recipes/<int:recipe_id>/tips")
class RecipeTips(MethodView):
    @blp.response(200, TipSchema(many=True))
    def get(self, recipe_id):
        """
        Get all tips for a specific recipe.
        """
        tips = TipModel.query.filter_by(RecipeID=recipe_id).all()
        return tips or []

# Get a tip by ID
@blp.route("/tips/<int:tip_id>")
class TipDetail(MethodView):
    @blp.response(200, TipSchema)
    def get(self, tip_id):
        """
        Get details of a specific tip by ID.
        """
        tip = TipModel.query.get_or_404(tip_id)
        return tip

# Approve tip
@blp.route("/tips/<int:tip_id>/approve")
class ApproveTip(MethodView):
    @jwt_required()
    def put(self, tip_id):
        """
        Admin can approve a tip.
        """
        user_id = get_jwt_identity()
        admin_user = User.query.get_or_404(user_id)

        if admin_user.Role != "admin":
            abort(403, message="You are not authorized to approve tips.")

        tip = TipModel.query.get_or_404(tip_id)
        tip.Status = "Approved"

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while approving the tip.")

        return {"message": "Tip approved successfully.", "tip_id": tip.TipID, "status": tip.Status}, 200

# Reject tip
@blp.route("/tips/<int:tip_id>/reject")
class RejectTip(MethodView):
    @jwt_required()
    def put(self, tip_id):
        """
        Admin can reject a tip.
        """
        user_id = get_jwt_identity()
        admin_user = User.query.get_or_404(user_id)

        if admin_user.Role != "admin":
            abort(403, message="You are not authorized to reject tips.")

        tip = TipModel.query.get_or_404(tip_id)
        tip.Status = "Rejected"

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while rejecting the tip.")

        return {"message": "Tip rejected successfully.", "tip_id": tip.TipID, "status": tip.Status}, 200

# Delete a tip
@blp.route("/tips/<int:tip_id>")
class TipDelete(MethodView):
    @jwt_required()
    def delete(self, tip_id):
        """
        Delete a tip.
        Only the user who created the tip or an admin can delete it.
        """
        user_id = get_jwt_identity()
        tip = TipModel.query.get_or_404(tip_id)

        if tip.UserID != user_id and get_jwt().get("role") != "admin":
            abort(403, message="You are not authorized to delete this tip.")

        try:
            db.session.delete(tip)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the tip.")

        return {"message": "Tip deleted successfully."}, 200

# Update a tip 
@blp.route("/tips/<int:tip_id>")
class TipUpdate(MethodView):
    @jwt_required()
    @blp.arguments(TipSchema(partial=True))  
    @blp.response(200, TipSchema)
    def put(self, tip_data, tip_id):
        """
        Update a specific tip.
        Only the user who created the tip or an admin can update it.
        """
        user_id = get_jwt_identity()
        tip = TipModel.query.get_or_404(tip_id)

        if tip.UserID != user_id and get_jwt().get("role") != "admin":
            abort(403, message="You are not authorized to update this tip.")

        for key, value in tip_data.items():
            setattr(tip, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the tip.")

        return tip
