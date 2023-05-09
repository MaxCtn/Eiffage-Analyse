import os
from flask import Flask, render_template, request, send_file, jsonify

def init_extensions(app):
    app.config.update(
        UPLOADED_PATH=os.path.join(app.root_path, "uploads"),
        DROPZONE_ALLOWED_FILE_TYPE=".xlsx",
        DROPZONE_MAX_FILE_SIZE=5,
        DROPZONE_MAX_FILES=2,
        DROPZONE_IN_FORM=True,
        DROPZONE_UPLOAD_ON_CLICK=True,
    )

    return app

# ...

def create_app():
    app = Flask(__name__)

    # Configuration et initialisation des extensions
    app = init_extensions(app)

    # ...
    
    app.config.update(
        UPLOADED_PATH=os.path.join(app.root_path, "uploads"),
        DROPZONE_ALLOWED_FILE_TYPE=".xlsx",
        DROPZONE_MAX_FILE_SIZE=5,
        DROPZONE_MAX_FILES=2,
        DROPZONE_IN_FORM=True,
        DROPZONE_UPLOAD_ON_CLICK=True,
    )
    
    # ...
    
    return app
