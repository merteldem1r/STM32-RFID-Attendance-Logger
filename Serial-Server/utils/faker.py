import os
import random
import pandas as pd
from typing import List
from datetime import datetime, timedelta


fake_users = [
    "Samuel Turner", 
    "Jane Smith", 
    "Alice Johnson", 
    "Bob Brown", 
    "Charlie Davis",
    "Diana Miller", 
    "Edward Wilson", 
    "Fiona Clark", 
    "George Lewis", 
    "Hannah Young",
    "Ian Walker", 
    "Julia Hall", 
    "Kevin Allen", 
    "Laura King", 
    "Michael Scott"
]

hex_digits = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "A", "B", "C", "D", "E", "F"
]

PATH_DB = "../../Database/uid.csv"


def random_uid() -> str:
    df = pd.read_csv(PATH_DB, sep=",", engine="python")
    while True:
        uid_arr = [f"{random.choice(hex_digits)}{random.choice(hex_digits)}" for _ in range(4)]
        uid_str = " ".join(uid_arr)
        if uid_str not in df["card_uid"].values:
            return uid_str


def random_user_id() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(9))


def random_time() -> str:
    hour = random.randint(10, 18)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"


def generate_attendance_for_date(attendance_date: datetime.date,
                                 user_count: int = 9,
                                 total_read_interval: List[int] = [1, 6]):

    date_str = attendance_date.strftime("%d-%m-%Y")
    output_path = f"../../Database/attendance_lists/{date_str}.csv"

    if os.path.exists(output_path):
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_att = pd.DataFrame(columns=["card_uid", "user_name", "user_id", "last_log_date", "total_reads"]);
    df_att.to_csv(output_path, index=False)

    df_uids = pd.read_csv(PATH_DB, sep=",", engine="python")
    uid_list = df_uids.values.tolist()
    picked = set()

    while len(picked) < user_count:
        idx = random.randint(0, len(uid_list) - 1)
        if idx in picked:
            continue
        picked.add(idx)
        card_uid, user_name, user_id = uid_list[idx]

        date_for_log = attendance_date.strftime("%d.%m.%Y")
        time_str = random_time()
        last_log_date = f"{date_for_log} {time_str}"
        total_reads = random.randint(total_read_interval[0], total_read_interval[1])

        new_row = pd.DataFrame([{
            "card_uid": card_uid,
            "user_name": user_name,
            "user_id": user_id,
            "last_log_date": last_log_date,
            "total_reads": total_reads
        }])
        df_att = pd.concat([df_att, new_row], ignore_index=True)
        df_att.to_csv(output_path, index=False)


def generate_random_attendance_lists(num_lists: int = 15,
                                     start_date_str: str = "01-01-2023",
                                     end_date_str: str = "31-12-2025",
                                     min_users: int = 1,
                                     max_users: int = None):
  
    start_date = datetime.strptime(start_date_str, "%d-%m-%Y").date()
    end_date = datetime.strptime(end_date_str, "%d-%m-%Y").date()
    delta_days = (end_date - start_date).days

    if max_users is None:
        max_users = len(fake_users)

    dates = set()
    while len(dates) < num_lists:
        rand_days = random.randint(0, delta_days)
        dates.add(start_date + timedelta(days=rand_days))

    for dt in sorted(dates):
        user_count = random.randint(min_users, max_users)
        generate_attendance_for_date(dt, user_count=user_count)


if __name__ == "__main__":
    generate_random_attendance_lists()
