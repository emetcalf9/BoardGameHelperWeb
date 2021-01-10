import os
import psycopg2

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    DATABASE_URL = os.environ['DATABASE_URL']
    #DATABASE_URL = "dbname=bgh user=eric password=test" # For Local Testing
    if 'db' not in g:
        g.db = psycopg2.connect(DATABASE_URL, sslmode='require')
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    dbcur = db.cursor()

    with current_app.open_resource('schema.sql') as f:
        dbcur.execute(f.read().decode('utf8'))
    dbcur.close()
    db.commit()
    db.close()



@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)