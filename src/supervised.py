from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from intial_rule_filtering import (
    dorm,
    flag_same_round_trans,
    generate_transactions,
    multiple_dormant_transactions,
    struc,
    threshold,
)
from random_forest_model_flagging import AMLRiskWrapper


def build_rule_filtered_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Combine the rule-based outputs into a single candidate transaction set."""
    flagged_frames = [
        threshold(df),
        flag_same_round_trans(df),
    ]

    flagged_senders = set(struc(df).index)
    flagged_senders.update(dorm(df).index)
    flagged_senders.update(multiple_dormant_transactions(df).index)

    if flagged_senders:
        flagged_frames.append(df[df["sender_id"].isin(flagged_senders)])

    combined = pd.concat(flagged_frames, ignore_index=False).drop_duplicates()
    return combined.sort_values("timestamp").reset_index(drop=True)


def prepare_model_features(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the transaction table into a numeric feature matrix for the forest."""
    feature_frame = df.copy()
    feature_frame["timestamp"] = pd.to_datetime(feature_frame["timestamp"])
    feature_frame["hour"] = feature_frame["timestamp"].dt.hour
    feature_frame["day_of_week"] = feature_frame["timestamp"].dt.dayofweek
    feature_frame["month"] = feature_frame["timestamp"].dt.month
    feature_frame["is_dormant"] = feature_frame["is_dormant"].astype(int)

    feature_frame = pd.get_dummies(
        feature_frame[
            [
                "amount",
                "is_dormant",
                "hour",
                "day_of_week",
                "month",
                "txn_type",
                "country",
            ]
        ],
        columns=["txn_type", "country"],
        drop_first=False,
    )

    return feature_frame


def run_supervised_pipeline() -> pd.DataFrame:
    """Run the rule filter first, then score the filtered rows with Isolation Forest."""
    transactions = generate_transactions()
    rule_filtered = build_rule_filtered_transactions(transactions)

    if rule_filtered.empty:
        return pd.DataFrame()

    features = prepare_model_features(rule_filtered)

    model = AMLRiskWrapper(contamination=0.05, random_state=42)
    model.fit(features)
    scored = model.predict_risk_tiers(features)

    return pd.concat([rule_filtered.reset_index(drop=True), scored.reset_index(drop=True)], axis=1)


def main() -> None:
    scored_transactions = run_supervised_pipeline()
    print(scored_transactions)


if __name__ == "__main__":
    main()
