# EloLifts
EloLifts is a web-app that allows users to track lifts, giving them a competitive rank to compare with their peers.

# To Get Started:
1. Install PostgreSQL (keep pgAdmin 4 selected in the installer). Write down the password
you choose for the `postgres` user, because you'll need it in step 4.
2. Open pgAdmin 4, expand **Servers → PostgreSQL**, right-click **Databases → Create → Database...**,
and name it `elolifts`.
3. Run `schema.sql`, then `seed.sql`, against that database with pgAdmin: right-click `elolifts` → **Query Tool**, open the file with the
folder icon, and press **F5**. Don't skip `seed.sql`, because the Log Lift page has no
exercises to choose from without it.
4. Create a `.env` file in the project folder with your connection URL, for example
`DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/elolifts`,
and a `SECRET_KEY=` line set to the output of
`python -c "import secrets; print(secrets.token_hex(32))"`.
The app will not start without both. `.env` is gitignored, so never commit it.
5. Download requirements: `pip install -r requirements.txt`
6. Run `python app.py`, open the link shown in the console, and click **Create an account**.
Users added by hand in SQL (like the old `test` user) have no password and can't log in.
7. To see saved data, go to **elolifts → Schemas → public → Tables** in pgAdmin, right-click
a table (e.g. `lift_logs`), and choose **View/Edit Data → All Rows**. Click the grid's
refresh button after logging new lifts.

# Project layout
| File | What it does | When it runs |
|---|---|---|
| `schema.sql` | Creates the empty tables. The app does not create them. | Once per database, by hand |
| `seed.sql` | Adds starter rows (exercises). Safe to run more than once. | Once per database, right after `schema.sql` |
| `ranking.py` | Rank rules: the Epley estimate and the Big 3 thresholds for each rank | Whenever ranks are shown or updated |
| `models.py` | Describes the tables so Python (SQLAlchemy) can read and write them | Every time the app runs |
| `app.py` | Starts the Flask server and connects it to the database | Every time you run `python app.py` |
| `frontend/` | The pages: Flask routes in `__init__.py`, HTML in `templates/` | While `app.py` is running |

`schema.sql` and `models.py` must describe the same tables. If you change a table in
one, change it in the other.

The website only works while `python app.py` is running (stop it with Ctrl+C).
The data is stored in PostgreSQL, which runs separately in the background, so
nothing is lost when the app stops.

# Current status
- The dashboard, profile and "Log a lift" pages use real data from the database.
  Lifts are saved to `lift_logs`, with weights in pounds.
- Sign up, log in and log out work. Accounts are identified by email, which is unique
  and case-insensitive. Passwords are stored hashed. Every page except log in and sign up
  requires being logged in, and lifts are saved to the logged-in user.
- Rank comes from the **Big 3 total**: the best estimated one-rep max (Epley formula,
  reps capped at 10) in Back Squat, Bench Press and Deadlift added together. Bronze under
  500 lb, Silver 500, Gold 750, Platinum 1,000, Diamond 1,250, Elite 1,500+. Other
  exercises can be logged but don't affect rank. The rules and thresholds are in `ranking.py`.