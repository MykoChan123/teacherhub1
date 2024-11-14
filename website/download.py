from flask import Blueprint,send_file, current_app, send_from_directory, session
import logging
import os
from .models import Files
from website import db
from .models import User, Useractivity



downloaddata = Blueprint('downloaddata', __name__)


@downloaddata.route('/download/<int:id>')
def download(id):
    try:
        file = Files.query.get(id)
        user = User.query.get(session['user_id'])
        action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Downloaded a file named: ' + str(file.file_name)
        addtolog = Useractivity(action=action)
        db.session.add(addtolog)
        db.session.commit()

        relative_path = os.path.dirname(file.file_path)
        current_app.logger.debug(relative_path)

        directory = os.path.join(current_app.root_path, relative_path)
        current_app.logger.debug(directory)

        filename = os.path.basename(file.file_path)
        current_app.logger.debug(filename)

        path = os.path.join(directory,filename)
        current_app.logger.debug(path)

        return send_file(path, as_attachment=True)
    except: pass
