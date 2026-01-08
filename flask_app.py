from app import create_app
from app.models import db

app = create_app("ProductionConfig")
# Start virtual environment for Mac
# python3 -m venv .venv --copies
# source .venv/bin/activate
# npm install -g @apidevtools/swagger-cli nodemon
# pip install -r requirements.txt
# pip freeze > requirements.txt

# for the merged yaml files run npm run watch-swagger in virtual environment,
# this will save the changes to other .yaml files and then add them to the merged.yaml file

# run app.py in seperate terminal
#hell

with app.app_context():
    # db.drop_all()
    db.create_all()

# do not need this because gunicorn, app.run()


# gunicorn flask_app:app
