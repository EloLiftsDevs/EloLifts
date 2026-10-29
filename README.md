# EloLifts
EloLifts is a web-app that allows users to track lifts, giving them a competitive rank to compare with their peers.

# To Get Started:
1. Install PostgreSQL and create a database named `elolifts`.
2. Run `schema.sql`, then `seed.sql`, against that database (for example in pgAdmin's Query Tool).
3. Add a test user, since login and registration aren't connected yet:
```sql
INSERT INTO users (username, email) VALUES ('test', 'test@example.com');
```
4. Create a `.env` file in the project folder with your connection URL, for example
`DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/elolifts`.
The app will not start without it. `.env` is gitignored, so never commit it.
5. Download requirements: `pip install -r requirements.txt`
6. Run `python app.py` and open the link shown in the console.

# Project layout
| File | What it does | When it runs |
|---|---|---|
| `schema.sql` | Creates the empty tables. The app does not create them. | Once per database, by hand |
| `seed.sql` | Adds starter rows (exercises). Safe to run more than once. | Once per database, right after `schema.sql` |
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
- Login and registration are not connected yet, so every page acts as the user
  with `user_id` 1 (`CURRENT_USER_ID` in `frontend/__init__.py`).
- Ranks and the leaderboard are still placeholder data. Ranking should be layered on
  after the team agrees on a comparable scoring rule (including weight units and how
  exercise/reps factor in).