import serial
import pandas as pd
import os

PATH = "./db/uid.csv"


def Initialize_DB():
    if not os.path.exists(PATH) or os.stat(PATH).st_size == 0:
        field_names = ["card_uid", "user_name", "user_id"]
        df = pd.DataFrame(columns=field_names)
        os.makedirs("./db", exist_ok=True)
        df.to_csv(PATH, index=False)


def send_message(ser: serial.Serial, message: str):
    ser.write(message.encode('utf-8'))


def fix_csv_if_broken():
    expected_columns = ["card_uid", "user_name", "user_id"]

    if not os.path.exists(PATH) or os.stat(PATH).st_size == 0:
        print("CSV is empty or missing. Wait fot reinitializing.")
        Initialize_DB()
        return

    # try:
    #     df = pd.read_csv(PATH, sep=",", engine="python")
    # except pd.errors.EmptyDataError:
    #     print("CSV is empty. Wait fot reinitializing.")
    #     Initialize_DB()
    #     return

    df = pd.read_csv(PATH, sep=",", engine="python")

    for ex_col in expected_columns:
        if not ex_col in df.columns:
            print("CSV header is invalid. Wait for fixing.")
            df.columns = expected_columns
            df.to_csv(PATH, index=False)
            break


def save_db(ser: serial.Serial, card_uid_str: str):
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


def read_db(ser: serial.Serial, card_uid_str: str):
    fix_csv_if_broken()

    df = pd.read_csv(PATH, sep=",", engine="python")
    df = df.dropna(how="all")

    if card_uid_str in df["card_uid"].values:
        row = df[df["card_uid"] == card_uid_str].iloc[0]
        
        user_name = str(row["user_name"]).strip() if pd.notna(row["user_name"]) else ""
        user_id = str(round(row["user_id"])).strip() if pd.notna(row["user_id"]) else ""
        
        message_toSend = f"{user_name}-{user_id}\n"

        if not user_name and not user_id:
            message_toSend = "ERR\n"

    else:
        message_toSend = "ERR\n"

    print(f"Sending to STM32: {message_toSend.strip()}")
    send_message(ser, message_toSend)
    
    
