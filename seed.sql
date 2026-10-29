-- Starter data. Run after schema.sql; safe to run more than once.

INSERT INTO exercises (exercise_name) VALUES
    ('Back Squat'),
    ('Bench Press'),
    ('Deadlift'),
    ('Overhead Press'),
    ('Barbell Row')
ON CONFLICT (exercise_name) DO NOTHING;
