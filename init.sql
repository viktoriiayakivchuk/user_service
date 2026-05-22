CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);

INSERT INTO roles (name, description)
VALUES 
    ('Student', 'Default role for enrolled platform consumers'),
    ('Instructor', 'Role for content creators and managers'),
    ('Admin', 'Platform administrator with account management authorities')
ON CONFLICT (name) DO NOTHING;