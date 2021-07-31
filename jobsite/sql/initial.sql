DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  pass TEXT NOT NULL
  );
  
CREATE TABLE jobs (
  id SERIAL PRIMARY KEY,
  name TEXT,
  company TEXT,
  oid INTEGER,
  fdate DATE,
  url TEXT,
  FOREIGN KEY (oid) references users(id) ON DELETE CASCADE
  );


