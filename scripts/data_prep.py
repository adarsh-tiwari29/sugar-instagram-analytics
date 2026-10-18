"""
Data Preparation - Sugar Cosmetics Instagram Performance Analytics
------------------------------------------------------------------
Reads the raw CSV, validates it, engineers the fields needed for the
dashboard, and saves:
    data/processed/sugar_instagram_cleaned.csv   (1 row per post)
    data/processed/hashtags_long.csv             (1 row per post-hashtag)
    data/processed/sugar_instagram_preprocessed.xlsx  (both + data dictionary)

Run from the project root:
    python scripts/data_prep.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "sugar_cosmetics_instagram_data.csv"
OUT_DIR = ROOT / "data" / "processed"

METRICS = ["Impressions", "Reach", "Likes", "Comments", "Shares",
           "Saves", "Profile Visits", "Follows"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]


def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise columns, types and text values."""
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    df["Post Date"] = pd.to_datetime(df["Post Date"], errors="coerce")
    for c in ["Post Type", "Campaign Type", "Audience Emotion",
              "Engagement Source", "Hashtags"]:
        df[c] = df[c].astype(str).str.strip()
    for c in METRICS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # drop unusable rows (none expected in this dataset, kept for safety)
    df = df.dropna(subset=["Post Date", "Reach"])
    df = df[df["Reach"] > 0]
    df = df.drop_duplicates()
    return df.reset_index(drop=True)


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Add the calculated fields used across the dashboard."""
    df = df.copy()

    # Post ID + label (dataset has no Caption column, so we build a readable label)
    df.insert(0, "Post ID", [f"P{i:05d}" for i in range(1, len(df) + 1)])
    df["Post Label"] = (df["Post ID"] + " | " + df["Post Type"] + " | "
                        + df["Campaign Type"] + " | "
                        + df["Post Date"].dt.strftime("%d %b %Y"))

    # Date parts
    df["Year"] = df["Post Date"].dt.year
    df["Month"] = df["Post Date"].dt.to_period("M").dt.to_timestamp()
    df["Month-Year"] = df["Post Date"].dt.strftime("%b %Y")
    df["Weekday"] = pd.Categorical(df["Post Date"].dt.day_name(),
                                   categories=WEEKDAYS, ordered=True)
    df["Week Part"] = df["Weekday"].isin(["Saturday", "Sunday"]).map(
        {True: "Weekend", False: "Weekday"})

    # Engagement metrics
    df["Total Engagement"] = df[["Likes", "Comments", "Shares", "Saves"]].sum(axis=1)
    df["Engagement Rate (%)"] = df["Total Engagement"] / df["Reach"] * 100
    df["Reach Rate (%)"] = df["Reach"] / df["Impressions"] * 100
    df["Save Rate (%)"] = df["Saves"] / df["Reach"] * 100
    df["Share Rate (%)"] = df["Shares"] / df["Reach"] * 100
    df["Follow Rate (%)"] = df["Follows"] / df["Reach"] * 100
    df["Profile-to-Follow (%)"] = (df["Follows"] / df["Profile Visits"]
                                   .where(df["Profile Visits"] > 0) * 100)

    # Hashtag helpers
    df["Hashtag Count"] = df["Hashtags"].str.count("#")

    # Engagement tier (quartiles of ER)
    df["ER Tier"] = pd.qcut(df["Engagement Rate (%)"], 4,
                            labels=["Low", "Medium", "High", "Top"])
    return df


def explode_hashtags(df: pd.DataFrame) -> pd.DataFrame:
    """One row per post-hashtag pair for hashtag analysis."""
    cols = ["Post ID", "Post Date", "Month", "Post Type", "Campaign Type",
            "Engagement Source", "Hashtags", "Impressions", "Reach", "Likes",
            "Comments", "Shares", "Saves", "Follows", "Total Engagement",
            "Engagement Rate (%)"]
    long = df[cols].copy()
    long["Hashtag"] = long["Hashtags"].str.split(",")
    long = long.explode("Hashtag")
    long["Hashtag"] = long["Hashtag"].str.strip()
    long = long[long["Hashtag"].str.startswith("#")]
    return long.drop(columns="Hashtags").reset_index(drop=True)


def prepare(path: Path = RAW_PATH):
    df = engineer(clean(load_raw(path)))
    return df, explode_hashtags(df)


DATA_DICTIONARY = [
    ("Post ID", "Generated unique ID for each post"),
    ("Post Label", "Readable label (ID | Type | Campaign | Date) - used instead of caption, which is not in the dataset"),
    ("Month / Month-Year", "Post date converted to month (for monthly trend)"),
    ("Weekday", "Day name extracted from Post Date"),
    ("Total Engagement", "Likes + Comments + Shares + Saves"),
    ("Engagement Rate (%)", "Total Engagement / Reach x 100"),
    ("Reach Rate (%)", "Reach / Impressions x 100"),
    ("Save Rate (%) / Share Rate (%)", "Saves or Shares / Reach x 100"),
    ("Follow Rate (%)", "Follows / Reach x 100"),
    ("Profile-to-Follow (%)", "Follows / Profile Visits x 100"),
    ("Hashtag Count", "Number of hashtags used in the post"),
    ("ER Tier", "Quartile bucket of Engagement Rate (Low / Medium / High / Top)"),
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = load_raw()
    print(f"Raw rows: {len(raw):,} | columns: {raw.shape[1]}")
    print(f"Missing values: {int(raw.isna().sum().sum())} | duplicates: {int(raw.duplicated().sum())}")

    df, tags = prepare()
    print(f"Clean rows: {len(df):,} | hashtag rows: {len(tags):,}")
    print(f"Date range: {df['Post Date'].min():%d %b %Y} - {df['Post Date'].max():%d %b %Y}")

    df.to_csv(OUT_DIR / "sugar_instagram_cleaned.csv", index=False)
    tags.to_csv(OUT_DIR / "hashtags_long.csv", index=False)

    xlsx = OUT_DIR / "sugar_instagram_preprocessed.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
        out = df.copy()
        out["Post Date"] = out["Post Date"].dt.date
        out["Month"] = out["Month"].dt.date
        out.round(3).to_excel(w, sheet_name="Posts_Cleaned", index=False)
        t = tags.copy()
        t["Post Date"] = t["Post Date"].dt.date
        t["Month"] = t["Month"].dt.date
        t.round(3).to_excel(w, sheet_name="Hashtags_Long", index=False)
        pd.DataFrame(DATA_DICTIONARY, columns=["Field", "Definition"]).to_excel(
            w, sheet_name="Data_Dictionary", index=False)
    print(f"Saved -> {OUT_DIR}")


if __name__ == "__main__":
    main()
