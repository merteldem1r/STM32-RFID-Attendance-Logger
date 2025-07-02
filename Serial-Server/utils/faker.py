import os
import random
import time
import pandas as pd
from typing import List

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

def random_uid():
    # 0B 46 98 25
    uid_str:str = ""
    uid_arr: List[str] = []
    
    for i in range(4):
        first_indx = random.randint(0, len(hex_digits) - 1)
        second_indx = random.randint(0, len(hex_digits) - 1)
        hex_num = f"{hex_digits[first_indx]}{hex_digits[second_indx]}"
        uid_arr.append(hex_num)
        
    uid_str = " ".join(uid_arr)

    df = pd.read_csv(PATH_DB, sep=",", engine="python")
    if uid_str in df["card_uid"].values:
        random_uid()
    
    return uid_str

def random_user_id():
    user_id_arr: List[str] = []
    
    for i in range(9):
        user_id_arr.append(str(random.randint(0, 9)))
        
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
        
def random_time():
    hour = random.randint(10, 18)
    minute = random.randint(0, 59)
    time_str = f"{hour:02d}.{minute:02d}"
    
    return time_str
        
def random_attendance_list():
    # MODIFY below 3 variables on each call to create new attendance list
    attentance_date = "02-06-2025" # random date for attendance list
    user_count = 7 # random user pick count from uid.csv
    total_read_interval = [1, 6] # min, max
    
    NEW_ATTENDANCE_PATH:str = f"../../Database/attendance_lists/{attentance_date}.csv"
    
    if os.path.exists(NEW_ATTENDANCE_PATH):
        return
    
    # create new attendance list
    field_names = ["card_uid", "user_name", "user_id", "last_log_date", "total_reads"]
    df = pd.DataFrame(columns=field_names)
    os.makedirs("./attendance_lists", exist_ok=True)
    df.to_csv(NEW_ATTENDANCE_PATH, index=False)
    
    # read uid.csv to pick random users
    df = pd.read_csv(PATH_DB, sep=",", engine="python")
    uid_list = df.values
    
    picked_indexes: List[int] = []
    
    # filling the attendance list with random users
    while user_count > 0:
        random_index = random.randint(0, len(uid_list) - 1)
        if random_index in picked_indexes:
            continue
        
        picked_user:list = uid_list[random_index]
        
        df = pd.read_csv(NEW_ATTENDANCE_PATH, sep=",", engine="python")
        df = df.dropna(how="all")

        date = attentance_date.replace("-", ".")
        time = random_time()
        
        date_str = f"{date} {time}"
        
        new_row = pd.DataFrame([{
            "card_uid": picked_user[0], # uid
            "user_name": picked_user[1], # user_name
            "user_id": picked_user[2], # user_id
            "last_log_date": date_str, 
            "total_reads": random.randint(total_read_interval[0], total_read_interval[1])
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(NEW_ATTENDANCE_PATH, index=False)

        picked_indexes.append(random_index)
        user_count -= 1
    

random_attendance_list()