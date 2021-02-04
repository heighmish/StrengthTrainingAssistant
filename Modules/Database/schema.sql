CREATE TABLE IF NOT EXISTS programs (
    P_id INTEGER PRIMARY KEY,
    P_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS program_weeks (
    Pw_id INTEGER PRIMARY KEY,
    P_id INTEGER,
    Week_num INTEGER,
    Week_complete INTEGER DEFAULT 0,
    FOREIGN KEY (P_id)
        REFERENCES programs (P_id)
);

CREATE TABLE IF NOT EXISTS program_days (
    Pd_id INTEGER PRIMARY KEY,
    Pw_id INTEGER,
    P_id INTEGER,
    Day_num INTEGER NOT NULL,
    Day_complete INTEGER DEFAULT 0,
    FOREIGN KEY (Pw_id)
        REFERENCES program_weeks (Pw_id)
    FOREIGN KEY (P_id) REFERENCES programs (P_id)
);


