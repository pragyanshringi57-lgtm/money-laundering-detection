from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from supervised import run_supervised_pipeline


FINAL_DISPLAY_COLUMNS = [
    "txn_id",
    "sender_id",
    "receiver_id",
    "amount",
    "timestamp",
    "txn_type",
    "country",
    "anomaly_score",
    "business_risk_tier",
    "primary_reason",
]


def build_final_report(scored_transactions: pd.DataFrame) -> pd.DataFrame:
    """Keep only the rows the Isolation Forest marked as actionable."""
    if scored_transactions.empty:
        return scored_transactions.copy()

    report = scored_transactions.copy()

    if "raw_anomaly_score" in report.columns and "anomaly_score" not in report.columns:
        report["anomaly_score"] = report["raw_anomaly_score"]

    if "business_risk_tier" in report.columns:
        report["is_flagged"] = report["business_risk_tier"].isin(
            ["High Alert", "Monitor"]
        ).astype(int)
    else:
        report["is_flagged"] = 0

    flagged = report[report["is_flagged"] == 1].copy()
    if flagged.empty:
        return flagged

    available_columns = [col for col in FINAL_DISPLAY_COLUMNS if col in flagged.columns]

    sort_column = "anomaly_score" if "anomaly_score" in flagged.columns else None
    if sort_column is not None:
        flagged = flagged.sort_values(by=sort_column, ascending=True)

    return flagged[available_columns].reset_index(drop=True)


def run_final_flagging_pipeline() -> pd.DataFrame:
    """Run the full AML pipeline and return the final flagged transaction report."""
    scored_transactions = run_supervised_pipeline()
    return build_final_report(scored_transactions)


def main() -> None:
    final_report = run_final_flagging_pipeline()

    if final_report.empty:
        print("No flagged transactions were produced by the pipeline.")
        return

    print(final_report.to_string(index=False))


if __name__ == "__main__":
    main()