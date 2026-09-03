# Workshop 1 — From Business Requirements to a Dimensional Data Warehouse

## Project Objective

Design and implement a Dimensional Data Warehouse that transforms raw candidate
application data from a technology recruitment company into an analytical system
capable of answering five specific business requirements about hiring performance,
using a reproducible ETL pipeline built in Python and loaded into a MySQL database.

## Business Context

A technology recruitment company receives thousands of job applications from
candidates with different professional backgrounds, experience levels, countries,
seniority levels, and technology profiles. Each candidate is evaluated through two
technical assessments: a Code Challenge and a Technical Interview. The organization
needs an analytical system — not raw files — to understand hiring patterns and
support data-driven recruitment decisions.

## Business Requirements

| ID | Business Requirement | Business Question | Decision Supported |
|----|----|----|----|
| R1 | Hiring Trends: Monitor hiring trends over time to identify changes in recruitment outcomes. | How have the number of applications, hires, and the hire rate changed over time (by month and year)? | Whether recruitment funnel performance is improving, declining, or stable, and when to plan hiring pushes. |
| R2 | Technology Analysis: Compare hiring results across technologies to identify which technical profiles generate the largest number and proportion of hired candidates. | Which technologies produce the largest number and proportion of hired candidates? | Where to focus sourcing and interview-pipeline investment by tech stack. |
| R3 | Candidate Profile Analysis: Analyze hiring outcomes according to candidate seniority and years of professional experience. | How do hiring outcomes differ across candidate seniority levels and years of experience? | How to calibrate seniority-level expectations and interview difficulty. |
| R4 | Evaluation Stage Funnel Analysis: Determine which evaluation stage (Code Challenge or Technical Interview) filters out more candidates, and whether this varies by technology or seniority level. | Which evaluation stage has a lower pass rate (score ≥ 7), and is this consistent across technologies and seniority levels or does it vary? | Guides where to invest in improving the evaluation process, depending on which stage is the bigger bottleneck. |
| R5 | Geographic Recruitment Analysis: Identify countries with the highest recruitment activity and compare their hiring outcomes. | Which countries generate the highest volume of applications, and which countries have the best hiring rates? | Supports decisions on where to prioritize sourcing investment and recruiting budget by geography. |

## Requirements Traceability

| Requirement | Business Question | Data Required | Expected Analytical Output |
|---|---|---|---|
| R1 | How have the number of applications, hires, and the hire rate changed over time (by month and year)? | Application Date, Code Challenge Score, Technical Interview Score | A time series (monthly/yearly) showing total applications, total hires, and hire rate (%) per period. |
| R2 | Which technologies produce the largest number and proportion of hired candidates? | Technology, Code Challenge Score, Technical Interview Score | A ranked table showing total applications, total hires, and hire rate (%) per technology. |
| R3 | How do hiring outcomes differ across candidate seniority levels and years of experience? | Seniority, YOE, Code Challenge Score, Technical Interview Score | A table showing total applications, total hires, and hire rate (%) broken down by seniority and experience range. |
| R4 | Which evaluation stage has a lower pass rate, and is this consistent across technologies and seniority levels? | Code Challenge Score, Technical Interview Score, Technology, Seniority | A comparison table showing the pass rate (%) of each stage overall, by technology, and by seniority. |
| R5 | Which countries generate the highest volume of applications, and which have the best hiring rates? | Country, Code Challenge Score, Technical Interview Score | A ranked table showing total applications, total hires, and hire rate (%) per country. |

## Dataset Description

- **Source:** `data/raw/candidates.csv` — 50,000 rows, one row per candidate application. **Delimiter is `;`**, not the default comma.
- **Columns:** First Name, Last Name, Email, Application Date, Country, YOE, Seniority, Technology, Code Challenge Score, Technical Interview Score.

### Business Rule — Hiring Outcome

```
HIRED = (Code Challenge Score >= 7) AND (Technical Interview Score >= 7)
```

## Main Profiling Findings

- **0 missing values** in any column.
- **0 fully duplicated rows**, but **167 duplicated emails**, corresponding to candidates who applied more than once — kept as separate applications, since the fact table grain is "one application," not "one candidate."
- **244 unique countries**, **7 seniority levels** (Trainee, Intern, Junior, Mid-Level, Senior, Lead, Architect), **24 unique technologies**.
- Application dates range from **2018-01-01 to 2022-07-04**.
- **YOE** ranges from **0 to 30 years**. Using each individual year as a category would create up to 31 distinct values per seniority level, making analysis harder to read — this motivated grouping YOE into experience ranges (0-2, 3-5, 6-10, 11-15, 16-20, 21+ years) in the dimensional model.
- Both **Code Challenge Score** and **Technical Interview Score** range exactly from **0 to 10**, confirming the source data is fully consistent with the documented business rule — no out-of-range values needed correction.
- Categorical columns (Country, Seniority, Technology) were explicitly checked for formatting inconsistencies (extra whitespace, casing) — none were found.

## Business Process

The business process being analyzed is the **technical recruitment and hiring
process**. Each record represents a candidate's application, evaluated through two
technical assessments (Code Challenge and Technical Interview), resulting in a
hiring decision. This process was selected because it directly aligns with all five
business requirements (R1–R5), which examine hiring trends, technology performance,
candidate profiles, evaluation-stage effectiveness, and geographic recruitment
patterns — all facets of this single end-to-end process.

## Grain Definition

One row in the **Fact Table** represents **one candidate application** — a single
application submitted by a candidate for a technical role, including their Code
Challenge Score, Technical Interview Score, and the resulting hiring outcome for
that specific application.
## Star Schema Diagram

![Star Schema](/diagrams/star_schema.png)

## Dimensions

| Dimension | Purpose | Main Attributes | Requirement(s) Supported |
|---|---|---|---|
| **Dim_Date** | Provides temporal context to each application, enabling trend analysis across different time periods. | date_key (surrogate key), full_date, year, month, day, month_name, day_of_week | R1 |
| **Dim_Technology** | Groups applications by the technical role/stack the candidate applied for, enabling comparison of hiring performance across technologies. | technology_key (surrogate key), technology_name | R2, R4 |
| **Dim_Candidate_Profile** | Groups applications by candidate seniority level and experience range, enabling analysis of hiring outcomes across candidate profiles. | profile_key (surrogate key), seniority, yoe_range | R3, R4 |
| **Dim_Country** | Groups applications by candidate country, enabling geographic analysis of recruitment activity and hiring outcomes. | country_key (surrogate key), country_name | R5 |

Candidate names and emails are intentionally excluded from the dimensional model:
no business requirement needs individual identification, and including them would
add personal data with no analytical purpose.

## Facts / Measures

| Measure | Meaning | Source / Calculation | Requirement(s) Supported |
|---|---|---|---|
| `code_challenge_score` | Raw Code Challenge assessment score (0–10) | Source column | R4 |
| `technical_interview_score` | Raw Technical Interview assessment score (0–10) | Source column | R4 |
| `score_gap` | Difference between the two evaluation stages for this application (semi-additive; average, don't sum) | Derived: code_challenge_score − technical_interview_score | R4 |
| `is_hired` | Whether this specific application resulted in a hire (1 = hired, 0 = not hired; additive) | Derived: (code_challenge_score ≥ 7) AND (technical_interview_score ≥ 7) | R1, R2, R3, R5 |

## Model Validation Against Requirements

| Requirement | Dimension(s) Required | Measure(s) Required | Supported? |
|---|---|---|---|
| R1 | dim_date | is_hired | Yes |
| R2 | dim_technology | is_hired | Yes |
| R3 | dim_candidate_profile | is_hired | Yes |
| R4 | dim_technology, dim_candidate_profile | code_challenge_score, technical_interview_score, score_gap | Yes |
| R5 | dim_country | is_hired | Yes |

## ETL Architecture
```
data/raw/candidates.csv
|
v
extract.py -> raw DataFrame (no business logic)
|
v
transform.py -> prepare(): types, dates
-> apply_business_rules(): HIRED rule, score_gap, yoe_range
|
v
dimensional_model.py -> dim_date, dim_technology, dim_candidate_profile,
dim_country, fact_application
(surrogate keys, key mapping via merge)
|
v
load.py -> creates schema (sql/create_tables.sql),
loads dimensions -> fact table,
validates referential integrity
|
v
MySQL Data Warehouse
|
v
sql/analytical_queries.sql -> R1-R5 analytical outputs
|
v
Power BI (connected directly to the Data Warehouse)
```
## Main Transformation Decisions

- The CSV is semicolon-separated (`;`) — confirmed during profiling, applied in `extract.py`.
- No missing values were found, so no imputation was required.
- Duplicated emails (repeat applicants) are **kept** as separate applications, consistent with the declared grain ("one application" per row, not "one candidate").
- Categorical columns (Country, Seniority, Technology) were verified to have no formatting inconsistencies, so no standardization step was needed.
- `score_gap` and `yoe_range` are derived attributes created specifically to support R3/R4 — no transformation without analytical purpose was added.
- Surrogate keys for all four dimensions are generated in Python (`dimensional_model.py`), never using natural source values (like technology name or country name) as primary keys.

## Technologies Used

- Python, Pandas
- Jupyter Notebook (initial data profiling)
- SQL (DDL + analytical queries)
- MySQL (Data Warehouse), via SQLAlchemy + PyMySQL
- Git / GitHub
- Power BI (BI visualization), connected directly to the MySQL Data Warehouse

## Instructions to Run the Project

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure MySQL is running, and create an empty database named recruitment_dw
#    (e.g. in MySQL Workbench: CREATE DATABASE recruitment_dw;)

# 3. Update the database connection string in src/load.py with your own
#    MySQL username, password, host and port.

# 4. Run the full ETL pipeline: extract -> transform -> dimensional model
#    -> load -> validate referential integrity
cd src
python main.py

# 5. (Optional) Re-run the profiling notebook
jupyter notebook notebooks/data_profiling.ipynb

# 6. Run the analytical queries in sql/analytical_queries.sql against the
#    loaded Data Warehouse using MySQL Workbench or any SQL client.

# 7. Connect Power BI (or another BI tool) directly to the recruitment_dw
#    MySQL database to reproduce the visualizations.
```

> **Note on the Data Warehouse:** this project uses MySQL as the Data
> Warehouse engine (a client-server database), not SQLite. Because of this,
> there is no portable `.db` file to include in the repository — the
> database is fully reproducible by running `main.py` against a local MySQL
> instance, as described above.
## Analytical Queries and KPIs

All queries run against the **loaded Data Warehouse** (`sql/analytical_queries.sql`),
never against the source CSV. Full result sets are saved in `results/`.

### R1 — Hiring Trends

**Business Question:** How have the number of applications, hires, and the hire
rate changed over time (by month and year)?

**SQL Query:**
```sql
SELECT
    d.year,
    d.month,
    COUNT(*) AS total_applications,
    SUM(f.is_hired) AS total_hires,
    ROUND((SUM(f.is_hired) / COUNT(*)) * 100, 2) AS hire_rate
FROM fact_application f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
```

**Result:** Monthly hire rate remained relatively stable across the full
2018–2022 period, fluctuating between approximately 11% and 16%, without a
clear long-term upward or downward trend. Monthly application volume was
also consistent, ranging from roughly 800 to 990 applications per month
(July 2022 is a partial month, since the dataset ends on July 4, 2022).

**Interpretation:** The recruitment process shows stable performance over
time rather than seasonal spikes or a degrading/improving trend. This
suggests that whatever is driving hiring outcomes has remained consistent,
and future changes in hire rate would likely reflect a genuine shift, not
normal month-to-month noise.

---

### R2 — Technology Analysis

**Business Question:** Which technologies produce the largest number and
proportion of hired candidates?

**SQL Query:**
```sql
SELECT
    t.technology_name,
    COUNT(*) AS total_applications,
    SUM(f.is_hired) AS total_hires,
    ROUND((SUM(f.is_hired) / COUNT(*)) * 100, 2) AS hire_rate
FROM fact_application f
JOIN dim_technology t ON f.technology_key = t.technology_key
GROUP BY t.technology_name
ORDER BY total_hires DESC;
```

**Result:** Game Development (519 hires) and DevOps (495 hires) produce the
largest number of hired candidates, driven by roughly double the
application volume of other technologies, not a higher hire rate. In
proportion, Development - CMS Backend has the highest hire rate (15.09%),
followed by Database Administration (14.59%) and System Administration
(14.55%). Social Media Community Management has the lowest hire rate
(11.69%).

**Interpretation:** Recruitment volume and recruitment quality (hire rate)
are not the same thing — Game Development and DevOps generate the most
hires simply because more people apply, while smaller-volume technologies
like Development - CMS Backend convert applicants into hires more
efficiently. Growing the larger pipelines further would yield more hires by
volume, while studying CMS Backend's process could reveal best practices to
apply elsewhere.

---

### R3 — Candidate Profile Analysis

**Business Question:** How do hiring outcomes differ across candidate
seniority levels and years of experience?

**SQL Query:**
```sql
SELECT
    p.seniority,
    p.yoe_range,
    COUNT(*) AS total_applications,
    SUM(f.is_hired) AS total_hires,
    ROUND((SUM(f.is_hired) / COUNT(*)) * 100, 2) AS hire_rate
FROM fact_application f
JOIN dim_candidate_profile p ON f.profile_key = p.profile_key
GROUP BY p.seniority, p.yoe_range
ORDER BY p.seniority, p.yoe_range;
```

**Result:** The highest hire rate (17.11%) belongs to Interns with 0-2
years of experience, while the lowest (10.78%) belongs to candidates
labeled Mid-Level with 0-2 years of experience. No simple linear
relationship exists between experience and hire rate across seniority
levels.

**Interpretation:** The low hire rate for "Mid-Level, 0-2 years" candidates
may indicate a mismatch between how candidates self-report seniority and
their actual experience. This is a useful signal for recruiters: seniority
self-classification should not be taken at face value.

---

### R4 — Evaluation Stage Funnel Analysis

**Business Question:** Which evaluation stage (Code Challenge or Technical
Interview) has a lower pass rate, and is this consistent across
technologies and seniority levels or does it vary?

**SQL Query:**
```sql
SELECT
    t.technology_name,
    ROUND(SUM(CASE WHEN f.code_challenge_score >= 7 THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS code_challenge_pass_rate,
    ROUND(SUM(CASE WHEN f.technical_interview_score >= 7 THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS technical_interview_pass_rate
FROM fact_application f
JOIN dim_technology t ON f.technology_key = t.technology_key
GROUP BY t.technology_name
ORDER BY t.technology_name;
```

**Result:** Overall, the Code Challenge has a 36.46% pass rate. Broken
down by seniority, both stages perform very similarly (within ~1.3 points)
at every level. Broken down by technology, most technologies also show
similar pass rates, but Security Compliance (34.99% vs. 38.44%) and QA
Automation (34.73% vs. 37.79%) show the Technical Interview being
noticeably easier to pass.

**Interpretation:** The funnel is broadly balanced across the organization
and across seniority levels. However, for Security Compliance and QA
Automation, the Code Challenge appears meaningfully harder than the
Technical Interview, which may indicate the code challenge content for
those tracks is miscalibrated and worth reviewing.

---

### R5 — Geographic Recruitment Analysis

**Business Question:** Which countries generate the highest volume of
applications, and which countries have the best hiring rates?

**SQL Query:**
```sql
SELECT
    c.country_name,
    COUNT(*) AS total_applications,
    SUM(f.is_hired) AS total_hires,
    ROUND((SUM(f.is_hired) / COUNT(*)) * 100, 2) AS hire_rate
FROM fact_application f
JOIN dim_country c ON f.country_key = c.country_key
GROUP BY c.country_name
ORDER BY total_applications DESC;
```

**Result:** Application volume is evenly distributed across the 244
countries, with no single country dominating (the highest, Malawi,
accounts for only 242 of 50,000 applications). Hire rates vary from 7.58%
(Montenegro) to 22.56% (Northern Mariana Islands).

**Interpretation:** Because each country has a relatively small sample
size (roughly 150-250 applications), the wide spread in hire rates is
partly explained by statistical noise rather than genuine differences in
candidate quality by geography. This should be revisited once more data
accumulates per country, or by grouping countries into larger regions.

## Main Business Findings

- Hiring performance has been **stable over the 2018–2022 period**, with no
  clear trend of improvement or decline (R1).
- **Volume and quality of hires are different signals** by technology —
  the technologies with the most hires are not the ones with the best hire
  rate (R2).
- **Early-career candidates (Interns) convert best**, while the
  "Mid-Level, 0-2 years" segment underperforms, suggesting a possible
  seniority self-classification issue worth investigating (R3).
- The **two evaluation stages are broadly balanced**, but Security
  Compliance and QA Automation show the Code Challenge as a harder gate
  than the Technical Interview — worth reviewing (R4).
- **Geographic hire-rate differences are likely influenced by small sample
  sizes** per country, and should be interpreted cautiously before
  informing sourcing budget decisions (R5).

## Final Requirements Validation

| Requirement | Implemented? | DW Tables Used | Query / KPI | Main Finding |
|---|---|---|---|---|
| R1 | Yes | fact_application, dim_date | Monthly hire rate (%) trend | Hire rate stable (~11%-16%) across 2018-2022. |
| R2 | Yes | fact_application, dim_technology | Total hires and hire rate (%) by technology | Game Development/DevOps lead in volume; CMS Backend leads in hire rate (15.09%). |
| R3 | Yes | fact_application, dim_candidate_profile | Hire rate (%) by seniority and experience | Interns (0-2 yrs) highest (17.11%); Mid-Level (0-2 yrs) lowest (10.78%). |
| R4 | Yes | fact_application, dim_technology, dim_candidate_profile | Code Challenge vs. Technical Interview pass rate (%) | Balanced overall; Security Compliance & QA Automation show a notable gap. |
| R5 | Yes | fact_application, dim_country | Total applications and hire rate (%) by country | Volume evenly spread; hire rate varies 7.58%-22.56%, limited by sample size. |

**Does the final Data Warehouse provide enough information to satisfy all
five business requirements?** Yes. Each requirement was answered directly
from the star schema using SQL queries executed against the loaded Data
Warehouse, matching the expected analytical output defined in the
Requirements Traceability table.

**Does the dimensional model contain elements that are not justified by
the analytical requirements?** No. Every dimension and measure was included
specifically because at least one requirement needed it. No candidate
personal data (name, email) or unused attributes were added to the model.

**What business decisions can now be supported by the implemented
analytical system?** Monitoring recruitment funnel performance over time;
prioritizing technology-specific sourcing based on both volume and
conversion quality; calibrating seniority-level expectations; reviewing
evaluation stages that may be miscalibrated for specific technologies; and
informing early-stage geographic sourcing priorities, with the caveat that
more data is needed for high-confidence country-level decisions.
