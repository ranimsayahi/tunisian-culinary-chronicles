from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from Models import CelebrationModel, User
from db import db
from schemas import CelebrationSchema

blp = Blueprint("Celebrations", "celebrations", description="Operations on celebrations")
VALID_CELEBRATIONS = ["Eid", "Ramadan", "Weddings", "Eid el-Adha"]

def is_admin():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return user.Role == 'admin'

# Create a new celebration
@blp.route("/celebrations")
class CelebrationList(MethodView):
    @jwt_required()
    @blp.arguments(CelebrationSchema)
    @blp.response(201, CelebrationSchema)
    def post(self, celebration_data):
        """
        Create a new celebration and add it to the list if it's not already there.
         """
        celebration_name = celebration_data["Name"]

        if celebration_name not in VALID_CELEBRATIONS:
            user_id = get_jwt_identity()
            user = User.query.get_or_404(user_id)
            if user.Role != "admin":
                abort(403, message="You are not authorized to add new celebrations.")
            else:
                VALID_CELEBRATIONS.append(celebration_name)

        existing_celebration = CelebrationModel.query.filter_by(Name=celebration_name).first()
        if existing_celebration:
            abort(409, message="A celebration with this name already exists.")

    # Create and add the new celebration
        user_id = get_jwt_identity()
        celebration = CelebrationModel(
            Name=celebration_name,
            Description=celebration_data.get("Description"),
            SubmittedBy=user_id,
            Status="Pending" if celebration_name not in VALID_CELEBRATIONS else "Approved"
         )

        try:
            db.session.add(celebration)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the celebration.")

        return celebration


#getall
    @jwt_required()
    @blp.response(200, CelebrationSchema(many=True))
    def get(self):
        """
        Get a list of all celebrations.
        """
        current_user = get_jwt_identity()
        is_admin = False
        if current_user:
            user = User.query.get(current_user)
            is_admin = user.Role == "admin"

        query = CelebrationModel.query

        if not is_admin:
            query = query.filter(CelebrationModel.Status == "Approved")

        celebrations = query.all()
        return celebrations

# Get a celebration by ID
@blp.route("/celebrations/<int:celebration_id>")
class Celebration(MethodView):
    @jwt_required()
    @blp.response(200, CelebrationSchema)
    def get(self, celebration_id):
        """
        Get a celebration by ID.
        """
        celebration = CelebrationModel.query.get_or_404(celebration_id)
        if celebration.Status != "Approved" and get_jwt_identity() != celebration.SubmittedBy:
            abort(403, message="You are not authorized to view this celebration.")
        return celebration

# Approve a celebration 
@blp.route("/celebrations/<int:celebration_id>/approve")
class ApproveCelebration(MethodView):
    @jwt_required()
    def put(self, celebration_id):
        """
        Approve a celebration.
        """
        user_id = get_jwt_identity()
        admin_user = User.query.get_or_404(user_id)

        if admin_user.Role != "admin":
            abort(403, message="You are not authorized to approve celebrations.")

        celebration = CelebrationModel.query.get_or_404(celebration_id)
        celebration.Status = "Approved"

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while approving the celebration.")

        return {"message": "Celebration approved successfully.", "celebration_id": celebration.CelebrationID, "status": celebration.Status}, 200

# Reject a celebration 
@blp.route("/celebrations/<int:celebration_id>/reject")
class RejectCelebration(MethodView):
    @jwt_required()
    def put(self, celebration_id):
        """
        Reject a celebration.
        """
        user_id = get_jwt_identity()
        admin_user = User.query.get_or_404(user_id)

        if admin_user.Role != "admin":
            abort(403, message="You are not authorized to reject celebrations.")

        celebration = CelebrationModel.query.get_or_404(celebration_id)
        celebration.Status = "Rejected"

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while rejecting the celebration.")

        return {"message": "Celebration rejected successfully.", "celebration_id": celebration.CelebrationID, "status": celebration.Status}, 200

# Delete a celebration 
@blp.route("/celebrations/<int:celebration_id>")
class CelebrationDelete(MethodView):
    @jwt_required()
    def delete(self, celebration_id):
        """
        Delete a celebration.
        """
        user_id = get_jwt_identity()
        celebration = CelebrationModel.query.get_or_404(celebration_id)
        
        if celebration.SubmittedBy != user_id and not is_admin():
            abort(403, message="You are not authorized to delete this celebration.")

        try:
            db.session.delete(celebration)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the celebration.")

        return {"message": "Celebration deleted successfully."}, 200

# Update a celebration
@blp.route("/celebrations/<int:celebration_id>")
class CelebrationUpdate(MethodView):
    @jwt_required()
    @blp.arguments(CelebrationSchema)
    @blp.response(200, CelebrationSchema)
    def put(self, celebration_data, celebration_id):
        """
        Update an existing celebration (only admin or owner can update).
        """
        celebration = CelebrationModel.query.get_or_404(celebration_id)

        user_id = get_jwt_identity()
        if not is_admin() and celebration.SubmittedBy != user_id:
            abort(403, message="You are not authorized to update this celebration.")
        
        if celebration_data["Name"] != celebration.Name:
            existing_celebration = CelebrationModel.query.filter_by(Name=celebration_data["Name"]).first()
            if existing_celebration:
                abort(409, message="A celebration with this name already exists.")

        celebration.Name = celebration_data["Name"]
        celebration.Description = celebration_data.get("Description", celebration.Description)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the celebration.")
        
        return celebration
