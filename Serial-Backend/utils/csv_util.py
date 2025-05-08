import pandas as pd
import os

PATH = "./db/uid.csv"

def Initialize_DB():
    if os.path.exists(PATH):
        return
    
    field_names = ["card_uid", "user_name", "user_id"]
    df = pd.DataFrame(columns=field_names)
    os.makedirs("./db", exist_ok=True)
    df.to_csv(PATH, index=False)
    
    
def send_message(ser, message):
    ser.write(message.encode('utf-8'))

    
def fix_csv_if_broken():
    expected_columns = ["card_uid", "user_name", "user_id"]
    
    if not os.path.exists(PATH) or os.stat(PATH).st_size == 0:
        print("CSV is empty or missing. Wait fot reinitializing.")
        Initialize_DB()
        return

    try:
        df = pd.read_csv(PATH, sep=",", engine="python")
    except pd.errors.EmptyDataError:
        print("CSV is empty. Wait fot reinitializing.")
        Initialize_DB()
        return

    if not all(col in df.columns for col in expected_columns):
        print("CSV header is invalid. Wait for fixing.")
        df.columns = expected_columns[:len(df.columns)] + [""] * (len(expected_columns) - len(df.columns))
        df.to_csv(PATH, index=False)

        
def save_db(ser, card_uid_str: str):
    Initialize_DB()
    fix_csv_if_broken()
        
    df = pd.read_csv(PATH, sep=",", engine="python")
    df = df.dropna(how="all")
    
    if card_uid_str not in df["card_uid"].values:
        new_row = pd.DataFrame([{
            "card_uid": card_uid_str,
            "user_name": "",
            "user_id": ""
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(PATH, index=False)
        message_toSend = "OK\n"
        send_message(ser, message_toSend)     


def read_db(ser, card_uid_str: str):
    Initialize_DB()
    fix_csv_if_broken()
        
    df = pd.read_csv(PATH, sep=",", engine="python")
    df = df.dropna(how="all")
    
    if card_uid_str in df["card_uid"].values:
        row = df[df["card_uid"] == card_uid_str].iloc[0]
        user_name = str(row["user_name"]).strip() if pd.notna(row["user_name"]) else None
        user_id = str(round(row["user_id"])).strip() if pd.notna(row["user_id"]) else None
        if user_name and user_id:
            message_toSend = f"{user_name}-{user_id}\n"
        elif user_name:
            message_toSend = f"{user_name}-None\n"
        elif user_id:
            message_toSend = f"None-{user_id}\n"
        else:
            message_toSend = "ERR\n"
    else:
        message_toSend = "ERR\n"

    print(f"Sending to STM32: {message_toSend.strip()}")
    send_message(ser, message_toSend)
        
    