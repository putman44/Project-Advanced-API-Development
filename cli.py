import click
from app import create_app
from app.models import db

app = create_app("DevelopmentConfig")


@app.cli.command("reset-db")
def reset_db():
    """Drops and recreates all tables."""
    click.confirm("This will erase the database, continue?", abort=True)
    db.drop_all()
    db.create_all()
    click.echo("Database has been reset ✅")


# to use the command:
# make sure its active source venv/bin/activate
# export FLASK_APP=cli.py
# flask reset-db
