from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from bghweb.auth import login_required
from bghweb.db import get_db

bp = Blueprint('collection', __name__, url_prefix='/collection')


@bp.route('/addgame')
def addgame():
    if request.method == 'POST':
        name = request.form['name']
        minplay = request.form['minplay']
        maxplay = request.form['maxplay']
        favorite = request.form['favorite']
        error = None

        if not name:
            error = 'Name is required.'
        elif not minplay:
            error = 'Minimum Players is required.'
        if not maxplay:
            error = 'Maximum Players is required.'

        if error is not None:
            flash(error)
        else:
            # to be continued
