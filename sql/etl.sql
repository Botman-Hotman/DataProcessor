CREATE table if not exists datawarehouse."job_titles" (
    job_title text PRIMARY KEY,
    pdl_count INT NOT NULL
);

INSERT INTO datawarehouse."job_titles" (job_title, pdl_count)
select  
title,
pdl_count
from staging."2019_free_title_data";

CREATE table if not exists datawarehouse."related_titles" (
    id SERIAL PRIMARY KEY,
    job_title TEXT NOT NULL,
    related_title TEXT NOT NULL,
    FOREIGN KEY (job_title) REFERENCES  datawarehouse."job_titles" (job_title)
);

INSERT INTO datawarehouse."related_titles" (job_title, related_title)
SELECT
    title AS job_title,
    trim(both '"' FROM unnest(string_to_array(trim(both '{}' FROM top_related_titles), ',')))::text AS related_title
FROM
    staging."2019_free_title_data";
