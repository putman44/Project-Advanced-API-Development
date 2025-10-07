from app import create_app
from app.models import db

app = create_app("DevelopmentConfig")
# Start virtual environment for Mac
# python3 -m venv .venv --copies
# source .venv/bin/activate
# pip install Flask Flask-SQLAlchemy Flask-Marshmallow mysql-connector-python marshmallow-sqlalchemy Flask-Limiter Flask-Caching python-jose alembic flask-swagger flask_swagger_ui @apidevtools/swagger-cli nodemon
# pip freeze > requirements.txt

# for the merged yaml files run npm run watch-swagger in virtual environment,
# this will save the changes to other .yaml files and then add them to the merged.yaml file

# run app.py in seperate terminal


with app.app_context():
    # db.drop_all()
    db.create_all()

app.run()
