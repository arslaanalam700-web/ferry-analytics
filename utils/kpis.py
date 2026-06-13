import numpy as np
import pandas as pd
from utils.data_generator import filter_data


def compute_kpis(df, year_filter=None, season_filter=None,
                 congestion_thresh=0.75, idle_thresh=0.20):
    """Compute all KPIs. Always use keyword arguments when calling."""
    fd = filter_data(df, year_filter, season_filter)
    if fd.empty:
        return {k: 0 for k in ["avg_oli","peak_oli","congestion_pct","idle_pct",
                                "variability","total_sales","total_redemptions",
                                "total_activity","avg_rpr","peak_strain_hours"]}
    oli = fd["oli"].values
    return {
        "avg_oli":           float(np.mean(oli)),
        "peak_oli":          float(np.max(oli)),
        "congestion_pct":    float(np.mean(oli > congestion_thresh) * 100),
        "idle_pct":          float(np.mean(oli < idle_thresh) * 100),
        "variability":       float(np.std(oli)),
        "total_sales":       int(fd["sales_count"].sum()),
        "total_redemptions": int(fd["redemption_count"].sum()),
        "total_activity":    int(fd["total_activity"].sum()),
        "avg_rpr":           float(fd["rpr"].mean()),
        "peak_strain_hours": int(np.sum(oli > congestion_thresh) / 4),
    }
