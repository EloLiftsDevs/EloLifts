import os

from flask import Flask, redirect, url_for

#josiah
from dotenv import load_dotenv
load_dotenv()
#josiah

from frontend import bp as frontend_bp, csrf, login_manager
from models import db

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not set. Add it to your .env file "
        "(see README.md for the format)."
    )

# used to sign the login cookie. if someone gets this they can fake logins, so keep it in .env and never commit it
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "SECRET_KEY is not set. Add it to your .env file "
        "(see README.md for how to generate one)."
    )

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = secret_key
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# keep csrf tokens good for the whole session (default is they expire after an hour)
app.config["WTF_CSRF_TIME_LIMIT"] = None

db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
app.register_blueprint(frontend_bp)


@app.route("/")
def home():
    return redirect(url_for("frontend.dashboard"))


if __name__ == "__main__":
    app.run(debug=True)