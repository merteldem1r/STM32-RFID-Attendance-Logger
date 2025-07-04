import os
import random
import pandas as pd
from typing import List
from datetime import datetime, timedelta
import calendar


class RandomCSVData:
    PATH_DB = "../../Database/uid.csv"
    fake_users = [
        "Samuel Turner", "Jane Smith", "Alice Johnson", "Bob Brown", "Charlie Davis", "Diana Miller", "Edward Wilson", "Fiona Clark", "George Lewis", "Hannah Young", "Ian Walker", "Julia Hall", "Kevin Allen", "Laura King", "Michael Scott"
    ]
    hex_digits = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "A", "B", "C", "D", "E", "F"
    ]

    def __init__(self, year: int, month: int, attendance_list_count: int, min_max_users: List[int], user_total_read_interval: List[int]):
        self.year = year
        self.month = month
        self.attendance_list_count = attendance_list_count
        self.min_max_users = min_max_users
        self.user_total_read_interval = user_total_read_interval

    # PRIVATE METHODS

    def __random_card_uid(self, existing_uids) -> str:
        uid_str: str = ""
        uid_arr: List[str] = []

        while True:
            for i in range(4):
                first_indx = random.randint(
                    0, len(self.hex_digits) - 1)
                second_indx = random.randint(
                    0, len(self.hex_digits) - 1)
                hex_num = f"{self.hex_digits[first_indx]}{self.hex_digits[second_indx]}"

                uid_arr.append(hex_num)

            uid_str = " ".join(uid_arr)
            if uid_str not in existing_uids:
                return uid_str

    def __random_user_id(self):
        user_id_arr: List[str] = []

        for i in range(9):
            user_id_arr.append(str(random.randint(1, 9)))

        return "".join(user_id_arr)

    def __random_time(self) -> str:
        hour = random.randint(10, 18)
        minute = random.randint(0, 59)
        return f"{hour:02d}:{minute:02d}"

    def __random_attendance_list_date(self) -> str:
        random_month = random.randint(
            1, 12) if self.month == None else self.month
        day_count = calendar.monthrange(self.year, random_month)[1]
        random_day = random.randint(1, day_count)

        attentance_date: str = f"{random_day:02}-{random_month:02}-{self.year}"

        return attentance_date

    # Read uid.csv to pick random users
    def __pick_random_users_from_db(self) -> List[List[str]]:
        if not os.path.exists(self.PATH_DB):
            print("uid.csv is not found")
            return

        df = pd.read_csv(self.PATH_DB, sep=",", engine="python")
        uid_list = df.values.tolist()

        user_count = random.randint(
            self.min_max_users[0], self.min_max_users[1])

        if user_count >= len(uid_list):
            print("Wrong user count")
            return

        random_user_arr = random.sample(uid_list, user_count)

        return random_user_arr

    # generate new list and return attendance list date to use for path and last_log_date
    def __generate_random_attendance_list(self) -> str:
        attendance_list_date = self.__random_attendance_list_date()
        attendance_list_path: str = f"../../Database/attendance_lists/{attendance_list_date}.csv"

        if os.path.exists(attendance_list_path):
            return

        # create new attendance list
        os.makedirs("../../Database/attendance_lists", exist_ok=True)
        field_names = ["card_uid", "user_name",
                       "user_id", "last_log_date", "total_reads"]
        df = pd.DataFrame(columns=field_names)
        df.to_csv(attendance_list_path, index=False)

        return attendance_list_date

    # PUBLIC METHODS (use only these methods outside of class)

    # To fill up uid.csv with random users if needed
    def generate_random_users_in_db(self):
        if not os.path.exists(self.PATH_DB):
            print("uid.csv is not found")
            return

        df = pd.read_csv(self.PATH_DB, sep=",", engine="python")
        existing_uids = df["card_uid"].values
        new_user_rows: List[dict] = []

        for user in self.fake_users:
            card_uid = self.__random_card_uid(existing_uids)
            user_id = self.__random_user_id()

            new_user_rows.append({
                "card_uid": card_uid,
                "user_name": user,
                "user_id": user_id
            })

        df = pd.concat([df, pd.DataFrame(new_user_rows)], ignore_index=True)
        df.to_csv(self.PATH_DB, index=False)

    # Complete function to generate multiple random attendance lists with random users and data inside
    def generate_random_attendance_lists(self):
        for _ in range(self.attendance_list_count):
            # generate new list
            generated_attendance_list_date = self.__generate_random_attendance_list()
            generated_attendance_list_path = f"../../Database/attendance_lists/{generated_attendance_list_date}.csv"

            # read generated attendace csv file
            df_attendance = pd.read_csv(
                generated_attendance_list_path, sep=",", engine="python")
            df_attendance = df_attendance.dropna(how="all")

            # filling the attendance list with random users
            random_users_arr = self.__pick_random_users_from_db()
            last_log_date = generated_attendance_list_date.replace("-", ".")

            new_attendance_rows: List[dict] = []

            for random_user in random_users_arr:
                card_uid, user_name, user_id = random_user
                time = self.__random_time()
                last_log_date_colum = f"{last_log_date} {time}"

                new_attendance_rows.append({
                    "card_uid": card_uid,
                    "user_name": user_name,
                    "user_id": user_id,
                    "last_log_date": last_log_date_colum,
                    "total_reads": random.randint(self.user_total_read_interval[0], self.user_total_read_interval[1])
                })

            df_attendance = pd.concat(
                [df_attendance, pd.DataFrame(new_attendance_rows)], ignore_index=True)
            df_attendance.to_csv(generated_attendance_list_path, index=False)


"""
For what (__name__ == "__main__") is used:
  - If you run this file directly, it generates the lists.
  - If you import RandomCSVData from another script, it won’t run automatically — it just provides the class.
"""
if __name__ == "__main__":
    # Example 1 WITH specifying month
    RandomLists = RandomCSVData(year=2024, month=2, attendance_list_count=5, min_max_users=[
                                4, 12], user_total_read_interval=[1, 4])
    RandomLists.generate_random_attendance_lists()

    # Example 2 WITHOUT specifying month
    RandomLists2 = RandomCSVData(year=2023, month=None, attendance_list_count=7, min_max_users=[
        4, 12], user_total_read_interval=[1, 4])
    RandomLists2.generate_random_attendance_lists()
