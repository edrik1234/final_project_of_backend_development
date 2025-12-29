-- Requests table
CREATE TABLE IF NOT EXISTS requests_status (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL CHECK (status IN ('in_progress', 'done', 'fail')),
    result TEXT
);


-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(2500) NOT NULL UNIQUE,
    email VARCHAR(2500) NOT NULL UNIQUE,
    password VARCHAR(2500) NOT NULL
);


-- telegram_users 
CREATE TABLE IF NOT EXISTS telegram_users (
    telegram_id BIGINT PRIMARY KEY,
    username TEXT,
    state VARCHAR(50) NOT NULL,
    request_id INTEGER,
    questions TEXT,
    answers TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE IF NOT EXISTS game_sessions (
    id SERIAL PRIMARY KEY ,
    telegram_id BIGINT NOT NULL,
    questions TEXT,
    answers TEXT,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_game_sessions_user
        FOREIGN KEY (telegram_id)
        REFERENCES telegram_users (telegram_id)
        ON DELETE CASCADE
);

