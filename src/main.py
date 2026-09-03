from load import reset_schema, create_schema, load_data, validate_load


def main():
    print("=" * 50)
    print("ETL Pipeline - Recruitment Data Warehouse")
    print("Workshop 1 - Data Engineering")
    print("=" * 50)

    reset_schema()
    create_schema()
    load_data()
    validate_load()

    print("\nPipeline completado exitosamente.")


if __name__ == "__main__":
    main()