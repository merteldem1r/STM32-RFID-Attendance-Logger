import serial
import pandas as pd
import os
from utils import attendance_lists_util
import threading


PATH_DB = "./db/uid.csv"


def Initialize_DB():
    if not os.path.exists(PATH_DB) or os.stat(PATH_DB).st_size == 0:
        field_names = ["card_uid", "user_name", "user_id"]
        df = pd.DataFrame(columns=field_names)
        os.makedirs("./db", exist_ok=True)
        df.to_csv(PATH_DB, index=False)


def send_serial_message(ser: serial.Serial, response_mode: str, message: str, lock: threading.Lock = None):
    if lock:
        with lock:
            message_str = f"{response_mode}|{message}\n"
            ser.write(message_str.encode('utf-8'))
            print("Sent to STM32: ", message_str)
    else:
        ser.write(message.encode('utf-8'))


def fix_csv_if_broken():
    expected_columns = ["card_uid", "user_name", "user_id"]

    if not os.path.exists(PATH_DB) or os.stat(PATH_DB).st_size == 0:
        print("CSV is empty or missing. Wait fot reinitializing.")
        Initialize_DB()
        return

    # try:
    #     df = pd.read_csv(PATH_DB, sep=",", engine="python")
    # except pd.errors.EmptyDataError:
    #     print("CSV is empty. Wait fot reinitializing.")
    #     Initialize_DB()
    #     return

    df = pd.read_csv(PATH_DB, sep=",", engine="python")

    for ex_col in expected_columns:
        if not ex_col in df.columns:
            print("CSV header is invalid. Wait for fixing.")
            df.columns = expected_columns
            df.to_csv(PATH_DB, index=False)
            break


def save_db(ser: serial.Serial, card_uid_str: str, lock=None):
    fix_csv_if_broken()

    df = pd.read_csv(PATH_DB, sep=",", engine="python")
    df = df.dropna(how="all")

    message_to_send = ""

    if card_uid_str not in df["card_uid"].values:
        new_row = pd.DataFrame([{
            "card_uid": card_uid_str,
            "user_name": "",
            "user_id": ""
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(PATH_DB, index=False)
        message_to_send = "OK"
    else:
        message_to_send = "DUP"  # duplicate

    send_serial_message(ser, "S", message_to_send, lock)


def read_db(ser: serial.Serial, card_uid_str: str, lock=None):
    fix_csv_if_broken()
    attendance_lists_util.create_attendance_list()

    df = pd.read_csv(PATH_DB, sep=",", engine="python")
    df = df.dropna(how="all")

    message_to_send = ""

    if card_uid_str in df["card_uid"].values:
        row = df[df["card_uid"] == card_uid_str].iloc[0]

        user_name = str(row["user_name"]).strip(
        ) if pd.notna(row["user_name"]) else ""
        user_id = str(round(row["user_id"])).strip(
        ) if pd.notna(row["user_id"]) else ""

        if user_name and user_id:
            message_to_send = f"{user_name}-{user_id}"
            attendance_lists_util.update_attendance_list(
                card_uid_str, user_name, user_id)
        else:
            message_to_send = "ERR"
    else:
        message_to_send = "ERR"

    send_serial_message(ser, "R", message_to_send, lock)
