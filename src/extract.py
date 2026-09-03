import pandas as pd

def extract(path='data/raw/candidates.csv'):
    df = pd.read_csv(path, sep=';')
    return df


if __name__ == "__main__":
    df = extract()
    print(df.head())
    print(f"Filas: {len(df)}, Columnas: {len(df.columns)}")