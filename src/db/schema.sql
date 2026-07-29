CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    location TEXT,
    description TEXT,
    url TEXT,
    source TEXT NOT NULL,
    status TEXT DEFAULT 'open',
    date_scraped TEXT NOT NULL,
    UNIQUE(company, external_id)
);