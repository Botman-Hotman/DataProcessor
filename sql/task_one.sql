CREATE table if not exists datawarehouse.job_titles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    pdl_count INT
);

CREATE table if not exists datawarehouse.related_titles (
    id SERIAL PRIMARY KEY,
    job_title_id INT REFERENCES datawarehouse.job_titles(id),
    related_title VARCHAR(255)
);
