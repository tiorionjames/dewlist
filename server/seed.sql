DROP TABLE IF EXISTS role_permissions CASCADE;
DROP TABLE IF EXISTS permissions CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS task_history CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(32) NOT NULL,
    last_name VARCHAR(32) NOT NULL,
    username VARCHAR(16) NOT NULL,
    email VARCHAR(64) NOT NULL,
    password_hash TEXT NOT NULL,
    user_role_id INT REFERENCES roles(id),
    profile_pic TEXT,
    create_date TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(32) NOT NULL,
    description_task TEXT,
    task_status VARCHAR(20),
    assigned_to INT REFERENCES users(id),
    created_by INT REFERENCES users(id),
    create_date TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_history (
    history_id SERIAL PRIMARY KEY,
    task_id INT REFERENCES tasks(id),
    title VARCHAR(32) NOT NULL,
    description_task TEXT,
    task_status VARCHAR(20),
    assigned_to INT REFERENCES users(id),
    created_by INT REFERENCES users(id),
    create_date TIMESTAMP(6),
    update_at TIMESTAMP(6),
    snapshot_at TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    changed_by INT REFERENCES users(id),
    action VARCHAR(20) NOT NULL
);

CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    permission_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE role_permissions (
    role_id INT REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INT REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- Insert roles
INSERT INTO roles (role_name) VALUES ('Admin'), ('Manager'), ('User');

-- Insert permissions
INSERT INTO permissions (permission_name) VALUES
    ('create_task'),
    ('edit_task'),
    ('assign_task'),
    ('approve_task'),
    ('reassign_task'),
    ('close_task'),
    ('delete_task'),
    ('add_notes'),
    ('start_task'),
    ('stop_task'),
    ('pause_task'),
    ('resume_task'),
    ('complete_task');

-- Insert users (linking to role IDs)
INSERT INTO users (first_name, last_name, username, email, password_hash, user_role_id, profile_pic, create_date)
VALUES
    ('George', 'Washington', 'gwashington', 'gwashington@dewlist.app', 'hashpassword', 1, 'http://localhost:8000/static/profile_pics/george.jpg', '2025-06-01'),
    ('Alissa', 'Franklin', 'afranklin', 'afranklin@dewlist.app', 'hashpassword', 2, 'http://localhost:8000/static/profile_pics/alissa.jpg', '2025-06-01'),
    ('Bill', 'Adams', 'badams', 'badams@dewlist.app', 'hashpassword', 2, 'http://localhost:8000/static/profile_pics/bill.jpg', '2025-06-01'),
    ('Tom', 'Jefferson', 'tjefferson', 'tjefferson@dewlist.app', 'hashpassword', 3, 'http://localhost:8000/static/profile_pics/tom.jpg', '2025-06-01'),
    ('James', 'Madison', 'jmadison', 'jmadison@dewlist.app', 'hashpassword', 3, 'http://localhost:8000/static/profile_pics/james.jpg', '2025-06-01'),
    ('Emma', 'Garcia', 'egarcia', 'egarcia@dewlist.app', 'hashpassword', 3, 'http://localhost:8000/static/profile_pics/emma.jpg', '2025-06-01');

-- Trigger for task history
CREATE OR REPLACE FUNCTION log_task_history()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO task_history (task_id, title, description_task, task_status,
                                  assigned_to, created_by, create_date, update_at,
                                  changed_by, action)
        VALUES (NEW.id, NEW.title, NEW.description_task, NEW.task_status,
                NEW.assigned_to, NEW.created_by, NEW.create_date, NEW.update_at,
                NEW.created_by, 'INSERT');
        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO task_history (task_id, title, description_task, task_status,
                                  assigned_to, created_by, create_date, update_at,
                                  changed_by, action)
        VALUES (NEW.id, NEW.title, NEW.description_task, NEW.task_status,
                NEW.assigned_to, NEW.created_by, NEW.create_date, NEW.update_at,
                NEW.assigned_by, 'UPDATE');
        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO task_history (task_id, title, description_task, task_status,
                                  assigned_to, created_by, create_date, update_at,
                                  changed_by, action)
        VALUES (OLD.id, OLD.title, OLD.description_task, OLD.task_status,
                OLD.assigned_to, OLD.created_by, OLD.create_date, OLD.update_at,
                OLD.created_by, 'DELETE');
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_task_history
AFTER INSERT OR UPDATE OR DELETE ON tasks
FOR EACH ROW
EXECUTE FUNCTION log_task_history();
