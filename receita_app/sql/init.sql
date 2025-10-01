-- Tabela para controle de arquivos baixados
CREATE TABLE IF NOT EXISTS download_control (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    path VARCHAR(500) DEFAULT '',
    name VARCHAR(200) NOT NULL,
    ref VARCHAR(7) NOT NULL,  -- formato YYYY-MM
    file_size BIGINT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    related_at INT REFERENCES download_control(id) ON DELETE CASCADE,
    UNIQUE(name, ref)
);

CREATE TABLE IF NOT EXISTS cnae
(
    code BIGINT,
    description text,
    effective_date date NOT NULL,
    download_control_id INT REFERENCES download_control(id) ON DELETE CASCADE,
    PRIMARY KEY (code, effective_date)
) PARTITION BY RANGE (effective_date);

CREATE TABLE IF NOT EXISTS natju
(
    code BIGINT,
    description text,
    effective_date date NOT NULL,
    download_control_id INT REFERENCES download_control(id) ON DELETE CASCADE,
    PRIMARY KEY (code, effective_date)
) PARTITION BY RANGE (effective_date);
