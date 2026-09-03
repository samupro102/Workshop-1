CREATE TABLE dim_date (
    date_key     INT PRIMARY KEY,
    full_date    DATE,
    year         INT,
    month        INT,
    day          INT,
    month_name   VARCHAR(20),
    day_of_week  VARCHAR(20)
);

CREATE TABLE dim_technology (
    technology_key   INT PRIMARY KEY,
    technology_name  VARCHAR(100)
);

CREATE TABLE dim_candidate_profile (
    profile_key   INT PRIMARY KEY,
    seniority     VARCHAR(30),
    yoe_range     VARCHAR(20)
);

CREATE TABLE dim_country (
    country_key   INT PRIMARY KEY,
    country_name  VARCHAR(100)
);

CREATE TABLE fact_application (
    application_key             INT PRIMARY KEY,
    date_key                    INT,
    technology_key              INT,
    profile_key                 INT,
    country_key                 INT,
    code_challenge_score        INT,
    technical_interview_score   INT,
    score_gap                   INT,
    is_hired                    INT,
    FOREIGN KEY (date_key)       REFERENCES dim_date(date_key),
    FOREIGN KEY (technology_key) REFERENCES dim_technology(technology_key),
    FOREIGN KEY (profile_key)    REFERENCES dim_candidate_profile(profile_key),
    FOREIGN KEY (country_key)    REFERENCES dim_country(country_key)
);