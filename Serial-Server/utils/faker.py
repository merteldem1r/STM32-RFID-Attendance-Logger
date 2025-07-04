import os
import random
import pandas as pd
from typing import List
from datetime import datetime, timedelta
import calendar


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
    uid_str: str = ""
    uid_arr: List[str] = []

    while True:
        for i in range(4):
            first_indx = random.randint(0, len(hex_digits) - 1)
            second_indx = random.randint(0, len(hex_digits) - 1)
            hex_num = f"{hex_digits[first_indx]}{hex_digits[second_indx]}"
            uid_arr.append(hex_num)

        uid_str = " ".join(uid_arr)
        if uid_str not in df["card_uid"].values:
            return uid_str


def random_user_id():
    user_id_arr: List[str] = []

    for i in range(9):
        user_id_arr.append(str(random.randint(1, 9)))

    return "".join(user_id_arr)


def random_uid_db():
    df = pd.read_csv(PATH_DB, sep=",", engine="python")

    for user in fake_users:
        user_uid = random_uid()
        user_id = random_user_id()

        new_row = pd.DataFrame([{
            "card_uid": user_uid,
            "user_name": user,
            "user_id": user_id
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(PATH_DB, index=False)

# random_uid_db()


def random_time() -> str:
    hour = random.randint(10, 18)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"


def random_attendance_list(year: int, num_lists: int, min_max_interval: List[int], total_read_interval: List[int]):
    for _ in range(num_lists):
        random_month = random.randint(1, 12)
        day_count = calendar.monthrange(year, random_month)[1]
        random_day = random.randint(1, day_count)

        attentance_date: str = f"{random_day:02}-{random_month:02}-{year}"

        NEW_ATTENDANCE_PATH: str = f"../../Database/attendance_lists/{attentance_date}.csv"

        if os.path.exists(NEW_ATTENDANCE_PATH):
            continue

        # create new attendance list
        os.makedirs("./attendance_lists", exist_ok=True)

        field_names = ["card_uid", "user_name",
                       "user_id", "last_log_date", "total_reads"]
        df = pd.DataFrame(columns=field_names)
        df.to_csv(NEW_ATTENDANCE_PATH, index=False)

        # read uid.csv to pick random users
        df_db = pd.read_csv(PATH_DB, sep=",", engine="python")
        uid_list = df_db.values.tolist()

        # attendace csv
        df_attendance = pd.read_csv(
            NEW_ATTENDANCE_PATH, sep=",", engine="python")
        df_attendance = df.dropna(how="all")

        user_count = random.randint(min_max_interval[0], min_max_interval[1])
        print("user_count ", user_count)

        if user_count >= len(uid_list):
            print("wrong user count")
            return

        random_user_arr = random.sample(uid_list, user_count)
        last_log_date = attentance_date.replace("-", ".")

        # filling the attendance list with random users
        for random_user in random_user_arr:
            card_uid, user_name, user_id = random_user
            print("random_user", random_user)

            time = random_time()
            random_last_log_date = f"{last_log_date} {time}"

            new_row = pd.DataFrame([{
                "card_uid": card_uid,
                "user_name": user_name,
                "user_id": user_id,
                "last_log_date": random_last_log_date,
                "total_reads": random.randint(total_read_interval[0], total_read_interval[1])
            }])
            df_attendance = pd.concat(
                [df_attendance, new_row], ignore_index=True)
            df_attendance.to_csv(NEW_ATTENDANCE_PATH, index=False)


random_attendance_list(2025, 5, (3, 7), (1, 7))
