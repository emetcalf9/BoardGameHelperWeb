from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session
)
import random
from bghweb.BGGAPI import *

from bghweb.auth import login_required
from bghweb.db import get_db

bp = Blueprint('collection', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    dbcur = db.cursor()
    dbcur.execute(
        "SELECT g.*, CASE c.favorite WHEN 1 THEN 'Yes' ELSE 'No' END "
        " FROM collection c LEFT OUTER JOIN games g ON c.game_id = g.id"
        " WHERE c.user_id = %s;", (session['user_id'],)
    )
    games = dbcur.fetchall()
    dbcur.execute("SELECT name, games_played FROM players "
                            "WHERE user_id = %s;", (session['user_id'],))
    players = dbcur.fetchall()
    return render_template('collection/index.html', games=games, players=players)


@bp.route('/addgame', methods=('GET', 'POST'))
@login_required
def addgame():
    if request.method == 'POST':
        name = request.form['name']
        favorite = request.form['favorite']
        error = None

        if not name:
            error = 'Name is required.'

        if error is None:
            results = search_games(name)
            if len(results) == 1:
                game_id = results[0][0]
                game_info = get_game_info(game_id)
                db = get_db()
                dbcur = db.cursor()
                dbcur.execute("Select id from games where id = %s;", (game_id,))
                game_exists = dbcur.fetchone()
                if not game_exists:
                    dbcur.execute('INSERT INTO games (id, name, minplay, maxplay) VALUES (%s, %s, %s, %s);', game_info)
                    db.commit()

                dbcur.execute('INSERT INTO collection (user_id, game_id, favorite) VALUES (%s, %s, %s);',
                              (session['user_id'], game_id, favorite))
                db.commit()
                flash("Added Successfully")
                return redirect(url_for('index'))
            else:
                return render_template('collection/searchresults.html', game_list=results)

        flash(error)

    return render_template('collection/addgame.html')


@bp.route('/pickgame', methods=('GET', 'POST'))
@login_required
def pickgame():
    if request.method == 'POST':
        numplayers = request.form['numplayers']
        error = None

        if not numplayers:
            error = 'Number of players is required'

        if error is None:
            db = get_db()
            dbcur = db.cursor()
            dbcur.execute(
                "Select id, Name from games where %s between minplay and maxplay;", (numplayers,))
            options = dbcur.fetchall()
            if not options:
                error = 'No games support that number of players. Try again'
                flash(error)
                return render_template('collection/pickgame.html')
            picked_game = random.randint(0, len(options) - 1)
            return render_template('collection/gameresult.html',
                                   game=options[picked_game][1])

        flash(error)

    return render_template('collection/pickgame.html')


@bp.route('/pickplayer', methods=('GET', 'POST'))
@login_required
def pickplayer():
    if request.method == 'POST':
        playertext = request.form['playerlist']
        error = None

        if not playertext:
            error = "You didn't list any players. Try again"

        if error is None:
            db = get_db()
            dbcur = db.cursor()
            playerlist = playertext.split()
            for player in playerlist:
                dbcur.execute('SELECT id from players WHERE user_id = %s and upper(name) = upper(%s);',
                                          (session['user_id'], player))
                player_id = dbcur.fetchone()
                if not player_id:
                    dbcur.execute('INSERT INTO players (user_id, name) VALUES (%s, %s);',
                                  (session['user_id'], player))
                    db.commit()
            pickagainlist = "_".join(playerlist)
            return render_template('collection/firstplayer.html',
                                   name=playerlist[random.randint(0, len(playerlist) - 1)],
                                   pickagainlist=pickagainlist)
        flash(error)

    return render_template('collection/pickplayer.html')


@bp.route('/togglefavorite/<id>', methods=['GET'])
@login_required
def togglefavorite(id):
    db = get_db()
    dbcur = db.cursor()
    dbcur.execute(
        "UPDATE collection set favorite = ((favorite | 1) - (favorite & 1)) where user_id = %s and game_id = %s;",
        (session['user_id'], id))
    db.commit()
    return redirect(url_for('index'))
