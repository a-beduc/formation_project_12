CREATE SCHEMA auth;
CREATE SCHEMA crm;

CREATE TABLE auth.users (
    user_id SERIAL NOT NULL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    superuser BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE crm.role (
    role_id SERIAL NOT NULL PRIMARY KEY,
    role VARCHAR(20)
);

CREATE TABLE crm.collaborator (
    collaborator_id SERIAL NOT NULL PRIMARY KEY,
    last_name VARCHAR(255),
    first_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20),
    activated BOOLEAN NOT NULL DEFAULT FALSE,
    role INT REFERENCES crm.role(role_id),
    linked_user INT NOT NULL UNIQUE REFERENCES auth.users(user_id) ON DELETE CASCADE
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
    salesman INT NOT NULL REFERENCES crm.collaborator(collaborator_id) ON DELETE CASCADE
);

CREATE TABLE crm.contract (
    contract_id SERIAL NOT NULL PRIMARY KEY,
    total_amount DECIMAL(10, 2),
    paid_amount DECIMAL(10, 2),
    created_at TIMESTAMP,
    signed BOOLEAN NOT NULL DEFAULT FALSE,
    client INT NOT NULL REFERENCES crm.client(client_id) ON DELETE CASCADE
);

CREATE TABLE crm.event (
    event_id SERIAL NOT NULL PRIMARY KEY,
    title VARCHAR(255),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    location VARCHAR(255),
    attendee INT,
    notes TEXT,
    supporter INT REFERENCES crm.collaborator(collaborator_id) ON DELETE CASCADE,
    contract INT NOT NULL REFERENCES crm.contract(contract_id) ON DELETE CASCADE
);
