import numpy as np
import pandas as pd
from pathlib import Path

_cache = None
DATA_PATH = Path(__file__).parent.parent / "data.csv"


def generate_data() -> pd.DataFrame:
    global _cache
    if _cache is not None:
        return _cache

    df = pd.read_csv(DATA_PATH, parse_dates=["Timestamp"])
    df = df.rename(columns={
        "Timestamp":        "timestamp",
        "Sales Count":      "sales_count",
        "Redemption Count": "redemption_count",
    })
    df = df.sort_values("timestamp").reset_index(drop=True)

    df["total_activity"]  = df["sales_count"] + df["redemption_count"]
    df["rpr"]             = (df["redemption_count"] / (df["sales_count"] + 1)).round(4)

    cap = df["total_activity"].quantile(0.99)
    df["oli"] = (df["total_activity"] / cap).clip(0, 1).round(4)

    df["hour"]        = df["timestamp"].dt.hour
    df["minute"]      = df["timestamp"].dt.minute
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["month"]       = df["timestamp"].dt.month
    df["year"]        = df["timestamp"].dt.year
    df["is_weekend"]  = df["day_of_week"] >= 5

    month_to_season = {1:"Off-season",2:"Off-season",3:"Off-season",
                       4:"Shoulder",5:"Shoulder",
                       6:"Summer",7:"Summer",8:"Summer",
                       9:"Shoulder",10:"Shoulder",
                       11:"Off-season",12:"Off-season"}
    df["season"] = df["month"].map(month_to_season)

    _cache = df
    return df


def filter_data(df: pd.DataFrame, year=None, season=None) -> pd.DataFrame:
    if year is not None:
        df = df[df["year"] == year]
    if season == "Summer":
        df = df[df["season"] == "Summer"]
    elif season == "Off-season":
        df = df[df["season"] == "Off-season"]
    elif season == "Shoulder":
        df = df[df["season"] == "Shoulder"]
    return df


def resample_df(df: pd.DataFrame, gran: str) -> pd.DataFrame:
    df2 = df.set_index("timestamp")
    agg = {"sales_count":"sum","redemption_count":"sum",
           "total_activity":"sum","rpr":"mean","oli":"mean"}
    rule = {"15min": None, "H": "h", "D": "D"}.get(gran)
    if rule is None:
        return df2.reset_index()
    return df2[list(agg)].resample(rule).agg(agg).reset_index()
