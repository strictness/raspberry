import datetime
import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename

from raspberry import (
    db,
    auth,
    file,
)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'raspberry.sqlite')
    )
    app.config['UPLOAD_FOLDER'] = 'media'

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass

    # @app.route('/upload', methods=['GET', 'POST'])
    # def upload_file():
    #     if request.method == 'POST':
    #         # check if the post request has the file part
    #         if 'file' not in request.files:
    #             flash('No file part')
    #             return redirect(request.url)
    #         file = request.files['file']
    #         # if user does not select file, browser also
    #         # submit an empty part without filename
    #         if file.filename == '':
    #             flash('No selected file')
    #             return redirect(request.url)
    #         if file and allowed_file(file.filename):
    #             filename = secure_filename(file.filename)
    #             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #             return redirect(url_for('index'))
    #     return render_template('upload_file.html')

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(file.bp)
    app.add_url_rule('/', endpoint='index')

    return app
