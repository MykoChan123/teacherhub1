

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_socketio import emit, SocketIO, leave_room, join_room
from flask_migrate import Migrate
from flask_mail import Mail, Message



db = SQLAlchemy()
socketio = SocketIO()
migrate = Migrate()
mail = Mail()


def Server():
    app = Flask(__name__)
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:mykochan@localhost:5432/teacherhub'
    app.config['SECRET_KEY'] = 'myko chan'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'teachershubsalincub@gmail.com'  # Your Gmail address
    app.config['MAIL_PASSWORD'] = 'fyyd ghxl svlh nmou'     # App Password from Google
    app.config['MAIL_DEFAULT_SENDER'] = ('Teacher Hub', 'myko.chan@yahoo.com')  # Default sende



    db.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app,db)
    mail.init_app(app)

    from .download import downloaddata
    from .views import views
    from .auth import auth
    from .dashboard import dashboard
    from .admin import admin
    from .models import User, Website
    from flask import session
    

    app.register_blueprint(downloaddata)
    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(admin)
    @app.context_processor
    def testingmykochan():
        id = session['user_id'] if 'user_id' in session else None
        websitename = Website.query.first()
        user = User.query.get(id)
        return {'mykochangwapo' : websitename.name,
                'mykochangwapo_userpos': user.position if hasattr(user, 'position') else None}
 
    
    return app
