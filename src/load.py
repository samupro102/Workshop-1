from sqlalchemy import create_engine, text
import sys
sys.path.append('.')

from extract import extract
from transform import prepare, apply_business_rules
from dimensional_model import (
    build_dim_technology, build_dim_country,
    build_dim_candidate_profile, build_dim_date,
    build_fact_application
)

engine = create_engine('mysql+pymysql://root:Soydelrojo4@localhost:3307/recruitment_dw')


def reset_schema():
    tablas = ['fact_application', 'dim_date', 'dim_technology', 'dim_candidate_profile', 'dim_country']
    with engine.begin() as conn:
        for tabla in tablas:
            conn.execute(text(f"DROP TABLE IF EXISTS {tabla}"))
    print("Tablas anteriores eliminadas (si existían).")


def create_schema():
    with open('sql/create_tables.sql', 'r') as f:
        script = f.read()
    statements = [s.strip() for s in script.split(';') if s.strip()]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
    print("Esquema creado correctamente.")


def load_data():
    df = extract()
    df = prepare(df)
    df = apply_business_rules(df)

    dim_technology = build_dim_technology(df)
    dim_country = build_dim_country(df)
    dim_candidate_profile = build_dim_candidate_profile(df)
    dim_date = build_dim_date(df)
    fact_application = build_fact_application(df, dim_technology, dim_country, dim_candidate_profile, dim_date)

    dim_date.to_sql('dim_date', engine, if_exists='append', index=False)
    print(f"dim_date cargada: {len(dim_date)} filas")

    dim_technology.to_sql('dim_technology', engine, if_exists='append', index=False)
    print(f"dim_technology cargada: {len(dim_technology)} filas")

    dim_candidate_profile.to_sql('dim_candidate_profile', engine, if_exists='append', index=False)
    print(f"dim_candidate_profile cargada: {len(dim_candidate_profile)} filas")

    dim_country.to_sql('dim_country', engine, if_exists='append', index=False)
    print(f"dim_country cargada: {len(dim_country)} filas")

    fact_application.to_sql('fact_application', engine, if_exists='append', index=False)
    print(f"fact_application cargada: {len(fact_application)} filas")


def validate_load():
    validaciones = {
        'date_key': 'dim_date',
        'technology_key': 'dim_technology',
        'profile_key': 'dim_candidate_profile',
        'country_key': 'dim_country'
    }

    print("\n--- Validación de integridad referencial ---")
    with engine.connect() as conn:
        for llave, tabla_dim in validaciones.items():
            query = text(f"""
                SELECT COUNT(*) AS referencias_invalidas
                FROM fact_application f
                LEFT JOIN {tabla_dim} d ON f.{llave} = d.{llave}
                WHERE d.{llave} IS NULL
            """)
            resultado = conn.execute(query).scalar()
            estado = "OK" if resultado == 0 else "ERROR"
            print(f"{llave} -> {tabla_dim}: {resultado} referencias inválidas [{estado}]")


if __name__ == "__main__":
    reset_schema()
    create_schema()
    load_data()
    validate_load()