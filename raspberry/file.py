import os
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from raspberry.auth import login_required
from raspberry.db import get_db

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

bp = Blueprint('file', __name__)


def _allowed_file(filename):
    return any(filename.endswith(f'.{ext}') for ext in ALLOWED_EXTENSIONS)


def _get_file(id, check_author=True):
    file = get_db().execute(
        '''
        SELECT f.id, title, description, path, created, author_id, username
        FROM file f
          JOIN user u
            ON f.author_id = u.id
        WHERE f.id = :id 
        ''',
        {
            'id': id,
        }
    ).fetchone()

    if file is None:
        abort(404, f"File id {id} doesn't exist.")

    if check_author and file['author_id'] != g.user['id']:
        abort(403)

    return file


@bp.route('/')
def index():
    db = get_db()
    files = db.execute(
        '''
        SELECT *
        FROM file f
          JOIN user u
            ON f.author_id = u.id
        ORDER BY created DESC
        '''
    ).fetchall()

    return render_template('file/index.html', files=files)


@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'
        elif not description:
            error = 'Description is required.'
        elif not request.files or 'file' not in request.files:
            error = 'File is required'

        file = request.files['file']
        if not _allowed_file(file.filename):
            error = 'Invalid file format'

        filename = secure_filename(file.filename)
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                '''
                INSERT INTO file (title, description, path, author_id)
                VALUES (:title, :description, :path, :author_id)
                ''',
                {
                    'title': title,
                    'description': description,
                    'path': path,
                    'author_id': g.user['id']
                }
            )
            try:
                file.save(path)
            except OSError:
                error = 'Unable to save file.'

            if not error:
                db.commit()
                return redirect(url_for('file.index'))
            else:
                flash(error)

    return render_template('file/upload.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    file = _get_file(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'
        if not description:
            error = 'Description is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                '''
                UPDATE file SET title = :title, description = :description
                WHERE id = :id
                ''',
                {
                    'title': title,
                    'description': description,
                    'id': id,
                }
            )
            db.commit()
            return redirect(url_for('file.index'))

    return render_template('file/update.html', file=file)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    error = None
    file = _get_file(id)
    db = get_db()
    db.execute(
        '''
        DELETE FROM file WHERE id = :id
        ''',
        {
            'id': id,
        }
    )
    try:
        os.remove(file['path'])
    except OSError:
        error = 'Unable to remove file.'

    if not error:
        db.commit()
        return redirect(url_for('file.index'))
    else:
        flash(error)

    return render_template('file/update.html', file=file)
