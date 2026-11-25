-- starter data. run this after schema.sql (it's fine to run it more than once)

INSERT INTO exercises (exercise_name) VALUES
    ('Back Squat'),
    ('Bench Press'),
    ('Deadlift'),
    ('Overhead Press'),
    ('Barbell Row')
ON CONFLICT (exercise_name) DO NOTHING;
