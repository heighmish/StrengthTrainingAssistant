 (
    Pd_id INTEGER,
    Set_id INTEGER PRIMARY KEY,
    Time DATETIME,
    Movement TEXT,
    E_reps INT CHECK(E_reps >= 0),
    E_rpe REAL CHECK(E_rpe>0),
    Weight_ REAL CHECK (Weight_ > 0),
    A_reps INT CHECK(E_reps >= 0),
    A_rpe REAL CHECK (E_rpe >0 and E_rpe <= 10),
    est_1rm REAL,
    FOREIGN KEY (Pd_id)
        REFERENCES program_days (Pd_id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);

