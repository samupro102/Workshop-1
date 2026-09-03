import pandas as pd


def build_dim_technology(df):
    technologies = df['Technology'].unique()
    dim_technology = pd.DataFrame({'technology_name': technologies})
    dim_technology['technology_key'] = range(1, len(dim_technology) + 1)
    return dim_technology


def build_dim_country(df):
    countries = df['Country'].unique()
    dim_country = pd.DataFrame({'country_name': countries})
    dim_country['country_key'] = range(1, len(dim_country) + 1)
    return dim_country


def build_dim_candidate_profile(df):
    profiles = df[['Seniority', 'yoe_range']].drop_duplicates()
    profiles = profiles.rename(columns={'Seniority': 'seniority'})
    profiles['profile_key'] = range(1, len(profiles) + 1)
    return profiles

def build_dim_date(df):
    fechas_unicas = df['Application Date'].unique()
    dim_date = pd.DataFrame({'full_date': fechas_unicas})
    
    dim_date['year'] = dim_date['full_date'].dt.year
    dim_date['month'] = dim_date['full_date'].dt.month
    dim_date['day'] = dim_date['full_date'].dt.day
    dim_date['month_name'] = dim_date['full_date'].dt.month_name()
    dim_date['day_of_week'] = dim_date['full_date'].dt.day_name()
    
    dim_date['date_key'] = range(1, len(dim_date) + 1)
    
    return dim_date

def build_fact_application(df, dim_technology, dim_country, dim_candidate_profile, dim_date):
    
    df = df.merge(dim_technology, left_on='Technology', right_on='technology_name', how='left')
    
    df = df.merge(dim_country, left_on='Country', right_on='country_name', how='left')
    
    df = df.merge(dim_candidate_profile, left_on=['Seniority', 'yoe_range'], right_on=['seniority', 'yoe_range'], how='left')
    
    df = df.merge(dim_date, left_on='Application Date', right_on='full_date', how='left')
    
    fact_application = df[[
        'date_key', 'technology_key', 'profile_key', 'country_key',
        'Code Challenge Score', 'Technical Interview Score', 'score_gap', 'is_hired'
    ]].copy()
    
    fact_application = fact_application.rename(columns={
        'Code Challenge Score': 'code_challenge_score',
        'Technical Interview Score': 'technical_interview_score'
    })
    
    fact_application.insert(0, 'application_key', range(1, len(fact_application) + 1))
    
    return fact_application

if __name__ == "__main__":
    from extract import extract
    from transform import prepare, apply_business_rules

    df = extract()
    df = prepare(df)
    df = apply_business_rules(df)

    dim_technology = build_dim_technology(df)
    print(dim_technology)

    dim_country = build_dim_country(df)
    print(dim_country)
    print(f"Total países: {len(dim_country)}")

    dim_candidate_profile = build_dim_candidate_profile(df)
    print(dim_candidate_profile)
    print(f"Total perfiles: {len(dim_candidate_profile)}")

    dim_date = build_dim_date(df)
    print(dim_date)
    print(f"Total fechas: {len(dim_date)}")

    dim_technology = build_dim_technology(df)
    dim_country = build_dim_country(df)
    dim_candidate_profile = build_dim_candidate_profile(df)
    dim_date = build_dim_date(df)

    fact_application = build_fact_application(df, dim_technology, dim_country, dim_candidate_profile, dim_date)
    print(fact_application.head(10))
    print(f"Total filas en fact_application: {len(fact_application)}")
    print(fact_application.isnull().sum())