-- NetLink Telco customer portal seed.

CREATE TABLE users (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    role     VARCHAR(32) NOT NULL DEFAULT 'customer',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE customers (
    id       SERIAL PRIMARY KEY,
    user_id  INT REFERENCES users(id) ON DELETE CASCADE,
    name     VARCHAR(128) NOT NULL,
    email    VARCHAR(128) NOT NULL UNIQUE,
    plan     VARCHAR(64) NOT NULL,
    address  VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE invoices (
    id           SERIAL PRIMARY KEY,
    customer_id  INT REFERENCES customers(id) ON DELETE CASCADE,
    period       VARCHAR(16) NOT NULL,
    amount_eur   NUMERIC(8,2) NOT NULL,
    status       VARCHAR(16) NOT NULL DEFAULT 'unpaid',
    notes        TEXT
);

INSERT INTO users (username, password, role) VALUES
    ('admin',       'Admin123',       'admin'),
    ('grid_ops',    'gridops!',       'staff'),
    ('alice',       'alice2024',      'customer'),
    ('bob',         'bobcustomer',    'customer'),
    ('carol',       'carolcorp',      'customer'),
    ('dean',        'dean-net',       'customer');

INSERT INTO customers (user_id, name, email, plan, address) VALUES
    (3, 'Alice Constantinou',       'alice@example.cy',         'Fibre 1 Gbps',         'Larnaca, CY'),
    (4, 'Bob Charalambous',         'bob@example.cy',           'Fibre 500 Mbps',       'Limassol, CY'),
    (5, 'Carol Corp Trading Ltd',   'billing@carolcorp.cy',     'Business 10 Gbps',     'Nicosia, CY'),
    (6, 'Dean Hadjichristofi',      'dean@example.cy',          'Fibre 200 Mbps',       'Paphos, CY');

INSERT INTO invoices (customer_id, period, amount_eur, status, notes) VALUES
    (1, '2026-03', 39.90,  'paid',    'Routine residential invoice.'),
    (1, '2026-04', 39.90,  'unpaid',  'Routine residential invoice.'),
    (2, '2026-03', 29.90,  'paid',    'Routine residential invoice.'),
    (2, '2026-04', 29.90,  'paid',    'Routine residential invoice.'),
    (3, '2026-03', 1290.00,'paid',    'CONFIDENTIAL: linked to fibre lease, see contract NLT-2025-014.'),
    (3, '2026-04', 1290.00,'overdue', 'CONFIDENTIAL: late-payment escalation pending; legal notified.'),
    (4, '2026-03', 24.90,  'paid',    'Routine residential invoice.'),
    (4, '2026-04', 24.90,  'unpaid',  'Routine residential invoice.');
