from flask_jwt_extended import get_jwt_identity
from marshmallow import Schema, ValidationError, fields, validate, validates

from Models import User
from db import db


class UserSchema(Schema):
    UserID = fields.Int(dump_only=True)
    Username = fields.Str(required=True, validate=validate.Length(max=100))
    Email = fields.Email(required=True, validate=validate.Length(max=150))
    Password = fields.Str(load_only=True, required=True, validate=validate.Length(min=8))
    Role = fields.Str(validate=validate.Length(max=50))  # Use marshmallow fields, not db.Column
    Timestamp = fields.DateTime(dump_only=True)
    Recipes = fields.Nested("RecipeSchema", many=True, dump_only=True)
    Tips = fields.Nested("TipSchema", many=True, dump_only=True)  
    Feedbacks = fields.Nested("FeedbackSchema", many=True, dump_only=True)  

    class Meta:
        name = "UserSchema"



class RecipeSchema(Schema):
    RecipeID = fields.Int(dump_only=True)
    Name = fields.Str(required=True, validate=validate.Length(max=255))
    Description = fields.Str(validate=validate.Length(max=2000))
    Difficulty = fields.Str(validate=validate.OneOf(["Easy", "Medium", "Hard"]))
    CookingTime = fields.Str(validate=validate.Length(max=50))
    Category = fields.Str(validate=validate.Length(max=100))
    UserID = fields.Int(required=True)
    Status = fields.Str(dump_only=True)
    Timestamp = fields.DateTime(dump_only=True)
    Steps = fields.Nested("RecipeStepSchema", many=True, dump_only=True)  
    Ingredients = fields.Nested("RecipeIngredientSchema", many=True, dump_only=True)  
    Ethnicities = fields.Nested("RecipeEthnicitySchema", many=True, dump_only=True) 
    Celebrations = fields.Nested("RecipeCelebrationSchema", many=True, dump_only=True)  
    Seasons = fields.Nested("SeasonSchema", many=True, dump_only=True)  
    


    class Meta:
        name = "RecipeSchema"


class RecipeStepSchema(Schema):
    StepID = fields.Int(dump_only=True)
    RecipeID = fields.Int(required=True)
    StepOrder = fields.Int(required=True)
    Content = fields.Str(required=True, validate=validate.Length(max=2000))

    class Meta:
        name = "RecipeStepSchema"


class IngredientSchema(Schema):
    IngredientID = fields.Int(dump_only=True)
    Name = fields.Str(required=True, validate=validate.Length(max=255))
    Unit = fields.Str(validate=validate.Length(max=50))
    Status = fields.Str(dump_only=True)  
    SubmittedBy = fields.Int(dump_only=True)

    class Meta:
        name = "IngredientSchema"


class RecipeIngredientSchema(Schema):
    RecipeID = fields.Int(required=True)
    IngredientID = fields.Int(required=True)
    Quantity = fields.Float(required=True)
    Ingredient = fields.Nested("IngredientSchema", dump_only=True) 

    class Meta:
        name = "RecipeIngredientSchema"




class TipSchema(Schema):
    TipID = fields.Int(dump_only=True)
    RecipeID = fields.Int(required=False)
    UserID = fields.Int(required=True)  
    Content = fields.Str(required=True, validate=validate.Length(max=500))
    Status = fields.Str(dump_only=True)  

    class Meta:
        name = "TipSchema"


class CelebrationSchema(Schema):
    CelebrationID = fields.Int(dump_only=True)
    Name = fields.Str(
        required=True,
        validate=validate.Length(max=100)
    )
    Description = fields.Str(validate=validate.Length(max=2000))
    Recipes = fields.Nested("RecipeCelebrationSchema", many=True, dump_only=True)
    Status = fields.Str(dump_only=True)
    SubmittedBy = fields.Int(dump_only=True)

    class Meta:
        name = "CelebrationSchema"


class RecipeCelebrationSchema(Schema):
    RecipeID = fields.Int(required=True)
    CelebrationID = fields.Int(required=True)
    Recipe = fields.Nested("RecipeSchema", dump_only=True)  
    Celebration = fields.Nested("CelebrationSchema", dump_only=True) 
    class Meta:
        name = "RecipeCelebrationSchema"


class EthnicitySchema(Schema):
    EthnicityID = fields.Int(dump_only=True)
    Name = fields.Str(required=True,validate=validate.Length(max=100))
    Description = fields.Str(validate=validate.Length(max=2000))
    Recipes = fields.Nested("RecipeEthnicitySchema", many=True, dump_only=True) 
    Status = fields.Str(dump_only=True)  
    SubmittedBy = fields.Int(dump_only=True)

    class Meta:
        name = "EthnicitySchema"


class RecipeEthnicitySchema(Schema):
    RecipeID = fields.Int(required=True)
    EthnicityID = fields.Int(required=True)
    Recipe = fields.Nested("RecipeSchema", dump_only=True)  
    Ethnicity = fields.Nested("EthnicitySchema", dump_only=True)  

    class Meta:
        name = "RecipeEthnicitySchema"


class SeasonSchema(Schema):
    SeasonID = fields.Int(dump_only=True)
    Season = fields.Str(
        required=True,
        validate=validate.OneOf(["Spring", "Summer", "Autumn", "Winter"]),)    
    Description = fields.Str(validate=validate.Length(max=2000))
    Recipes = fields.Nested("RecipeSchema", many=True, dump_only=True)  

    class Meta:
        name = "SeasonSchema"


class SeasonalRecipeSchema(Schema):
    SeasonID = fields.Int(dump_only=True)
    RecipeID = fields.Int(required=True)

    class Meta:
        name = "SeasonalRecipeSchema"


class FeedbackSchema(Schema):
    FeedbackID = fields.Int(dump_only=True)
    UserID = fields.Int(required=True)
    RecipeID = fields.Int(required=True)
    Rating = fields.Int(required=False, validate=validate.Range(min=1, max=5))
    Comment = fields.Str(validate=validate.Length(max=2000))

    class Meta:
        name = "FeedbackSchema"
