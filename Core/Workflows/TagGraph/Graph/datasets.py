import pandas as pd
from pathlib import Path

path = Path(__file__).resolve().parents[4]
df = pd.read_csv(path / "7817_1.csv")

review_dataset = (
    df.drop_duplicates(subset=["asins", "reviews.text"])
    .groupby("asins")["reviews.text"]
    .apply(list)
    .reset_index(name="reviews")
    .rename(columns={"asins": "id"})
    .sort_values(by="reviews", key=lambda x: x.str.len(), ascending=False)
    .to_dict(orient="records")
)
