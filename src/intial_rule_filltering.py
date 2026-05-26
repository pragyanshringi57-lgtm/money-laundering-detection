from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd
def generate_transactions(n=500, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    accounts = [f"ACC{str(i).zfill(4)}" for i in range(1, 51)]
    transaction_types = ["TRANSFER", "WITHDRAWAL", "DEPOSIT", "PAYMENT"]
    countries = ["IN", "US", "UK", "AE", "SG", "NG", "PK", "IR"]

    base_date = datetime(2024, 1, 1)
    records = []

    for i in range(n):
        sender = random.choice(accounts)
        receiver = random.choice([a for a in accounts if a != sender])
        txn_date = base_date + timedelta(days=random.randint(0, 90),
                                         hours=random.randint(0, 23),
                                         minutes=random.randint(0, 59))
        amount = round(np.random.lognormal(mean=9, sigma=1.5), 2)
        country = random.choice(countries)
        txn_type = random.choice(transaction_types)

        records.append({
            "txn_id":       f"TXN{str(i+1).zfill(5)}",
            "sender_id":    sender,
            "receiver_id":  receiver,
            "amount":       amount,
            "currency":     "INR",
            "txn_type":     txn_type,
            "country":      country,
            "timestamp":    txn_date,
            "is_dormant":   False,
        })

    df = pd.DataFrame(records)

    # ── Inject suspicious patterns ──────────────

    # Pattern A: Structuring — many txns just below ₹10L threshold
    for j in range(20):
        idx = random.randint(0, len(df) - 1)
        df.at[idx, "amount"]    = round(random.uniform(950000, 999999), 2)
        df.at[idx, "sender_id"] = "ACC0001"

    # Pattern B: Large single transactions above ₹10L
    for j in range(10):
        idx = random.randint(0, len(df) - 1)
        df.at[idx, "amount"]    = round(random.uniform(1_000_001, 5_000_000), 2)
        df.at[idx, "sender_id"] = "ACC0002"

    # Pattern C: Round number transactions
    for j in range(15):
        idx = random.randint(0, len(df) - 1)
        df.at[idx, "amount"] = random.choice(
            [50000, 100000, 200000, 500000, 1000000]
        )

    # Pattern D: High velocity — many txns from one account in one day
    burst_date = base_date + timedelta(days=10)
    for j in range(25):
        df = pd.concat([df, pd.DataFrame([{
            "txn_id":      f"TXN_BURST_{j}",
            "sender_id":   "ACC0003",
            "receiver_id": random.choice(accounts),
            "amount":      round(random.uniform(5000, 50000), 2),
            "currency":    "INR",
            "txn_type":    "TRANSFER",
            "country":     "IN",
            "timestamp":   burst_date + timedelta(hours=j % 24, minutes=j*2),
            "is_dormant":  False,
        }])], ignore_index=True)

    # Pattern E: Dormant account suddenly active
    dormant_date = base_date + timedelta(days=80)
    for j in range(5):
        df = pd.concat([df, pd.DataFrame([{
            "txn_id":      f"TXN_DORM_{j}",
            "sender_id":   "ACC0050",
            "receiver_id": random.choice(accounts),
            "amount":      round(random.uniform(100000, 800000), 2),
            "currency":    "INR",
            "txn_type":    "TRANSFER",
            "country":     "AE",
            "timestamp":   dormant_date + timedelta(hours=j),
            "is_dormant":  True,
        }])], ignore_index=True)

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def threshold(df: pd.DataFrame) -> pd.DataFrame:
	threshold_value = 1000000
	flag = df[df["amount"] > threshold_value]
	return flag


def struc(df: pd.DataFrame) -> pd.Series:
	stru_thre = 900000
	trans_limit = 3

	# 1. Filter the dataframe to only include rows where amount > 900000
	high_amount_df = df[df["amount"] > stru_thre]

	# 2. Group the filtered dataframe by sender_id and count the occurrences
	# (.size() is generally better than .count() here as it counts rows regardless of NaNs)
	flags = high_amount_df.groupby("sender_id").size()

	# 3. Filter to only include senders who exceed the limit
	flag = flags[flags > trans_limit]

	return flag


def dorm(df: pd.DataFrame) -> pd.Series:
	dfd = df[df["is_dormant"] == True]
	flag = dfd.groupby("sender_id").size()
	flag = flag[flag > 3]
	return flag


def multiple_dormant_transactions(df: pd.DataFrame, trans_limit: int = 1) -> pd.Series:
    # 1. Keep only transactions coming from accounts marked as dormant.
    dormant_df = df[df["is_dormant"] == True]

    # 2. Count how many dormant transactions each sender made.
    dormant_counts = dormant_df.groupby("sender_id").size()

    # 3. Flag senders that made more than one dormant transaction.
    flagged_senders = dormant_counts[dormant_counts > trans_limit]

    return flagged_senders


def flag_same_round_trans(df: pd.DataFrame) -> pd.DataFrame:
	# 1. Define the round numbers
	rn = [10000, 50000, 100000, 500000, 1000000]

	# 2. Filter the dataframe to only include these round numbers
	dfr = df[df["amount"].isin(rn)]

	# 3. Find rows where BOTH the 'sender_id' and the 'amount' are identical to another row.
	# keep=False tells pandas to flag ALL copies of the duplicate (the 1st, 2nd, 3rd occurrence, etc.)
	duplicate_mask = dfr.duplicated(subset=["sender_id", "amount"], keep=False)

	# 4. Filter and return only the matching rows
	final_flagged_rows = dfr[duplicate_mask]

	return final_flagged_rows


def main() -> None:
    df = generate_transactions()
    print(df.head())
    print(threshold(df))
    print(struc(df))
    print(dorm(df))
    print(multiple_dormant_transactions(df))
    print(flag_same_round_trans(df))


if __name__ == "__main__":
	main()
