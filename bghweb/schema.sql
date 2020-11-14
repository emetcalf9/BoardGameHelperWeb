DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS history;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS collection;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE games (
  id INTEGER UNIQUE NOT NULL,
  name TEXT UNIQUE NOT NULL,
  minplay INTEGER NOT NULL,
  maxplay INTEGER NOT NULL
);

CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    games_played INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    winner_id INTEGER,
    score INTEGER,
    date_played TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (game_id) REFERENCES games (id),
    FOREIGN KEY (winner_id) REFERENCES players (id)
);

CREATE TABLE collection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    favorite INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (game_id) REFERENCES games (id)
)