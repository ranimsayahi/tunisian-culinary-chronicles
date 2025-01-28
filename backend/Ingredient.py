from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from Models import Ingredient, db, User
from schemas import IngredientSchema

blp = Blueprint("Ingredients", "ingredients", description="Operations on ingredients")

# Helper function to check if the user is an admin
def is_admin():
    user_id = get_jwt_identity()  
    user = User.query.get_or_404(int(user_id)) 
    return user.Role == 'admin'



# Create Ingredients
@blp.route("/ingredients")
class IngredientList(MethodView):
    @jwt_required()
    @blp.arguments(IngredientSchema)
    @blp.response(201, IngredientSchema)
    def post(self, ingredient_data):
        """
        Create a new ingredient.
        """
        existing_ingredient = Ingredient.query.filter_by(Name=ingredient_data["Name"]).first()
        if existing_ingredient:
            abort(409, message="An ingredient with this name already exists.")

        user_id = int(get_jwt_identity())
        ingredient = Ingredient(
            Name=ingredient_data["Name"],
            Unit=ingredient_data.get("Unit"),
            SubmittedBy=user_id,
        )
        
        try:
            db.session.add(ingredient)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the ingredient.")
        
        return ingredient
    
# get all Ingredients
    @blp.response(200, IngredientSchema(many=True))
    @jwt_required()
    def get(self):
        """
        Get a list of ingredients (only approved ones for non-admins).
        """
        if not is_admin():
            ingredients = Ingredient.query.filter_by(Status="Approved").all()
        else:
            ingredients = Ingredient.query.all()
        
        return ingredients

# Get an Ingredient by id
@blp.route("/ingredients/<int:ingredient_id>")
class IngredientDetail(MethodView):
    @jwt_required()
    @blp.response(200, IngredientSchema)
    def get(self, ingredient_id):
        """
        Get a specific ingredient by ID (only approved for non-admins).
        """
        ingredient = Ingredient.query.get_or_404(ingredient_id)

        if not is_admin() and ingredient.Status != "Approved":
            abort(403, message="You can only view approved ingredients.")

        return ingredient

#update an ingredient
    @jwt_required()
    @blp.arguments(IngredientSchema)
    @blp.response(200, IngredientSchema)
    def put(self, ingredient_data, ingredient_id):
        """
        Update an ingredient (only admin or owner can update).
        """
        ingredient = Ingredient.query.get_or_404(ingredient_id)

        user_id = int(get_jwt_identity())
        if not is_admin() and ingredient.SubmittedBy != user_id:
            abort(403, message="You are not authorized to update this ingredient.")

        if ingredient_data["Name"] != ingredient.Name:
            existing_ingredient = Ingredient.query.filter_by(Name=ingredient_data["Name"]).first()
            if existing_ingredient:
                abort(409, message="An ingredient with this name already exists.")

        ingredient.Name = ingredient_data["Name"]
        ingredient.Unit = ingredient_data.get("Unit", ingredient.Unit)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the ingredient.")
        
        return ingredient
    
#delete an ingredient
    @jwt_required()
    def delete(self, ingredient_id):
        """
        Delete an ingredient (only admin or owner can delete).
        """
        ingredient = Ingredient.query.get_or_404(ingredient_id)

        user_id = int(get_jwt_identity())
        if not is_admin() and ingredient.SubmittedBy != user_id:
            abort(403, message="You are not authorized to delete this ingredient.")
        
        try:
            db.session.delete(ingredient)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the ingredient.")
        
        return {"message": "Ingredient deleted successfully."}

# Approve or Reject an Ingredient
@blp.route("/ingredients/<int:ingredient_id>/approve")
class ApprovalIngredient(MethodView):
    @jwt_required()
    @blp.response(200, IngredientSchema)
    def patch(self, ingredient_id):
        """
        Approve or reject an ingredient (only admin).
        """
        if not is_admin():
            abort(403, message="Only admin can approve or reject an ingredient.")

        ingredient = Ingredient.query.get_or_404(ingredient_id)

        action = request.args.get("action", "").lower()
        if action == "approve":
            ingredient.Status = "Approved"
        elif action == "reject":
            ingredient.Status = "Rejected"
        else:
            abort(400, message="Invalid action. Use 'approve' or 'reject'.")
        
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the ingredient status.")
        
        return ingredient

#search for ingredient
@blp.route("/ingredients/search")
class IngredientSearch(MethodView):
    @jwt_required()
    @blp.arguments(IngredientSchema(partial=True), location="query")
    @blp.response(200, IngredientSchema(many=True))
    def get(self, args):
        """
        Search for ingredients based on query parameters.
        """
        query = db.session.query(Ingredient)

        claims = get_jwt()
        is_admin = claims.get("is_admin", False)

        if not is_admin:
            query = query.filter(Ingredient.Status == "Approved")
        
        if "Name" in args:
            query = query.filter(Ingredient.Name.ilike(f"%{args['Name']}%"))
        
        if "Unit" in args:
            query = query.filter(Ingredient.Unit.ilike(f"%{args['Unit']}%"))
        
        ingredients = query.all()

        if not ingredients:
            abort(404, message="No ingredients match the search criteria.")
        
        return ingredients