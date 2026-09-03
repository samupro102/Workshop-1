import pandas as pd

def prepare(df):
    df['Application Date'] = pd.to_datetime(df['Application Date'])
    return df


def apply_business_rules(df):
    df['is_hired'] = (df['Code Challenge Score'] >= 7) & (df['Technical Interview Score'] >= 7)

    df['score_gap'] = df['Code Challenge Score'] - df['Technical Interview Score']

    df['yoe_range'] = pd.cut(
        df['YOE'],
        bins=[-1, 2, 5, 10, 15, 20, 100],
        labels=['0-2 yrs', '3-5 yrs', '6-10 yrs', '11-15 yrs', '16-20 yrs', '21+ yrs']
    )

    return df


if __name__ == "__main__":
    from extract import extract
    df = extract()
    df = prepare(df)
    df = apply_business_rules(df)
    print(df[['Code Challenge Score', 'Technical Interview Score', 'is_hired', 'score_gap', 'YOE', 'yoe_range']].head())
    print(f"Contratados: {df['is_hired'].sum()} de {len(df)} ({df['is_hired'].mean()*100:.1f}%)")