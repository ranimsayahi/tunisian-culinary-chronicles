from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from Models import Season, db
from schemas import SeasonSchema

blp = Blueprint("Seasons", "seasons", description="Operations on predefined seasons")

#get all seasons
@blp.route("/seasons")
class SeasonList(MethodView):
    @jwt_required()
    @blp.response(200, SeasonSchema(many=True))
    def get(self):
        """
        Get a list of all predefined seasons.
        """
        seasons = Season.query.all()
        return seasons

#get  seasons by id
@blp.route("/seasons/<int:season_id>")
class SeasonDetail(MethodView):
    @jwt_required()
    @blp.response(200, SeasonSchema)
    def get(self, season_id):
        """
        Get a specific season by ID.
        """
        season = Season.query.get_or_404(season_id)
        return season
