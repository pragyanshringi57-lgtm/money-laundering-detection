from __future__ import annotations

from final_flagging import run_final_flagging_pipeline


def main() -> None:
    final_report = run_final_flagging_pipeline()
    if final_report.empty:
        print("No flagged transactions were produced by the pipeline.")
        return

    print(final_report.to_string(index=False))


if __name__ == "__main__":
    main()
