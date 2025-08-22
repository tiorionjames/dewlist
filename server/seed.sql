-- server/seed.sql
DROP TABLE IF EXISTS task_history CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(32) UNIQUE NOT NULL,
    email VARCHAR(64) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    profile_pic TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    title VARCHAR(64) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'New',
    assigned_to INT REFERENCES users(user_id),
    created_by INT REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_history (
    history_id SERIAL PRIMARY KEY,
    task_id INT REFERENCES tasks(task_id),
    previous_status VARCHAR(20),
    new_status VARCHAR(20),
    changed_by INT REFERENCES users(user_id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note TEXT
);

-- seed users (passwords are placeholders; replace with bcrypt hashes)
INSERT INTO users (username, email, hashed_password, role, profile_pic, created_at)
VALUES
    ('gwashington', 'gwashington@dewlist.app', 'hashpassword', 'Admin', 'http://localhost:8000/static/profile_pics/george.jpg', '2025-06-01'),
    ('afranklin', 'afranklin@dewlist.app', 'hashpassword', 'Manager', 'http://localhost:8000/static/profile_pics/alissa.jpg','2025-06-01'),
    ('badams', 'badams@dewlist.app', 'hashpassword', 'Manager', 'http://localhost:8000/static/profile_pics/bill.jpg','2025-06-01'),
    ('tjefferson', 'tjefferson@dewlist.app', 'hashpassword', 'User', 'http://localhost:8000/static/profile_pics/tom.jpg','2025-06-01'),
    ('jmadison', 'jmadison@dewlist.app', 'hashpassword', 'User', 'http://localhost:8000/static/profile_pics/james.jpg','2025-06-01'),
    ('egarcia', 'egarcia@dewlist.app', 'hashpassword', 'User', 'http://localhost:8000/static/profile_pics/emma.jpg','2025-06-01');

-- trigger to keep updated_at current on updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trg_update_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
