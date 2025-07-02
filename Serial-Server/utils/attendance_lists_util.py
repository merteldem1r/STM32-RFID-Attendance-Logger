import time
import pandas as pd
import os

time_in_secs = time.time()
# current_time_full_day = time.ctime(time_in_secs)
current_day = time.strftime("%d", time.gmtime(time_in_secs))
current_month = time.strftime("%m", time.gmtime(time_in_secs))
current_year = time.strftime("%Y", time.gmtime(time_in_secs))

full_date = f"{current_day}" + "-" + f"{current_month}" + "-" + f"{current_year}"

print(full_date)

PATH_AL:str = f"../Database/attendance_lists/{full_date}.csv"


def create_attendance_list():
    if not os.path.exists(PATH_AL):
        field_names = ["card_uid", "user_name", "user_id", "last_log_date", "total_reads"]
        df = pd.DataFrame(columns=field_names)
        os.makedirs("./attendance_lists", exist_ok=True)
        df.to_csv(PATH_AL, index=False)
        
        # print created list path
        path_slice_indez =PATH_AL.rfind('/') 
        if path_slice_indez != -1:
            print(f"List created: {PATH_AL[path_slice_indez + 1:]}")
        
def update_attendance_list(card_uid_str: str, user_name: str, user_id: str):
    df = pd.read_csv(PATH_AL, sep=",", engine="python")
    df = df.dropna(how="all")

    new_time = time.strftime("%d.%m.%Y %I:%M", time.localtime())
    
    if card_uid_str not in df["card_uid"].values:
        new_row = pd.DataFrame([{
            "card_uid": card_uid_str,
            "user_name": f"{user_name}",
            "user_id": f"{user_id}",
            "last_log_date": new_time, 
            "total_reads": 0
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(PATH_AL, index=False)
        
    if card_uid_str in df["card_uid"].values:
        current_time_full_day = time.ctime(time_in_secs)
        df.loc[df["card_uid"] == card_uid_str, "total_reads"] += 1
        df.loc[df["card_uid"] == card_uid_str, "last_log_date"] = new_time
        df.to_csv(PATH_AL, index=False)
        
        print(f"Attendance Logged, User: '{user_name}' Time: '{new_time}'", )