-- PortPilot seed data
-- NOTE: passwords are stored in plaintext on purpose for the training scenario.

CREATE TABLE users (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    role     VARCHAR(32) NOT NULL DEFAULT 'operator',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE vessels (
    id     SERIAL PRIMARY KEY,
    imo    VARCHAR(16) UNIQUE NOT NULL,
    name   VARCHAR(128) NOT NULL,
    flag   VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL,
    eta    TIMESTAMP
);

CREATE TABLE manifests (
    id            SERIAL PRIMARY KEY,
    vessel_id     INT REFERENCES vessels(id) ON DELETE CASCADE,
    cargo_type    VARCHAR(64) NOT NULL,
    weight_tonnes NUMERIC(10,2) NOT NULL,
    consignee     VARCHAR(128) NOT NULL,
    notes         TEXT,
    owner_user_id INT REFERENCES users(id) ON DELETE SET NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO users (username, password, role) VALUES
    ('admin',    'Admin123',          'admin'),
    ('aoswald',  'columbia2024',      'operator'),
    ('mioannou', 'bolton!secure',     'operator'),
    ('viewer',   'viewer',            'viewer');

INSERT INTO vessels (imo, name, flag, status, eta) VALUES
    ('IMO9876543', 'MV Aegean Star',    'Cyprus',  'Inbound',  NOW() + INTERVAL '6 hours'),
    ('IMO9123456', 'MV Larnaca Dawn',   'Greece',  'Berthed',  NOW() - INTERVAL '2 hours'),
    ('IMO9555111', 'MV Helios Wave',    'Malta',   'Inbound',  NOW() + INTERVAL '18 hours'),
    ('IMO9777222', 'MV Black Sea Lily', 'Romania', 'Inbound',  NOW() + INTERVAL '1 day'),
    ('IMO9333888', 'MV Limassol Pride', 'Cyprus',  'Departed', NOW() - INTERVAL '1 day'),
    ('IMO9444555', 'MV Polaris',        'Panama',  'Inbound',  NOW() + INTERVAL '3 days'),
    ('IMO9666777', 'MV Adriatic Sun',   'Italy',   'Berthed',  NOW() - INTERVAL '8 hours'),
    ('IMO9888999', 'MV Carpathian',     'Romania', 'Inbound',  NOW() + INTERVAL '2 days');

INSERT INTO manifests (vessel_id, cargo_type, weight_tonnes, consignee, notes, owner_user_id) VALUES
    (1, 'Containers (20ft)',      4200.50, 'Cyprus Importers Ltd',     'Standard cargo, no notes.',                                   2),
    (2, 'Refrigerated produce',    980.00, 'Mediterranean Foods SA',   'Temperature must remain below 4°C during discharge.',         2),
    (3, 'Bulk grain',            12500.00, 'Helios Agri-Cooperative',  'Customs pre-clearance attached.',                             3),
    (4, 'Liquid bulk (diesel)',   8800.00, 'EximProd Engineering S.A.','CLASSIFIED: strategic fuel reserve for partner network.',     1),
    (5, 'Containers (40ft)',      3650.25, 'Limassol Logistics Hub',   'Routine outbound shipment.',                                  3),
    (6, 'Project cargo (turbine)', 420.00, 'EU Energy Partners',       'CONFIDENTIAL: offshore wind installation components.',        1),
    (7, 'Containers (mixed)',     5400.75, 'Adriatic Trade House',     'Customer requests after-hours discharge.',                    2),
    (8, 'Vehicles (ro-ro)',       1850.00, 'Romanian Auto Imports',    'Standard cargo, no notes.',                                   3);
