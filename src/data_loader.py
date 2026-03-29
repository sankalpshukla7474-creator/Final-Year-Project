import pandas as pd

def load_data(path):
    columns = (
        ["unit", "cycle"] +
        [f"op_setting_{i}" for i in range(1, 4)] +
        [f"sensor_{i}" for i in range(1, 22)]
    )

    df = pd.read_csv(
        path,
        sep=" ",
        header=None,
        names=columns
    )

    df = df.dropna(axis=1)
    return df


if __name__ == "__main__":
    df = load_data("data/raw/train_FD001.txt")
    print(df.head())
    print("Shape:", df.shape)
