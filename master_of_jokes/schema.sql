DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS joke;
DROP TABLE IF EXISTS joke_taken;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  nickname TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  joke_balance INTEGER DEFAULT 0,
  viewed_jokes TEXT DEFAULT "^"
);

CREATE TABLE joke (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  rating INTEGER DEFAULT 0,
  times_rated INTEGER DEFAULT 0,
  FOREIGN KEY (author_id) REFERENCES user (id)
);