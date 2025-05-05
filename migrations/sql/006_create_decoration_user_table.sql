CREATE TABLE IF NOT EXISTS decoration_user (
    did BIGINT NOT NULL,
    uid BIGINT NOT NULL,
    acquired_at TIMESTAMPTZ NOT NULL,
    is_equipped BOOLEAN DEFAULT FALSE,
    type DECO_TYPE NOT NULL,
    CONSTRAINT "pk_decoration_user" PRIMARY KEY (did, uid),
    CONSTRAINT "fkey_uid" FOREIGN KEY (uid) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "fkey_did" FOREIGN KEY (did) REFERENCES decorations (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_uid" ON decoration_user (uid);
