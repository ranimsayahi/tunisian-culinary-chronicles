from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from Models import EthnicityModel, User
from db import db 
from schemas import EthnicitySchema

blp = Blueprint("Ethnicities", "ethnicities", description="Operations on ethnicities")
VALID_Ethnicities=["Tunisian", "Berber", "Arab", "Jewish"]   

# Helper function to check if the user is an admin
def is_admin():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return user.Role == 'admin'

# Create a new ethnicity
@blp.route("/ethnicities")
class EthnicityList(MethodView):
    @jwt_required()
    @blp.arguments(EthnicitySchema)
    @blp.response(201, EthnicitySchema)
    def post(self, ethnicity_data):
        """
        Create a new ethnicity.
        """
        ethnicity_name = ethnicity_data["Name"]

        # Check if ethnicity already exists
        existing_ethnicity = EthnicityModel.query.filter_by(Name=ethnicity_name).first()
        if existing_ethnicity:
            abort(409, message="An ethnicity with this name already exists.")

        # Create a new ethnicity with status "Pending"
        user_id = get_jwt_identity()
        ethnicity = EthnicityModel(
            Name=ethnicity_name,
            Description=ethnicity_data.get("Description"),
            SubmittedBy=user_id,
            Status="Pending"  # Default status is Pending
        )

        try:
            db.session.add(ethnicity)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the ethnicity.")

        return ethnicity


        
#see all ethnicities
    @blp.response(200, EthnicitySchema(many=True))
    @jwt_required()
    def get(self):
        """
        Get a list of ethnicities (only approved ones for non-admins).
        """
        if not is_admin():
            ethnicities = EthnicityModel.query.filter_by(Status="Approved").all()
        else:
            ethnicities = EthnicityModel.query.all()
        
        return ethnicities

# Get a specific ethnicity by its ID
@blp.route("/ethnicities/<int:ethnicity_id>")
class EthnicityDetail(MethodView):
    @blp.response(200, EthnicitySchema)
    @jwt_required()
    def get(self, ethnicity_id):
        """
        Get a specific ethnicity by its ID (only approved for non-admins).
        """
        ethnicity = EthnicityModel.query.get_or_404(ethnicity_id)

        if not is_admin() and ethnicity.Status != "Approved":
            abort(403, message="You can only view approved ethnicities.")

        return ethnicity
#update
    @jwt_required()
    @blp.arguments(EthnicitySchema)
    @blp.response(200, EthnicitySchema)
    def put(self, ethnicity_data, ethnicity_id):
        """
        Update an existing ethnicity (only admin or owner can update).
        """
        ethnicity = EthnicityModel.query.get_or_404(ethnicity_id)

        user_id = get_jwt_identity()
        if not is_admin() and ethnicity.SubmittedBy != user_id:
            abort(403, message="You are not authorized to update this ethnicity.")
        
        if ethnicity_data["Name"] != ethnicity.Name:
            existing_ethnicity = EthnicityModel.query.filter_by(Name=ethnicity_data["Name"]).first()
            if existing_ethnicity:
                abort(409, message="An ethnicity with this name already exists.")

        ethnicity.Name = ethnicity_data["Name"]
        ethnicity.Description = ethnicity_data.get("Description", ethnicity.Description)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the ethnicity.")
        
        return ethnicity

#delete
    @jwt_required()
    def delete(self, ethnicity_id):
        """
        Delete an ethnicity (only admin or owner can delete).
        """
        ethnicity = EthnicityModel.query.get_or_404(ethnicity_id)

        user_id = get_jwt_identity()
        if not is_admin() and ethnicity.SubmittedBy != user_id:
            abort(403, message="You are not authorized to delete this ethnicity.")
        
        try:
            db.session.delete(ethnicity)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the ethnicity.")
        
        return {"message": "Ethnicity deleted successfully."}

#  Approve  an ethnicity
# Approve an ethnicity
@blp.route("/ethnicities/<int:ethnicity_id>/approve")
class ApproveEthnicity(MethodView):
    @jwt_required()
    def patch(self, ethnicity_id):
        """
        Approve an ethnicity (only admin).
        """
        if not is_admin():
            abort(403, message="Only admin can approve an ethnicity.")

        ethnicity = EthnicityModel.query.get_or_404(ethnicity_id)

        ethnicity.Status = "Approved"  
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while approving the ethnicity.")
        
        # Return the serialized ethnicity using the schema
        return EthnicitySchema().dump(ethnicity), 200  # Serializing the ethnicity model to a dictionary

#reject  an ethnicity
# Reject an ethnicity
@blp.route("/ethnicities/<int:ethnicity_id>/reject")
class RejectEthnicity(MethodView):
    @jwt_required()
    def patch(self, ethnicity_id):
        """
        Reject an ethnicity (only admin).
        """
        if not is_admin():
            abort(403, message="Only admin can reject an ethnicity.")

        ethnicity = EthnicityModel.query.get_or_404(ethnicity_id)

        ethnicity.Status = "Rejected"  
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while rejecting the ethnicity.")
        
        # Return the serialized ethnicity using the schema
        return EthnicitySchema().dump(ethnicity), 200  # Serializing the ethnicity model to a dictionary

