CREATE TABLE IF NOT EXISTS challenge_decoration (
    did BIGINT NOT NULL,
    cid BIGINT NOT NULL,
    CONSTRAINT "pk_challenge_decoration" PRIMARY KEY (did, cid),
    CONSTRAINT "fkey_cid" FOREIGN KEY (cid) REFERENCES challenges (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "fkey_did" FOREIGN KEY (did) REFERENCES decorations (id) ON DELETE CASCADE ON UPDATE CASCADE
);
