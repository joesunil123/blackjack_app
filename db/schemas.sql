DROP TABLE IF EXISTS team_details;

CREATE TABLE team_details (
    name VARCHAR PRIMARY KEY,
    reg VARCHAR,
    grp INTEGER
);

DROP TABLE IF EXISTS match_details;

CREATE TABLE match_details (
    player_one VARCHAR PRIMARY KEY,
    player_two VARCHAR,
    goals INTEGER,
    result VARCHAR
);
