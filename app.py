import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
import logging
from sqlalchemy import text
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["EXPLAIN_TEMPLATE_LOADING"] = True
app.config["DEBUG"] = True
app.config["WTF_CSRF_ENABLED"] = True
app.config["WTF_CSRF_SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)
app.jinja_env.auto_reload = True

# Initialize extensions
Session(app)
csrf.init_app(app)
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Initialize database and verify directories
with app.app_context():
    import models
    try:
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        logger.info("Upload directory checked/created")
        
        # Test database connection
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise
