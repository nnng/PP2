CREATE TABLE IF NOT EXISTS groups (
	id SERIAL PRIMARY KEY,
	name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO groups (name)
VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS contacts (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	surname VARCHAR(100) NOT NULL,
	email VARCHAR(100),
	birthday DATE,
	group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	UNIQUE (name, surname)
);

CREATE TABLE IF NOT EXISTS phones (
	id SERIAL PRIMARY KEY,
	contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
	phone VARCHAR(20) NOT NULL,
	type VARCHAR(10) NOT NULL CHECK (type IN ('home', 'work', 'mobile')),
	UNIQUE (contact_id, phone)
);

CREATE INDEX IF NOT EXISTS idx_contacts_group_id ON contacts(group_id);
CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name);
CREATE INDEX IF NOT EXISTS idx_contacts_surname ON contacts(surname);
CREATE INDEX IF NOT EXISTS idx_phones_contact_id ON phones(contact_id);
