#querie1
SELECT
    d.year,
    d.month,
    COUNT(*) AS total_applications,
    SUM(f.is_hired) AS total_hires,
    ROUND(
        (SUM(f.is_hired) / COUNT(*)) * 100,
        2
    ) AS hire_rate
FROM fact_application f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month
ORDER BY
    d.year,
    d.month;

#querie2
SELECT
    t.technology_name,
    COUNT(*) AS total_applications,
    SUM(f.is_hired) AS total_hires,
    ROUND(
        (SUM(f.is_hired) / COUNT(*)) * 100,
        2
    ) AS hire_rate
FROM fact_application f
JOIN dim_technology t
    ON f.technology_key = t.technology_key
GROUP BY
    t.technology_name
ORDER BY
    total_hires DESC;

 #querie3
  SELECT
    p.seniority,
    p.yoe_range,
    COUNT(*) AS total_applications,
    SUM(f.is_hired) AS total_hires,
    ROUND(
        (SUM(f.is_hired) / COUNT(*)) * 100,
        2
    ) AS hire_rate
FROM fact_application f
JOIN dim_candidate_profile p
    ON f.profile_key = p.profile_key
GROUP BY
    p.seniority,
    p.yoe_range
ORDER BY
    p.seniority,
    p.yoe_range;

#querie4

Technical Interview and code challenge
SELECT
    'Code Challenge' AS evaluation_stage,
    SUM(
        CASE
            WHEN code_challenge_score >= 7 THEN 1
            ELSE 0
        END
    ) AS passed,
    COUNT(*) AS total_applications,
    ROUND(
        SUM(
            CASE
                WHEN code_challenge_score >= 7 THEN 1
                ELSE 0
            END
        ) / COUNT(*) * 100,
        2
    ) AS pass_rate
FROM fact_application

UNION ALL

SELECT
    'Technical Interview' AS evaluation_stage,
    SUM(
        CASE
            WHEN technical_interview_score >= 7 THEN 1
            ELSE 0
        END
    ) AS passed,
    COUNT(*) AS total_applications,
    ROUND(
        SUM(
            CASE
                WHEN technical_interview_score >= 7 THEN 1
                ELSE 0
            END
        ) / COUNT(*) * 100,
        2
    ) AS pass_rate
FROM fact_application;
technology
SELECT
    t.technology_name,
    ROUND(
        SUM(
            CASE
                WHEN f.code_challenge_score >= 7 THEN 1
                ELSE 0
            END
        ) / COUNT(*) * 100,
        2
    ) AS code_challenge_pass_rate,
    ROUND(
        SUM(
            CASE
                WHEN f.technical_interview_score >= 7 THEN 1
                ELSE 0
            END
        ) / COUNT(*) * 100,
        2
    ) AS technical_interview_pass_rate
FROM fact_application f
JOIN dim_technology t
    ON f.technology_key = t.technology_key
GROUP BY
    t.technology_name
ORDER BY
    t.technology_name;
seniority
SELECT
    p.seniority,
    ROUND(
        SUM(
            CASE
                WHEN f.code_challenge_score >= 7 THEN 1
                ELSE 0
            END
        ) / COUNT(*) * 100,
        2
    ) AS code_challenge_pass_rate,
    ROUND(
        SUM(
            CASE
                WHEN f.technical_interview_score >= 7 THEN 1
                ELSE 0
            END
        ) / COUNT(*) * 100,
        2
    ) AS technical_interview_pass_rate
FROM fact_application f
JOIN dim_candidate_profile p
    ON f.profile_key = p.profile_key
GROUP BY
    p.seniority
ORDER BY
    p.seniority;
#querie5
SELECT
    c.country_name,
    COUNT(*) AS total_applications,
    SUM(f.is_hired) AS total_hires,
    ROUND(
        (SUM(f.is_hired) / COUNT(*)) * 100,
        2
    ) AS hire_rate
FROM fact_application f
JOIN dim_country c
    ON f.country_key = c.country_key
GROUP BY
    c.country_name
ORDER BY
    total_applications DESC;
