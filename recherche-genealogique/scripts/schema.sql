-- Schéma de la base d'enquête généalogique (SQLite ; compatible DuckDB pour l'essentiel)

CREATE TABLE IF NOT EXISTS persons (
  id          INTEGER PRIMARY KEY,
  gedcom_id   TEXT,                   -- identifiant dans le GEDCOM d'origine (@I12@), pour l'aller-retour
  full_name   TEXT NOT NULL,
  given_names TEXT,
  surname     TEXT,
  birth_name  TEXT,
  sex         TEXT,
  notes       TEXT
);

CREATE TABLE IF NOT EXISTS sources (
  id          INTEGER PRIMARY KEY,
  label       TEXT NOT NULL,          -- ex. « AD69, recensement 1931, Lyon 2e »
  url         TEXT,
  reference   TEXT,                   -- cote, vue, page
  local_file  TEXT,                   -- image ou PDF conservé
  consulted   TEXT                    -- date de consultation (AAAA-MM-JJ)
);

CREATE TABLE IF NOT EXISTS events (
  id          INTEGER PRIMARY KEY,
  person_id   INTEGER NOT NULL REFERENCES persons(id),
  kind        TEXT NOT NULL,          -- naissance, mariage, décès, résidence, emploi…
  date        TEXT,                   -- texte libre ISO partiel (1936, 1936-05)
  place       TEXT,
  details     TEXT
);

CREATE TABLE IF NOT EXISTS relations (
  id          INTEGER PRIMARY KEY,
  person_a    INTEGER NOT NULL REFERENCES persons(id),
  person_b    INTEGER NOT NULL REFERENCES persons(id),
  kind        TEXT NOT NULL           -- époux, parent, enfant, gendre…
);

-- Une affirmation, sa source et son niveau de certitude.
-- A = acte vu · B = notice secondaire · C = déduction
CREATE TABLE IF NOT EXISTS evidence (
  id          INTEGER PRIMARY KEY,
  claim       TEXT NOT NULL,
  event_id    INTEGER REFERENCES events(id),
  relation_id INTEGER REFERENCES relations(id),
  source_id   INTEGER REFERENCES sources(id),
  certainty   TEXT NOT NULL CHECK (certainty IN ('A','B','C')),
  reader      TEXT,                   -- « assistant IA » ou prénom de l'humain pour une lecture d'image
  notes       TEXT
);

-- Toutes les recherches, y compris celles qui n'ont rien donné.
CREATE TABLE IF NOT EXISTS research_log (
  id          INTEGER PRIMARY KEY,
  searched_on TEXT,
  base        TEXT NOT NULL,
  query       TEXT NOT NULL,
  period      TEXT,
  result      TEXT NOT NULL,          -- « rien », « 3 homonymes », « trouvé : … »
  next_step   TEXT
);

CREATE TABLE IF NOT EXISTS help_requests (
  id          INTEGER PRIMARY KEY,
  asked_on    TEXT,
  request     TEXT NOT NULL,
  answer      TEXT,
  status      TEXT DEFAULT 'ouverte'
);
