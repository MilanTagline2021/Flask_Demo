from flask import *
import flask
from flask_app.auth import login_required
from flask_app.db import get_db
from werkzeug.exceptions import abort

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id,title,body,craeted,auhtor_id,username FROM post p JOIN user u ON p.auhtor_id = u.id ORDER BY craeted DESC').fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        if not title:
            error = 'Title reqiured!..'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO post (title,body,auhtor_id) VALUES (?,?,?)',
                       (title, body, g.user['id']))
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, craeted, auhtor_id, username'
        ' FROM post p JOIN user u ON p.auhtor_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post Id {id} does not exixst")

    if check_author and post['auhtor_id'] != g.user['id']:
        abort(403)
    return post


@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = get_post(id)

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
                'UPDATE post SET title = ?, body = ? WHERE id = ?', (title, body, id))
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?",(id,))
    db.commit()
    return redirect(url_for('blog.index'))
