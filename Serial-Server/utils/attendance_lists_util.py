import time
import pandas as pd
import os

time_in_secs = time.time()
current_time_full_day = time.ctime(time_in_secs)
current_day = time.strftime("%d", time.gmtime(time_in_secs))
current_month = time.strftime("%b", time.gmtime(time_in_secs))
current_year = time.strftime("%Y", time.gmtime(time_in_secs))

full_date = f"{current_day}" + "-" + f"{current_month}" + "-" + f"{current_year}"

print(full_date)

PATH_AL = f"./attendance_lists/{full_date}.csv"


def create_attendance_list():
    if not os.path.exists(PATH_AL):
        field_names = ["card_uid", "user_name", "user_id", "last_log_date", "total_reads"]
        df = pd.DataFrame(columns=field_names)
        os.makedirs("./attendance_lists", exist_ok=True)
        df.to_csv(PATH_AL, index=False)
        
def update_attendance_list(card_uid_str: str, user_name, user_id):
    df = pd.read_csv(PATH_AL, sep=",", engine="python")
    df = df.dropna(how="all")

    if card_uid_str not in df["card_uid"].values:
        counter = 0
        new_row = pd.DataFrame([{
            "card_uid": card_uid_str,
            "user_name": f"{user_name}",
            "user_id": f"{user_id}",
            "last_log_date": f"{current_time_full_day}", 
            "total_reads": counter
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(PATH_AL, index=False)
        
    if card_uid_str in df["card_uid"].values:
        df.loc[df["card_uid"] == card_uid_str, "total_reads"] += 1
        df.loc[df["card_uid"] == card_uid_str, "last_log_date"] = current_time_full_day
        df.to_csv(PATH_AL, index=False)