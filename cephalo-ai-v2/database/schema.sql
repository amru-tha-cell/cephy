-- SQLAlchemy creates the SQLite schema automatically on API startup.
-- PostgreSQL: set DATABASE_URL=postgresql+psycopg://user:password@host:5432/cephalo
CREATE TABLE cases (
  id INTEGER PRIMARY KEY,
  patient_code VARCHAR(80) NOT NULL,
  image_path VARCHAR(500) NOT NULL,
  image_width INTEGER NOT NULL,
  image_height INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL,
  landmarks JSON,
  ground_truth JSON,
  initial_landmarks JSON,
  evaluation JSON,
  measurements JSON,
  history JSON
);
