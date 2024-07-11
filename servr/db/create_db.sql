-- Init database schema, only four columns to concern ourselves with

CREATE TABLE tip_records (

    id SMALLINT PRIMARY KEY,
    date DATE NOT NULL,
    tips DECIMAL (4, 2), -- specifies precision of decimal, 4 because it won't get past 5 digits per shift, 2 for tens place decimal
    notes TEXT,
);