from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
import random

from bghweb.auth import login_required
from bghweb.db import get_db

bp = Blueprint('collection', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    games = db.execute(
        "SELECT g.name, c.times_played"
        " FROM collection c LEFT OUTER JOIN games g ON c.game_id = g.id"
        " WHERE c.user_id = ?", (session['user_id'],)
    ).fetchall()
    return render_template('collection/index.html', games=games)


@bp.route('/addgame', methods=('GET', 'POST'))
@login_required
def addgame():
    if request.method == 'POST':
        name = request.form['name']
        minplay = request.form['minplay']
        maxplay = request.form['maxplay']
        error = None

        if not name:
            error = 'Name is required.'
        elif not minplay:
            error = 'Minimum Players is required.'
        elif not maxplay:
            error = 'Maximum Players is required.'

        if error is None:
            db = get_db()
            game_id = db.execute("Select id from games where name = ?", (name,)).fetchone()
            if not game_id:
                db.execute('INSERT INTO games (name, minplay, maxplay) VALUES (?, ?, ?)', (name, minplay, maxplay))
                game_id = db.execute('SELECT id from games where name = ?', (name,)).fetchone()
                db.execute('INSERT INTO collection (user_id, game_id) VALUES (?, ?)', (session['user_id'], game_id[0]))
                db.commit()
                return redirect(url_for('index'))
            else:
                game_id = db.execute('SELECT id from games where name = ?', (name,)).fetchone()
                db.execute('INSERT INTO collection (user_id, game_id) VALUES (?, ?)', (session['user_id'], game_id[0]))
                db.commit()
                return redirect(url_for('index'))

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
            options = db.execute(
                "Select Name from games where ? between minplay and maxplay", (numplayers,)
            ).fetchall()
            if not options:
                error = 'No games support that number of players. Try again'
                flash(error)
                return render_template('collection/pickgame.html')
            options_list = []
            for game in options:
                options_list.append(game[0])
            # choice_num = random.randint(0, len(options_list) - 1)
            return render_template('collection/gameresult.html',
                                   game=options_list[random.randint(0, len(options_list) - 1)])

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
            playerlist = playertext.split()
            for player in playerlist:
                player_id = db.execute('SELECT id from players WHERE user_id = ? and upper(name) = upper(?)',
                                       (session['user_id'], player)).fetchone()
                if not player_id:
                    db.execute('INSERT INTO players (user_id, name) VALUES (?, ?)',
                               (session['user_id'], player))
                    db.commit()
                else:
                    db.execute('UPDATE players SET games_played = games_played + 1'
                               ' WHERE id = ?', (player_id))
                    db.commit()
            first_player_num = random.randint(0, len(playerlist) - 1)
            return render_template('collection/firstplayer.html', name=playerlist[first_player_num])
        flash(error)

    return render_template('collection/pickplayer.html')
