# EloLifts
EloLifts is a web-app that allows users to track lifts, giving them a competitive rank to compare with their peers.

# To Get Started:
1. Download Requirements
2. Run app.py to update server, link will be provided in console

## Lift logging API

The backend provides `POST /api/users/<user_id>/lifts` to record a set and
`GET /api/users/<user_id>/lifts` to retrieve that user's most recent 100 sets.
The POST body is JSON:
Example:
```json
{
  "exercise": "squat",
  "weight": 100,
  "reps": 5
}
```
# To test the logging API:
1. Open PowerShell in the project folder and start the server:
2. Submit a lift (example): 
```
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:5000/api/users/1/lifts `
  -ContentType "application/json" `
  -Body '{"exercise":"squat","weight":100,"reps":5}'
```


----

Set `DATABASE_URL` to a PostgreSQL SQLAlchemy connection URL before starting
the app, for example
`postgresql://user:password@localhost:5432/elolifts`. When `DATABASE_URL` is
not set, the app uses a local SQLite database for development. On startup,
`app.py` creates the `lift_logs` table if it does not exist; it expects the
user IDs in requests to refer to users managed by the rest of the application.

This is a first logging slice: it does not authenticate the caller or verify
that a user exists. Add authentication and user validation before exposing it
publicly. Ranking should be layered on after the team agrees on a comparable
scoring rule (including weight units and how exercise/reps factor in).


