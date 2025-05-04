-- 사용되는 ENUM 타입을 정의
CREATE TYPE DECO_TYPE AS ENUM (
    'terrain',
    'sky',
    'grass',
    'tree',
    'flower',
    'animal'
);

CREATE TABLE IF NOT EXISTS decorations (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    version SMALLINT NOT NULL,
    type DECO_TYPE NOT NULL,
    rarity SMALLINT NOT NULL,
    color JSON NULL,
    CONSTRAINT "unique_name" UNIQUE (name, version)
);
