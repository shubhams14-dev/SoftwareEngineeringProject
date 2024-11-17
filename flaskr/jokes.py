from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('jokes', __name__)


@bp.route('/')
def hello():
    return render_template('base.html')

@bp.route('/my_jokes')
def my_jokes():
    db = get_db()
    jokes = db.execute(
        'SELECT j.id, title, rating, times_rated, created, author_id, nickname'
        ' FROM joke j JOIN user u ON j.author_id = u.id'
        ' WHERE u.id = ?'
        ' ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()
    return render_template('jokes/my_jokes.html', jokes=jokes, route='my_jokes')


@bp.route('/leave_a_joke', methods=('GET', 'POST'))
@login_required
def leave_a_joke():
    if request.method == 'POST':
        title = request.form['title'].strip()
        body = request.form['body'].strip()
        error = None

        db = get_db()

        if not title:
            error = 'Title is required.'

        elif len(title.split()) > 10:
            error = 'Title must be less than 10 words.'

        elif db.execute('SELECT id FROM joke WHERE title = ? AND author_id = ?',
                        (title, g.user['id'])).fetchone() is not None:
            error = 'This title has already been used.'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO joke (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.execute(
                'UPDATE user SET joke_balance = joke_balance + 1 WHERE id = ?', (
                    g.user['id'],)
            )
            db.commit()
            return redirect(url_for('jokes.my_jokes'))

    return render_template('jokes/leave_a_joke.html', route='leave_a_joke')


def get_joke(id, check_author=True):
    joke = get_db().execute(
        'SELECT p.id, title, body, created, author_id, nickname'
        ' FROM joke p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if joke is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and joke['author_id'] != g.user['id']:
        abort(403)

    return joke


@bp.route('/<int:id>/update_joke', methods=('GET', 'POST'))
@login_required
def update_joke(id):
    joke = get_joke(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE joke SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('jokes.my_jokes'))

    return render_template('jokes/update_joke.html', joke=joke, route='update_joke')


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_joke(id)
    db = get_db()
    db.execute('DELETE FROM joke WHERE id = ?', (id,))
    db.execute(
        'UPDATE user SET joke_balance = joke_balance - 1 WHERE id = ?', (g.user['id'],))
    db.commit()
    return redirect(url_for('jokes.my_jokes'))

@bp.route('/take_a_joke')
@login_required
def take_a_joke():
    db = get_db()
    jokes = db.execute(
        'SELECT p.id, title, body, created, author_id, nickname'
        ' FROM joke p JOIN user u ON p.author_id = u.id'
        ' WHERE u.id != ?'
        ' ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()
    return render_template('jokes/take_a_joke.html', jokes=jokes, route='take_a_joke')
