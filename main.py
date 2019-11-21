from raspberry import config
from raspberry import app

if __name__ == "__main__":
    app.app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

    app.app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG_MODE)
