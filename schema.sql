CREATE TABLE guinea_pig (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    gender TEXT,
    birth_date TEXT
);

CREATE TABLE pairing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    male_id INTEGER,
    female_id INTEGER,
    pairing_date TEXT,
    expected_due_date TEXT
);
