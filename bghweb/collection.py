from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from bghweb.auth import login_required
from bghweb.db import get_db

bp = Blueprint('collection', __name__)


@bp.route('/')
def index():
    db = get_db()
    games = db.execute(
        "SELECT g.name, c.times_played"
        " FROM collection c LEFT OUTER JOIN games g ON c.game_id = g.id"
        " WHERE c.user_id = ?", (session['user_id'],)
    ).fetchall()
    return render_template('collection/index.html', games=games)


@bp.route('/addgame')
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
        if not maxplay:
            error = 'Maximum Players is required.'

        if error is None:
            db = get_db()
            gameexists = db.execute("Select id from game where name like '%?%'", name)
            if not gameexists:
                db.execute('INSERT INTO game (name, minplay, maxplay) VALUES (?, ?, ?)', (name, minplay, maxplay))
                game_id = db.execute('SELECT id from game where name = ?', name)
                db.execute('INSERT INTO collection (user_id, game_id) VALUES (?, ?)', (session['user_id'], game_id))
                db.commit()
            else:
                game_id = db.execute('SELECT id from game where name = ?', name)
                db.execute('INSERT INTO collection (user_id, game_id) VALUES (?, ?)', (session['user_id'], game_id))
                db.commit()

        flash(error)

        return redirect(url_for('index'))

    return render_template('collection/addgame.html')

