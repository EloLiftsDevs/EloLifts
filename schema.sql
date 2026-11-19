
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash TEXT,
    role TEXT DEFAULT 'user',
    rank TEXT DEFAULT 'Bronze',
    suspended BOOLEAN DEFAULT FALSE
);

CREATE TABLE exercises (
    exercise_id SERIAL PRIMARY KEY,
    exercise_name TEXT UNIQUE,
    measurement TEXT DEFAULT 'weight_reps'
);

CREATE TABLE lift_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    exercise_id INT REFERENCES exercises(exercise_id),
    weight_lb NUMERIC,
    reps INT,
    sets INT DEFAULT 1,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    review_status TEXT DEFAULT 'normal'
);

CREATE TABLE workouts (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    name TEXT,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP
);

CREATE TABLE workout_exercises (
    id SERIAL PRIMARY KEY,
    workout_id INT REFERENCES workouts(id),
    exercise_id INT REFERENCES exercises(exercise_id),
    sets INT,
    reps INT,
    weight INT
);

CREATE TABLE comparison_groups (
    user_id INT REFERENCES users(user_id),
    member_id INT REFERENCES users(user_id),
    PRIMARY KEY (user_id, member_id)
);
