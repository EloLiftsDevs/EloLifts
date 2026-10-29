import os

from flask import Flask, redirect, url_for

#josiah
from dotenv import load_dotenv
load_dotenv()
#josiah

from frontend import bp as frontend_bp
from models import db

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not set. Add it to your .env file "
        "(see README.md for the format)."
    )

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(frontend_bp)


@app.route("/")
def home():
    return redirect(url_for("frontend.dashboard"))


if __name__ == "__main__":
    app.run(debug=True)