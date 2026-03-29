import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from data_loader import load_data

def preprocess_data(path):
    df = load_data(path)

    # Drop identifiers (not behavioral features)
    df = df.drop(columns=["unit", "cycle"])

    # Normalize data to range [0,1]
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df)

    processed_df = pd.DataFrame(scaled_data, columns=df.columns)
    return processed_df


if __name__ == "__main__":
    processed = preprocess_data("data/raw/train_FD001.txt")
    processed.to_csv("data/processed/processed_data.csv", index=False)

    print(processed.head())
    print("Processed shape:", processed.shape)
