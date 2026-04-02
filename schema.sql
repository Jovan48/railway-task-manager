CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    done BOOLEAN DEFAULT FALSE
);

INSERT INTO tasks (title, done) VALUES ('Buy groceries', false);
INSERT INTO tasks (title, done) VALUES ('Finish PaaS assignment', false);
INSERT INTO tasks (title, done) VALUES ('Read Flask docs', true);
```

Create `.gitignore`:
```
venv/
__pycache__/
*.pyc
.env