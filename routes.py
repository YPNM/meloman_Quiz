import collections
import datetime
import locale
from collections import Counter

locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))

from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session,
    abort
)

from datetime import timedelta
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError
import base64

from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)
from flask import request

import db_init
from app import create_app, db, login_manager, bcrypt
from models import User
from forms import login_form, register_form
from werkzeug.utils import secure_filename
import os
import jinja2

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app = create_app()


@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)


@app.route("/admin/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if (user):
                if check_password_hash(user.pwd, form.pwd.data):
                    login_user(user)
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash("Invalid Username or password!", "danger")
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("admin/auth.html",
                           form=form,
                           text="Login",
                           title="Login",
                           btn_action="Login"
                           )


# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            pwd = form.pwd.data
            username = form.username.data

            newuser = User(
                username=username,
                pwd=bcrypt.generate_password_hash(pwd),
                superadmin=1
            )

            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("admin/auth.html",
                           form=form,
                           text="Create account",
                           title="Register",
                           btn_action="Register account"
                           )


@app.route("/admin/dashboard", methods=["GET"], strict_slashes=False)
@login_required
def admin_dashboard():
    return render_template("admin/index.html", title="Главная")


# Routing for cities
@app.route("/admin/cities", methods=["GET"], strict_slashes=False)
@login_required
def admin_cities():
    if (current_user.superadmin):
        citiesModel = db_init.CitiesDB()
        cities = citiesModel.get_all_cities()
        return render_template("admin/pages/cities/index.html", title="Города", cities=cities)
    else:
        abort(403)


@app.route("/admin/cities/create", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_cities_create():
    if (current_user.superadmin):
        if request.method == "GET":
            return render_template("admin/pages/cities/create.html", title="Добавление города")
        if request.method == "POST":
            cityName = request.form.get("cityName")
            citiesModel = db_init.CitiesDB()
            status = citiesModel.create_new_city(cityName)
            if (status == True):
                flash("Город успешно добавлен", "success")
                return redirect(url_for('admin_cities'))
            elif (status == 2):
                flash("Данный город уже существует в базе!", "danger")
                return redirect(url_for('admin_cities'))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_cities'))
    else:
        abort(403)


@app.route("/admin/cities/edit/<string:city_id>", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_cities_edit(city_id):
    if (current_user.superadmin):
        if request.method == "GET":
            citiesModel = db_init.CitiesDB()
            city = citiesModel.get_city_by_id(city_id)
            return render_template("admin/pages/cities/edit.html", title="Изменение города", city=city)
        if request.method == "POST":
            cityName = request.form.get("cityName")
            cities_model = db_init.CitiesDB()
            status = cities_model.edit_city_by_id(city_id=city_id, cityName=cityName)
            if (status == True):
                flash("Данные обновлены", "success")
                return redirect(url_for('admin_cities'))
            elif (status == 2):
                flash("Данный город уже существует в базе!", "danger")
                return redirect(url_for('admin_cities'))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_cities'))
    else:
        abort(403)


@app.route("/admin/cities/delete/<string:city_id>", methods=["GET"], strict_slashes=False)
@login_required
def admin_cities_delete(city_id):
    if (current_user.superadmin):
        if request.method == "GET":
            citiesModel = db_init.CitiesDB()
            status = citiesModel.delete_city_by_id(cityId=city_id)
            if (status == True):
                flash("Город успешно удален", "success")
                return redirect(url_for('admin_cities'))
    else:
        abort(403)


# Routing for seasons
@app.route("/admin/seasons", methods=["GET"], strict_slashes=False)
@login_required
def admin_seasons():
    if (current_user.superadmin or current_user.city_superadmin):
        if (current_user.superadmin):
            seasons = db_init.SeasonsDB().get_all_seasons()
        else:
            seasons = db_init.SeasonsDB().get_all_seasons(current_user.city_id.decode())
        return render_template("admin/pages/seasons/index.html", title="Сезоны", seasons=seasons)
    else:
        abort(403)


@app.route("/admin/seasons/create", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_seasons_create():
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            if (current_user.superadmin):
                cities = db_init.CitiesDB().get_all_cities()
            else:
                cities = db_init.CitiesDB().get_all_cities(current_user.city_id.decode())
            return render_template("admin/pages/seasons/create.html", title="Добавление сезона", cities=cities)
        if request.method == "POST":
            seasonName = request.form.get('seasonName')
            seasonDescription = request.form.get('seasonDescription')
            seasonCity = request.form.get('seasonCity')
            file = request.files['fileupload']
            image_string = None

            if (seasonCity == 'not'):
                flash("Выберите город", "danger")
                return redirect(url_for('admin_seasons'))

            if file and allowed_file(file.filename):
                image_string = base64.b64encode(file.read())
            else:
                flash("Поддерживаемые форматы для файла: png, jpg, jpeg, gif", "danger")
                return redirect(url_for('admin_seasons'))
            if (seasonName != '' and seasonDescription != '' and seasonCity != ''):
                seasonsModel = db_init.SeasonsDB()
                status = seasonsModel.create_new_season(seasonName=seasonName, seasonDescription=seasonDescription,
                                                        cityId=seasonCity, previewPhotoBase64=image_string.decode())
                if (status == True):
                    flash("Сезон успешно добавлен", "success")
                    return redirect(url_for('admin_seasons'))
                elif (status == 2):
                    flash("Данный сезон уже существует в базе!", "danger")
                    return redirect(url_for('admin_seasons'))
                elif (status == 3):
                    flash("Произошла непредвиденная ошибка!", "danger")
                    return redirect(url_for('admin_seasons'))
            else:
                flash("Заполните все необходимые поля", "danger")
                return redirect(url_for('admin_seasons'))
    else:
        abort(403)


@app.route("/admin/seasons/edit/<string:season_id>", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_seasons_edit(season_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            if (current_user.superadmin):
                seasonsModel = db_init.SeasonsDB()
                season = seasonsModel.get_season_by_id(season_id)
                cities = db_init.CitiesDB().get_all_cities()
            else:
                seasonsModel = db_init.SeasonsDB()
                season = seasonsModel.get_season_by_id(season_id)
                cities = db_init.CitiesDB().get_all_cities(current_user.city_id.decode())
            return render_template("admin/pages/seasons/edit.html", title="Изменение сезона", season=season,
                                   cities=cities)
        if request.method == "POST":
            seasonsModel = db_init.SeasonsDB()
            seasonName = request.form.get('seasonName')
            seasonDescription = request.form.get('seasonDescription')
            seasonCity = request.form.get('seasonCity')
            file = request.files['fileupload']
            image_string = None

            if (seasonCity == 'not'):
                flash("Выберите город", "danger")
                return redirect(url_for('admin_seasons'))
            elif (seasonCity != current_user.city_superadmin.decode()):
                flash("Вы не можете управлять данным городом", "danger")
                return redirect(url_for('admin_seasons'))

            if file.filename != '':
                if file and allowed_file(file.filename):
                    image_string = base64.b64encode(file.read())
                else:
                    flash("Поддерживаемые форматы для файла: png, jpg, jpeg, gif", "danger")
                    return redirect(url_for('admin_seasons'))
                status = seasonsModel.edit_season_by_id(seasonId=season_id, seasonName=seasonName,
                                                        seasonDescription=seasonDescription, cityId=seasonCity,
                                                        previewPhotoBase64=image_string.decode())
            else:
                status = seasonsModel.edit_season_by_id(seasonId=season_id, seasonName=seasonName,
                                                        seasonDescription=seasonDescription, cityId=seasonCity)
            if (status == True):
                flash("Сезон успешно обновлен", "success")
                return redirect(url_for('admin_seasons'))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_seasons'))
    else:
        abort(403)


@app.route("/admin/seasons/delete/<string:season_id>", methods=["GET"], strict_slashes=False)
@login_required
def admin_seasons_delete(season_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            seasonsModel = db_init.SeasonsDB()
            if (current_user.superadmin):
                status = seasonsModel.delete_season_by_id(seasonId=season_id)
            else:
                status = seasonsModel.delete_season_by_id(seasonId=season_id, city_id=current_user.city_id)
            if (status == True):
                flash("Сезон успешно удален", "success")
                return redirect(url_for('admin_seasons'))
    else:
        abort(403)


# Games routing
@app.route("/admin/games", methods=["GET"], strict_slashes=False)
@login_required
def admin_games():
    if (current_user.superadmin or current_user.city_superadmin):
        if (current_user.superadmin):
            games = db_init.GamesDB().get_all_games()
        else:
            games = db_init.GamesDB().get_all_games(current_user.city_id.decode())
        return render_template("admin/pages/games/index.html", title="Игры", games=games)
    else:
        abort(403)


@app.route("/admin/games/create", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_games_create():
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            if (current_user.superadmin):
                cities = db_init.CitiesDB().get_all_cities()
                seasons = db_init.SeasonsDB().get_all_seasons()
                gametypes = db_init.GametypesDB().get_all_gametypes()
            else:
                cities = db_init.CitiesDB().get_all_cities(current_user.city_id.decode())
                seasons = db_init.SeasonsDB().get_all_seasons(current_user.city_id.decode())
                gametypes = db_init.GametypesDB().get_all_gametypes()
            return render_template("admin/pages/games/create.html", title="Добавление игры", cities=cities,
                                   seasons=seasons, gametypes=gametypes)
        if request.method == "POST":
            gameName = request.form.get('gameName')
            gameDescription = request.form.get('gameDescription')
            gameDate = request.form.get('gameDate')
            gameLocation = request.form.get('gameLocation')
            gameCity = request.form.get('gameCity')
            gameType = request.form.get('gameType')
            gameSeason = request.form.get('season')
            reserveLink = request.form.get('reserveLink')
            file = request.files['fileupload']
            image_string = None

            if (gameCity == 'not'):
                flash("Выберите город", "danger")
                return redirect(url_for('admin_games'))

            if (gameSeason == 'not'):
                flash("Выберите сезон", "danger")
                return redirect(url_for('admin_games'))

            if (gameType == 'not'):
                flash("Выберите тип игры", "danger")
                return redirect(url_for('admin_games'))

            if file and allowed_file(file.filename):
                image_string = base64.b64encode(file.read())
            else:
                flash("Поддерживаемые форматы для файла: png, jpg, jpeg, gif", "danger")
                return redirect(url_for('admin_games'))

            if (
                    gameName != '' and gameLocation != '' and gameCity != '' and gameDescription != '' and reserveLink != '' and gameType != ''):
                gamesModel = db_init.GamesDB()
                status = gamesModel.create_new_game(gameName=gameName, gameDescription=gameDescription,
                                                    gameTypeId=gameType, gameDate=gameDate, location=gameLocation,
                                                    season_id=gameSeason, city_id=gameCity, bookingLink=reserveLink,
                                                    previewPhotoBase64=image_string.decode())
                if (status == True):
                    flash("Игра успешно добавлена", "success")
                    return redirect(url_for('admin_games'))
                elif (status == 2):
                    flash("Данный игра уже существует в базе!", "danger")
                    return redirect(url_for('admin_games'))
                elif (status == 3):
                    flash("Произошла непредвиденная ошибка!", "danger")
                    return redirect(url_for('admin_games'))
            else:
                flash("Заполните все необходимые поля", "danger")
                return redirect(url_for('admin_games'))
    else:
        abort(403)


@app.route("/admin/games/edit/<string:game_id>", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_games_edit(game_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            if (current_user.superadmin):
                seasons = db_init.SeasonsDB().get_all_seasons()
                cities = db_init.CitiesDB().get_all_cities()
                gamesModel = db_init.GamesDB()
                game = gamesModel.get_game_by_id(game_id)
                gametypes = db_init.GametypesDB().get_all_gametypes()
            else:
                seasons = db_init.SeasonsDB().get_all_seasons(current_user.city_id.decode())
                cities = db_init.CitiesDB().get_all_cities(current_user.city_id.decode())
                gamesModel = db_init.GamesDB()
                game = gamesModel.get_game_by_id(game_id)
                gametypes = db_init.GametypesDB().get_all_gametypes()
            return render_template("admin/pages/games/edit.html", title="Изменение игры", seasons=seasons,
                                   cities=cities, game=game, gametypes=gametypes)
        if request.method == "POST":
            gamesModel = db_init.GamesDB()
            gameName = request.form.get('gameName')
            gameDescription = request.form.get('gameDescription')
            gameDate = request.form.get('gameDate')
            gameLocation = request.form.get('gameLocation')
            gameCity = request.form.get('gameCity')
            gameType = request.form.get('gameType')
            gamePublished = request.form.get('published') != None
            gameScorePublished = request.form.get('scorePublished') != None
            gameSeason = request.form.get('season')
            reserveLink = request.form.get('reserveLink')
            file = request.files['fileupload']
            image_string = None

            if (gameCity == 'not'):
                flash("Выберите город", "danger")
                return redirect(url_for('admin_games'))

            if (gameSeason == 'not'):
                flash("Выберите сезон", "danger")
                return redirect(url_for('admin_games'))

            if (gameType == 'not'):
                flash("Выберите тип игры", "danger")
                return redirect(url_for('admin_games'))

            if file.filename != '':
                if file and allowed_file(file.filename):
                    image_string = base64.b64encode(file.read())
                else:
                    flash("Поддерживаемые форматы для файла: png, jpg, jpeg, gif", "danger")
                    return redirect(url_for('admin_seasons'))
                status = gamesModel.edit_game_by_id(game_id=game_id, gameName=gameName, gameDescription=gameDescription,
                                                    gameTypeId=gameType, gameDate=gameDate, location=gameLocation,
                                                    city_id=gameCity, season_id=gameSeason, bookingLink=reserveLink,
                                                    published=gamePublished, scorePublished=gameScorePublished,
                                                    previewPhotoBase64=image_string.decode())
            else:
                status = gamesModel.edit_game_by_id(game_id=game_id, gameName=gameName, gameDescription=gameDescription,
                                                    gameTypeId=gameType, gameDate=gameDate, location=gameLocation,
                                                    city_id=gameCity, season_id=gameSeason, bookingLink=reserveLink,
                                                    published=gamePublished, scorePublished=gameScorePublished)
            if (status == True):
                flash("Игра успешно обновлена", "success")
                return redirect(url_for('admin_games'))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_games'))
    else:
        abort(403)


@app.route("/admin/games/delete/<string:game_id>", methods=["GET"], strict_slashes=False)
@login_required
def admin_games_delete(game_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            if (current_user.superadmin):
                gamesModel = db_init.GamesDB()
                status = gamesModel.delete_game_by_id(gameId=game_id)
            else:
                gamesModel = db_init.GamesDB()
                status = gamesModel.delete_game_by_id(gameId=game_id, city_id=current_user.city_id.decode())
            if (status == True):
                flash("Игра успешно удалена", "success")
                return redirect(url_for('admin_games'))
    else:
        abort(403)


# Rounds Route
@app.route("/admin/rounds", methods=["GET"], strict_slashes=False)
@login_required
def admin_rounds():
    if (current_user.superadmin or current_user.city_superadmin):
        if (current_user.superadmin):
            games = db_init.GamesDB().get_all_games()
        else:
            games = db_init.GamesDB().get_all_games(current_user.city_id.decode())
        return render_template("admin/pages/rounds/index.html", title="Игры", games=games)
    else:
        abort(403)


@app.route("/admin/rounds/show/<string:game_id>", methods=["GET"], strict_slashes=False)
@login_required
def admin_rounds_show(game_id):
    if (current_user.superadmin or current_user.city_superadmin):
        roundsModel = db_init.RoundsDB()
        return render_template("admin/pages/rounds/show.html", title="Раунды",
                               rounds=roundsModel.get_all_rounds(game_id), game_id=game_id)
    else:
        abort(403)


@app.route("/admin/rounds/create/<string:game_id>", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_rounds_create(game_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            return render_template("admin/pages/rounds/create.html", title="Добавление раунда", game=game_id)
        if request.method == "POST":
            roundsCount = request.form.get("rounds")
            roundsModel = db_init.RoundsDB()
            status = roundsModel.create_new_rounds(game_id=game_id, roundsCount=int(roundsCount))
            if (status == True):
                flash("Раунд успешно добавлен", "success")
                return redirect(url_for('admin_rounds_show', game_id=game_id))
            elif (status == 2):
                flash("Данный раунд уже существует в базе!", "danger")
                return redirect(url_for('admin_rounds_show', game_id=game_id))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_rounds_show', game_id=game_id))
    else:
        abort(403)


@app.route("/admin/rounds/delete/<string:round_id>/<string:game_id>", methods=["GET"], strict_slashes=False)
@login_required
def admin_rounds_delete(round_id, game_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            roundsModel = db_init.RoundsDB()
            status = roundsModel.delete_round_by_id(round_id=round_id)
            if (status == True):
                flash("Раунд успешно удален", "success")
                return redirect(url_for('admin_rounds_show', game_id=game_id))
    else:
        abort(403)


# Teams Route
@app.route("/admin/teams", methods=["GET"], strict_slashes=False)
@login_required
def admin_teams():
    if (current_user.superadmin or current_user.city_superadmin):
        teamsModel = db_init.TeamsDB()
        return render_template("admin/pages/teams/index.html", title="Команды", teams=teamsModel.get_all_teams())
    else:
        abort(403)


@app.route("/admin/teams/create", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_teams_create():
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            return render_template("admin/pages/teams/create.html", title="Добавление команды")
        if request.method == "POST":
            teamName = request.form.get("teamName")
            teamModel = db_init.TeamsDB()
            status = teamModel.create_new_team(teamName)
            if (status == True):
                flash("Команда успешно добавлена", "success")
                return redirect(url_for('admin_teams'))
            elif (status == 2):
                flash("Данная команда уже существует в базе!", "danger")
                return redirect(url_for('admin_teams'))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_teams'))
    else:
        abort(403)


@app.route("/admin/teams/edit/<string:team_id>", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_teams_edit(team_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            teamsModel = db_init.TeamsDB()
            team = teamsModel.get_team_by_id(team_id)
            return render_template("admin/pages/teams/edit.html", title="Изменение команды", team=team)
        if request.method == "POST":
            teamName = request.form.get("teamName")
            teamsModel = db_init.TeamsDB()
            status = teamsModel.edit_team_by_id(team_id=team_id, teamName=teamName)
            if (status == True):
                flash("Данные обновлены", "success")
                return redirect(url_for('admin_teams'))
            elif (status == 2):
                flash("Данная команда уже существует в базе!", "danger")
                return redirect(url_for('admin_teams'))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_teams'))
    else:
        abort(403)


@app.route("/admin/teams/delete/<string:team_id>", methods=["GET"], strict_slashes=False)
@login_required
def admin_teams_delete(team_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            teamsModel = db_init.TeamsDB()
            status = teamsModel.delete_team_by_id(teamId=team_id)
            if (status == True):
                flash("Команда успешно удалена", "success")
                return redirect(url_for('admin_teams'))
            else:
                flash("Произошла непредвиденная ошибка", "danger")
                return redirect(url_for('admin_teams'))
    else:
        abort(403)


# Tables Route
@app.route("/admin/tables", methods=["GET"], strict_slashes=False)
@login_required
def admin_tables():
    if (current_user.superadmin):
        games = db_init.GamesDB().get_all_games()
    else:
        games = db_init.GamesDB().get_all_games(current_user.city_id.decode())
    return render_template("admin/pages/tables/index.html", title="Игры", games=games)


@app.route("/admin/tables/show/<string:game_id>", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_tables_show(game_id):
    if (current_user.superadmin or db_init.RoundsDB().admin_permission_check(game_id, current_user.city_id.decode())):
        if request.method == "GET":
            teamsModel = db_init.TeamsDB()
            scoresModel = db_init.ScoresDB()
            roundsModel = db_init.RoundsDB()

            teams = teamsModel.get_all_teams()
            scoresDictionary = scoresModel.get_scores_by_game_id(game_id=game_id)
            rounds = roundsModel.get_all_rounds(game_id=game_id)
            return render_template("admin/pages/tables/show.html", title="Таблица", rounds=rounds,
                                   scoresDictionary=scoresDictionary, teams=teams, game_id=game_id)
        if request.method == "POST":
            scoresModel = db_init.ScoresDB()
            dictionary = request.form.to_dict()
            print(dictionary)
            status = scoresModel.add_scores(dictionary=dictionary)
            if (status == True):
                flash("Данные обновлены", "success")
                return redirect(url_for('admin_tables_show', game_id=game_id))
            else:
                flash("Произошла непредвиденная ошибка", "danger")
                return redirect(url_for('admin_tables_show', game_id=game_id))
    else:
        abort(403)


# Games routing
@app.route("/admin/events", methods=["GET"], strict_slashes=False)
@login_required
def admin_events():
    if (current_user.superadmin or current_user.city_superadmin):
        if (current_user.superadmin):
            events = db_init.EventsDB().get_all_events()
        else:
            events = db_init.EventsDB().get_all_events(current_user.city_id.decode())

        return render_template("admin/pages/events/index.html", title="Мероприятия", events=events)
    else:
        abort(403)


@app.route("/admin/events/create", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_events_create():
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            if (current_user.superadmin):
                cities = db_init.CitiesDB().get_all_cities()
            else:
                cities = db_init.CitiesDB().get_all_cities(current_user.city_id.decode())
            return render_template("admin/pages/events/create.html", title="Добавление мероприятия", cities=cities)

        if request.method == "POST":
            eventName = request.form.get('eventName')
            eventDescription = request.form.get('eventDescription')
            eventDate = request.form.get('eventDate')
            eventCost = request.form.get('eventCost')
            eventLocation = request.form.get('eventLocation')
            eventCity = request.form.get('eventCity')
            reserveLink = request.form.get('reserveLink')
            file = request.files['fileupload']
            image_string = None

            if (eventCity == 'not'):
                flash("Выберите город", "danger")
                return redirect(url_for('admin_events'))

            if file and allowed_file(file.filename):
                image_string = base64.b64encode(file.read())
            else:
                flash("Поддерживаемые форматы для файла: png, jpg, jpeg, gif", "danger")
                return redirect(url_for('admin_events'))

            if (
                    eventName != '' and eventLocation != '' and eventCity != '' and eventDescription != '' and reserveLink != '' and eventCost != ''):
                eventsModel = db_init.EventsDB()
                status = eventsModel.create_new_event(eventName=eventName, eventDescription=eventDescription,
                                                      eventDate=eventDate, eventCost=eventCost, location=eventLocation,
                                                      city_id=eventCity, bookingLink=reserveLink,
                                                      previewPhotoBase64=image_string.decode())
                if (status == True):
                    flash("Мероприятие добавлено", "success")
                    return redirect(url_for('admin_events'))
                else:
                    flash("Произошла непредвиденная ошибка!", "danger")
                    return redirect(url_for('admin_events'))
            else:
                flash("Заполните все необходимые поля", "danger")
                return redirect(url_for('admin_events'))
    else:
        abort(403)


@app.route("/admin/events/edit/<string:event_id>", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_events_edit(event_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            if (current_user.superadmin):
                event = db_init.EventsDB().get_event_by_id(event_id)
                cities = db_init.CitiesDB().get_all_cities()
            else:
                event = db_init.EventsDB().get_event_by_id(event_id)
                cities = db_init.CitiesDB().get_all_cities(current_user.city_id.decode())
            return render_template("admin/pages/events/edit.html", title="Изменение мероприятия", cities=cities,
                                   event=event)
        if request.method == "POST":
            eventsModel = db_init.EventsDB()
            eventPublished = request.form.get('published') != None
            eventName = request.form.get('eventName')
            eventDescription = request.form.get('eventDescription')
            eventDate = request.form.get('eventDate')
            eventCost = request.form.get('eventCost')
            eventLocation = request.form.get('eventLocation')
            eventCity = request.form.get('eventCity')
            reserveLink = request.form.get('reserveLink')
            file = request.files['fileupload']
            image_string = None

            if (eventCity == 'not'):
                flash("Выберите город", "danger")
                return redirect(url_for('admin_events'))

            if file.filename != '':
                if file and allowed_file(file.filename):
                    image_string = base64.b64encode(file.read())
                else:
                    flash("Поддерживаемые форматы для файла: png, jpg, jpeg, gif", "danger")
                    return redirect(url_for('admin_events'))
                status = eventsModel.edit_event_by_id(event_id=event_id, eventName=eventName,
                                                      eventDescription=eventDescription, eventCost=eventCost,
                                                      eventDate=eventDate, location=eventLocation, city_id=eventCity,
                                                      bookingLink=reserveLink, published=eventPublished,
                                                      previewPhotoBase64=image_string.decode())
            else:
                status = eventsModel.edit_event_by_id(event_id=event_id, eventName=eventName,
                                                      eventDescription=eventDescription, eventCost=eventCost,
                                                      eventDate=eventDate, location=eventLocation, city_id=eventCity,
                                                      bookingLink=reserveLink, published=eventPublished)
            if (status == True):
                flash("Данные обновлены", "success")
                return redirect(url_for('admin_events'))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_events'))
    else:
        abort(403)


@app.route("/admin/events/delete/<string:event_id>", methods=["GET"], strict_slashes=False)
@login_required
def admin_events_delete(event_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            eventsModel = db_init.EventsDB()
            status = eventsModel.delete_event_by_id(eventId=event_id)
            if (status == True):
                flash("Мероприятие успешно удалено", "success")
                return redirect(url_for('admin_events'))
    else:
        abort(403)


# Routing for photos
@app.route("/admin/photos", methods=["GET"], strict_slashes=False)
@login_required
def admin_photos():
    if (current_user.superadmin or current_user.city_superadmin):
        if (current_user.superadmin):
            photos = db_init.PhotosDB().get_all_photos()
        else:
            photos = db_init.PhotosDB().get_all_photos(current_user.city_id.decode())
        return render_template("admin/pages/photos/index.html", title="Фотоотчеты", photos=photos)
    else:
        abort(403)


@app.route("/admin/photos/create", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_photos_create():
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            if (current_user.superadmin):
                games = db_init.GamesDB().get_all_games()
            else:
                games = db_init.GamesDB().get_all_games(current_user.city_id.decode())
            return render_template("admin/pages/photos/create.html", title="Добавление фотоотчета", games=games)
        if request.method == "POST":
            game_id = request.form.get('game')
            photoLink = request.form.get('photoLink')
            file = request.files['fileupload']
            image_string = None

            if (game_id == 'not'):
                flash("Выберите игру", "danger")
                return redirect(url_for('admin_photos'))

            if file and allowed_file(file.filename):
                image_string = base64.b64encode(file.read())
            else:
                flash("Поддерживаемые форматы для файла: png, jpg, jpeg, gif", "danger")
                return redirect(url_for('admin_photos'))
            if (game_id != '' and photoLink != ''):
                photosModel = db_init.PhotosDB()
                status = photosModel.create_new_photos(game_id=game_id, photoLink=photoLink,
                                                       previewPhotoBase64=image_string.decode())
                if (status == True):
                    flash("Фотоотчет успешно добавлен", "success")
                    return redirect(url_for('admin_photos'))
                else:
                    flash("Произошла непредвиденная ошибка!", "danger")
                    return redirect(url_for('admin_photos'))
            else:
                flash("Заполните все необходимые поля", "danger")
                return redirect(url_for('admin_photos'))
    else:
        abort(403)


@app.route("/admin/photos/edit/<string:game_id>", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_photos_edit(game_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            photosModel = db_init.PhotosDB()
            gamesModel = db_init.GamesDB()
            if (current_user.superadmin):
                photo = photosModel.get_photos_by_id(game_id)
                games = gamesModel.get_all_games()
            else:
                photo = photosModel.get_photos_by_id(game_id)
                games = gamesModel.get_all_games(current_user.city_id.decode())
            return render_template("admin/pages/photos/edit.html", title="Изменение фотоотчета", games=games,
                                   photo=photo)
        if request.method == "POST":
            photosModel = db_init.PhotosDB()
            game_id = request.form.get('game')
            photoLink = request.form.get('photoLink')
            file = request.files['fileupload']
            image_string = None

            if (game_id == 'not'):
                flash("Выберите игру", "danger")
                return redirect(url_for('admin_photos'))

            if file.filename != '':
                if file and allowed_file(file.filename):
                    image_string = base64.b64encode(file.read())
                else:
                    flash("Поддерживаемые форматы для файла: png, jpg, jpeg, gif", "danger")
                    return redirect(url_for('admin_photos'))
                status = photosModel.edit_photos_by_id(game_id=game_id, photoLink=photoLink,
                                                       previewPhotoBase64=image_string.decode())
            else:
                status = photosModel.edit_photos_by_id(game_id=game_id, photoLink=photoLink)
            if (status == True):
                flash("Фотоотчет успешно обновлен", "success")
                return redirect(url_for('admin_photos'))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_photos'))
    else:
        abort(403)


@app.route("/admin/photos/delete/<string:game_id>", methods=["GET"], strict_slashes=False)
@login_required
def admin_photos_delete(game_id):
    if (current_user.superadmin or current_user.city_superadmin):
        if request.method == "GET":
            photosModel = db_init.PhotosDB()
            status = photosModel.delete_photos_by_id(gameId=game_id)
            if (status == True):
                flash("Фотоотчет успешно удален", "success")
                return redirect(url_for('admin_photos'))
    else:
        abort(403)


# Routing for game types
@app.route("/admin/gametypes", methods=["GET"], strict_slashes=False)
@login_required
def admin_gametypes():
    if (current_user.superadmin):
        gametypesModel = db_init.GametypesDB()
        return render_template("admin/pages/gametypes/index.html", title="Города",
                               gametypes=gametypesModel.get_all_gametypes())
    else:
        abort(403)


@app.route("/admin/gametypes/create", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_gametypes_create():
    if (current_user.superadmin):
        if request.method == "GET":
            return render_template("admin/pages/gametypes/create.html", title="Добавление тип игры")
        if request.method == "POST":
            gameType = request.form.get("gametype")
            gameTypesModel = db_init.GametypesDB()
            status = gameTypesModel.create_new_gametype(gameType)
            if (status == True):
                flash("Тип игры успешно добавлена", "success")
                return redirect(url_for('admin_gametypes'))
            elif (status == 2):
                flash("Данный тип игры уже существует в базе!", "danger")
                return redirect(url_for('admin_gametypes'))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_gametypes'))
    else:
        abort(403)


@app.route("/admin/gametypes/edit/<string:game_type_id>", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_gametypes_edit(game_type_id):
    if (current_user.superadmin):
        if request.method == "GET":
            gametypesModel = db_init.GametypesDB()
            gametype = gametypesModel.get_gametype_by_id(game_type_id)
            return render_template("admin/pages/gametypes/edit.html", title="Изменение тип игры", gametype=gametype)
        if request.method == "POST":
            gameType = request.form.get("gametype")
            gametypesModel = db_init.GametypesDB()
            status = gametypesModel.edit_gametype_by_id(gameTypeId=game_type_id, gameTypeName=gameType)
            if (status == True):
                flash("Данные обновлены", "success")
                return redirect(url_for('admin_gametypes'))
            elif (status == 2):
                flash("Данный тип игры уже существует в базе!", "danger")
                return redirect(url_for('admin_gametypes'))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_gametypes'))
    else:
        abort(403)


@app.route("/admin/gametypes/delete/<string:game_type_id>", methods=["GET"], strict_slashes=False)
@login_required
def admin_gametypes_delete(game_type_id):
    if (current_user.superadmin):
        if request.method == "GET":
            gametypesModel = db_init.GametypesDB()
            status = gametypesModel.delete_gametype_by_id(gameTypeId=game_type_id)
            if (status == True):
                flash("Тип игры успешно удален", "success")
                return redirect(url_for('admin_gametypes'))
    else:
        abort(403)


# Routing for catalog
@app.route("/admin/catalog", methods=["GET"], strict_slashes=False)
@login_required
def admin_catalog():
    if (current_user.superadmin):
        catalogModel = db_init.CatalogDB()
        return render_template("admin/pages/catalog/index.html", title="Каталог",
                               catalog=catalogModel.get_all_catalog())
    else:
        abort(403)


@app.route("/admin/catalog/create", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_catalog_create():
    if (current_user.superadmin):
        if request.method == "GET":
            return render_template("admin/pages/catalog/create.html", title="Добавление товара")
        if request.method == "POST":
            itemName = request.form.get('itemName')
            itemDescription = request.form.get('itemDescription')
            itemCost = request.form.get('itemCost')
            bookingLink = request.form.get('bookingLink')
            file = request.files['fileupload']
            image_string = None

            if file and allowed_file(file.filename):
                image_string = base64.b64encode(file.read())
            else:
                flash("Поддерживаемые форматы для файла: png, jpg, jpeg, gif", "danger")
                return redirect(url_for('admin_catalog'))
            if (itemName != '' and itemDescription != '' and itemCost != '' and bookingLink != ''):
                catalogModel = db_init.CatalogDB()
                status = catalogModel.create_new_item(itemName=itemName, itemDescription=itemDescription,
                                                      itemCost=itemCost, bookingLink=bookingLink,
                                                      previewPhotoBase64=image_string.decode())
                if (status == True):
                    flash("Товар успешно добавлен", "success")
                    return redirect(url_for('admin_catalog'))
                else:
                    flash("Произошла непредвиденная ошибка!", "danger")
                    return redirect(url_for('admin_catalog'))
            else:
                flash("Заполните все необходимые поля", "danger")
                return redirect(url_for('admin_catalog'))
    else:
        abort(403)


@app.route("/admin/catalog/edit/<string:item_id>", methods=["GET", "POST"], strict_slashes=False)
@login_required
def admin_catalog_edit(item_id):
    if (current_user.superadmin):
        if request.method == "GET":
            catalogModel = db_init.CatalogDB()
            return render_template("admin/pages/catalog/edit.html", title="Изменение товара",
                                   item=catalogModel.get_item_by_id(item_id))
        if request.method == "POST":
            catalogModel = db_init.CatalogDB()
            itemName = request.form.get('itemName')
            itemDescription = request.form.get('itemDescription')
            itemCost = request.form.get('itemCost')
            bookingLink = request.form.get('bookingLink')
            file = request.files['fileupload']
            image_string = None

            if file.filename != '':
                if file and allowed_file(file.filename):
                    image_string = base64.b64encode(file.read())
                else:
                    flash("Поддерживаемые форматы для файла: png, jpg, jpeg, gif", "danger")
                    return redirect(url_for('admin_catalog'))
                if (itemName != '' and itemDescription != '' and itemCost != '' and bookingLink != ''):
                    status = catalogModel.edit_item_by_id(item_id=item_id, itemName=itemName,
                                                          itemDescription=itemDescription, itemCost=itemCost,
                                                          bookingLink=bookingLink,
                                                          previewPhotoBase64=image_string.decode())
            else:
                status = catalogModel.edit_item_by_id(item_id=item_id, itemName=itemName,
                                                      itemDescription=itemDescription,
                                                      itemCost=itemCost, bookingLink=bookingLink)
            if (status == True):
                flash("Товар успешно обновлен", "success")
                return redirect(url_for('admin_catalog'))
            elif (status == 3):
                flash("Произошла непредвиденная ошибка!", "danger")
                return redirect(url_for('admin_catalog'))
    else:
        abort(403)


@app.route("/admin/catalog/delete/<string:item_id>", methods=["GET"], strict_slashes=False)
@login_required
def admin_catalog_delete(item_id):
    if (current_user.superadmin):
        if request.method == "GET":
            catalogModel = db_init.CatalogDB()
            status = catalogModel.delete_item_by_id(itemId=item_id)
            if (status == True):
                flash("Товар успешно удален", "success")
                return redirect(url_for('admin_catalog'))
    else:
        abort(403)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/")
@app.route("/index", methods=['GET'])
def index():
    # Получаем город от пользователя, если None, то город не выбран
    selected_city = None
    selected_city = request.args.get("selectedCity")
    # Получаем все города из бд и отправляем их на сайт
    cityModel = db_init.CitiesDB()
    gamesModel = db_init.GamesDB()
    seasonsModel = db_init.SeasonsDB()
    photosModel = db_init.PhotosDB()
    allCities = cityModel.get_all_cities()
    cities = {}
    for i in range(len(allCities)):
        cities[allCities[i][1]] = allCities[i][0]
    if selected_city is not None:
        try:
            next_games = []
            last_photos = []
            all_games = gamesModel.get_all_games(cities.get(selected_city),
                                                 seasonsModel.get_last_season(cities.get(selected_city))[0][0])
            last_photos = photosModel.get_all_photos(cities.get(selected_city))
            for i in range(len(all_games)):
                if all_games[i][4] > datetime.datetime.now() and all_games[i][8]:
                    next_games.append([all_games[i][1], all_games[i][4], all_games[i][6], str(all_games[i][10])[1:]])

            if len(next_games) > 3:
                del (next_games[3:len(next_games)])

            if len(last_photos) > 3:
                del (last_photos[3:len(last_photos)])
            return render_template('index.html', cityNames=list(cities.keys()), next_games=next_games,
                                   last_photos=last_photos)
        except IndexError:
            pass
    return render_template('index.html', cityNames=list(cities.keys()))


@app.route("/shedule", methods=['GET'])
@app.route("/shedule.html", methods=['GET'])
def shedule():
    selected_city = request.args.get("selectedCity")
    selected_game_type = request.args.get("game-type")
    print(selected_game_type)
    cityModel = db_init.CitiesDB()
    gamesModel = db_init.GamesDB()
    seasonsModel = db_init.SeasonsDB()
    gametypesModel = db_init.GametypesDB()
    game_types = gametypesModel.get_all_gametypes()

    allCities = cityModel.get_all_cities()
    cities = {}
    for i in range(len(allCities)):
        cities[allCities[i][1]] = allCities[i][0]

    if selected_city is not None:
        all_games = gamesModel.get_all_published_games(cities.get(selected_city),
                                                       seasonsModel.get_last_season(cities.get(selected_city))[0][0])
        for i in range(len(all_games)):
            if all_games[i][4] > datetime.datetime.now():
                del (all_games[0:i])
                break
        if selected_game_type == "all" or selected_game_type is None:
            return render_template('shedule.html', cityNames=list(cities.keys()), game_types=game_types,
                                   selected_games=all_games)
        elif selected_game_type != "all":
            selected_games = []
            for i in range(len(all_games)):
                if all_games[i][3] == selected_game_type:
                    selected_games.append(all_games[i])
            return render_template('shedule.html', cityNames=list(cities.keys()), game_types=game_types,
                                   selected_games=selected_games)

    return render_template('shedule.html', game_types=game_types, cityNames=list(cities.keys()))


@app.route("/photos")
def photos():
    selected_city = request.args.get("selectedCity")
    cityModel = db_init.CitiesDB()
    photosModel = db_init.PhotosDB()

    allCities = cityModel.get_all_cities()
    cities = {}
    for i in range(len(allCities)):
        cities[allCities[i][1]] = allCities[i][0]

    if selected_city is not None:
        all_photos = photosModel.get_all_photos(cities.get(selected_city))
        all_photos.reverse()
        return render_template('photos.html', cityNames=list(cities.keys()), all_photos=all_photos)
    return render_template('photos.html', cityNames=list(cities.keys()))


@app.route("/events")
def events():
    selected_city = request.args.get("selectedCity")
    cityModel = db_init.CitiesDB()
    eventsModel = db_init.EventsDB()

    allCities = cityModel.get_all_cities()
    cities = {}
    for i in range(len(allCities)):
        cities[allCities[i][1]] = allCities[i][0]

    if selected_city is not None:
        all_events = eventsModel.get_all_events(cities.get(selected_city))
        return render_template('events.html', cityNames=list(cities.keys()), all_events=all_events)
    return render_template('events.html', cityNames=list(cities.keys()))


@app.route("/table", methods=['GET'])
def table():
    selected_city = request.args.get("selectedCity")
    selected_game = request.args.get("selectedGame")
    cityModel = db_init.CitiesDB()
    gamesModel = db_init.GamesDB()
    seasonsModel = db_init.SeasonsDB()
    scoreModel = db_init.ScoresDB()

    allCities = cityModel.get_all_cities()
    cities = {}
    for i in range(len(allCities)):
        cities[allCities[i][1]] = allCities[i][0]

    if selected_city is not None:
        comands_score = {}
        all_results = []
        all_games = gamesModel.get_all_games_with_score(cities.get(selected_city),
                                                        seasonsModel.get_last_season(cities.get(selected_city))[0][0])
        games_names_id = {}
        for i in range(len(all_games)):
            games_names_id[all_games[i][1]] = all_games[i][0]
            all_results.append(scoreModel.get_scores_by_game_id(all_games[i][0]))
        game_counter = Counter()
        for d in all_results:
            game_counter.update(d.keys())
        # Считаю результаты за последний сезон
        for i in range(len(all_results)):
            for keys, values in all_results[i].items():
                if comands_score.get(keys, 0) == 0:
                    comands_score[keys] = int(values[0][4])
                else:
                    comands_score[keys] += int(values[0][4])
        # Получаю результаты за выбранную игру
        if selected_game is not None:
            game_result = scoreModel.get_scores_by_game_id(games_names_id.get(selected_game))
            return render_template('table.html', game_counter=dict(game_counter), comands_score=comands_score,
                                   game_result=game_result, selected_game=selected_game, game_names=games_names_id,
                                   round_counter=len(list(game_result.values())[0]), cityNames=list(cities.keys()))
        else:
            game_result = scoreModel.get_scores_by_game_id(
                games_names_id.get(collections.deque(games_names_id, maxlen=1)[0]))
            round_counter = len(list(game_result.values())[0])
            return render_template('table.html', game_counter=dict(game_counter), comands_score=comands_score,
                                   game_result=game_result,
                                   selected_game=collections.deque(games_names_id, maxlen=1)[0],
                                   game_names=games_names_id, round_counter=round_counter,
                                   cityNames=list(cities.keys()))

        # game_counter - {"Название команды": Количество посещённых игр}
        # Comands_score - {"Название команды": int(Количество набранных очков за все игры)}
    return render_template('table.html', game_counter={}, comands_score={}, cityNames=list(cities.keys()),
                           game_names={}, round_counter=0, game_result={})


@app.route("/shop")
def shop():
    catalogModel = db_init.CatalogDB()
    all_catalog = catalogModel.get_all_catalog()
    return render_template('shop.html', all_catalog=all_catalog)


@app.route("/contacts")
@app.route("/contacts.html")
def contacts():
    return render_template('contacts.html')


if __name__ == "__main__":
    app.run(debug=True)
