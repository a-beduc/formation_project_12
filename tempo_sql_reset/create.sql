CREATE SCHEMA auth;
CREATE SCHEMA crm;

CREATE TABLE auth.users (
    user_id SERIAL NOT NULL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE crm.role (
    role_id SERIAL NOT NULL PRIMARY KEY,
    role VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE crm.collaborator (
    collaborator_id SERIAL NOT NULL PRIMARY KEY,
    last_name VARCHAR(255),
    first_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20),
    role_id INT DEFAULT 0 REFERENCES crm.role(role_id),
    user_id INT NOT NULL UNIQUE REFERENCES auth.users(user_id)
);


CREATE TABLE crm.client (
    client_id SERIAL NOT NULL PRIMARY KEY,
    last_name VARCHAR(255),
    first_name VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(20),
    company VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    salesman_id INT NOT NULL REFERENCES crm.collaborator(collaborator_id)
);

CREATE TABLE crm.contract (
    contract_id SERIAL NOT NULL PRIMARY KEY,
    total_amount DECIMAL(10, 2),
    paid_amount DECIMAL(10, 2),
    created_at TIMESTAMP,
    signed BOOLEAN NOT NULL DEFAULT FALSE,
    client_id INT NOT NULL REFERENCES crm.client(client_id)
);

CREATE TABLE crm.event (
    event_id SERIAL NOT NULL PRIMARY KEY,
    title VARCHAR(255),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    location VARCHAR(255),
    attendee INT,
    notes TEXT,
    supporter_id INT REFERENCES crm.collaborator(collaborator_id),
    contract_id INT NOT NULL REFERENCES crm.contract(contract_id)
);
