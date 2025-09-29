from app import create_app
from app.models import db

app = create_app("DevelopmentConfig")
# Start virtual environment for Mac
# python3 -m venv venv
# source .venv/bin/activate
# pip install Flask Flask-SQLAlchemy Flask-Marshmallow mysql-connector-python marshmallow-sqlalchemy Flask-Limiter Flask-Caching alembic
# pip freeze > requirements.txt


with app.app_context():
    db.create_all()

app.run()
