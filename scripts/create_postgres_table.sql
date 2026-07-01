CREATE TABLE IF NOT EXISTS submissions (
    id BIGSERIAL PRIMARY KEY,
    codigo_mca TEXT NOT NULL,
    nombre_mca TEXT NOT NULL,
    brigadas_realizadas INTEGER NOT NULL,
    personas_brigada_1 INTEGER NOT NULL,
    personas_brigada_2 INTEGER NOT NULL,
    region TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_submissions_created_at
    ON submissions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_submissions_codigo_mca
    ON submissions(codigo_mca);
