CREATE TABLE users (
    user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash TEXT,
    role VARCHAR(20) DEFAULT 'user',
    rank VARCHAR(20) DEFAULT 'Bronze'
);

CREATE TABLE exercises (
    exercise_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    exercise_name VARCHAR(100) UNIQUE
);

CREATE TABLE lift_logs (
    log_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    exercise_id INTEGER REFERENCES exercises(exercise_id),
    weight_lb NUMERIC,
    reps INTEGER,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workouts (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    name VARCHAR(100),
    completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE workout_exercises (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    workout_id INTEGER REFERENCES workouts(id),
    exercise_id INTEGER REFERENCES exercises(exercise_id),
    sets INTEGER,
    reps INTEGER,
    weight INTEGER
);