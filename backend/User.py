from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import SQLAlchemyError
from db import db
from Models import User, RecipeModel
from schemas import RecipeSchema, UserSchema
import re

blp = Blueprint("Users", "users", description="Operations on user accounts")
BLOCKLIST = set()

def validate_password(password):
    """
    Validates password strength.
    """
    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        abort(400, message="Password must be at least 8 characters long and include both letters and numbers.")

# User registration
@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """
        A user registers a new account.
        """
        if User.query.filter_by(Email=user_data["Email"]).first():
            abort(409, message="A user with this email already exists.")

        validate_password(user_data["Password"])

        user = User(
            Username=user_data["Username"],
            Email=user_data["Email"]
        )
        user.set_password(user_data["Password"])
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the user.")
        return {"message": f"User '{user.Username}' registered successfully."}, 201

# User login
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema(partial=("Username",)))
    def post(self, user_data):
        """
        A user logs in.
        """
        email = user_data.get("Email")
        password = user_data.get("Password")

        if not email or not password:
            abort(400, message="Email and Password are required.")

        user = User.query.filter_by(Email=email).first()
        if not user or not user.check_password(password):
            abort(401, message="Invalid credentials. Please check your email or password.")

        access_token = create_access_token(
                identity=str(user.UserID),
                additional_claims={"Role": user.Role, "is_admin": user.Role == "admin"})        
        return {"access_token": access_token}, 200

# Profile operations
@blp.route("/profile")
class UserProfile(MethodView):
    @jwt_required()
    def get(self):
        """
        Access current user's profile info.
        """
        current_user_id = get_jwt_identity()

        if not current_user_id:
            abort(401, message="Invalid token. Please log in again.")

        user = User.query.get_or_404(int(current_user_id))
        recipes = RecipeModel.query.filter_by(UserID=user.UserID).all()
        recipe_data = RecipeSchema(many=True).dump(recipes)
        return {
            "ID": user.UserID,
            "Username": user.Username,
            "Email": user.Email,
            "Role": user.Role,
            "Recipes": recipe_data
        }, 200
    
#update
    @jwt_required()
    @blp.arguments(UserSchema(partial=True))
    @blp.response(200, UserSchema)
    def put(self, user_data):
        """
        Update current user's credentials.
        """
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(int(current_user_id))

        if "Username" in user_data:
            user.Username = user_data["Username"]
        if "Email" in user_data:
            if User.query.filter(User.Email == user_data["Email"], User.UserID != user.UserID).first():
                abort(409, message="A user with this email already exists.")
            user.Email = user_data["Email"]
        if "Password" in user_data:
            validate_password(user_data["Password"])
            user.set_password(user_data["Password"])

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the user.")

        return user

#delete
    @jwt_required()
    def delete(self):
        """
        Delete current user.
        """
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(int(current_user_id))

        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the user.")

        return {"message": f"User '{user.Username}' deleted successfully."}, 200

# User logout
@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        """
        User logs out from current session.
        """
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out."}, 200

# Get all users
@blp.route("/users")
class UserList(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema(many=True))
    def get(self):
        """
        Get a list of all users.
        """
        current_user = get_jwt_identity()
        current_role = get_jwt().get("Role")
        if current_role != "admin":
            abort(403, message="You are not authorized to view all users.")

        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            users = User.query.paginate(page=page, per_page=per_page, error_out=False).items
            return users
        except SQLAlchemyError as e:
            print(f"Error fetching users: {e}")
            abort(500, message="An error occurred while retrieving users.")
