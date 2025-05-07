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
    
        
def save_db(card_uid_str: str):
    if not os.path.exists(PATH):
        Initialize_DB()
        
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
               
        
def send_message(ser, message):
    # saved_text = "OK\n"
    # ser.write(saved_text.encode('utf-8'))
    ser.write(message.encode('utf-8'))
    

def read_db(ser, card_uid_str: str):
    if not os.path.exists(PATH):
        Initialize_DB()
        
    df = pd.read_csv(PATH, sep=",", engine="python")
    df = df.dropna(how="all")
    
    if card_uid_str in df["card_uid"].values:
        row = df[df["card_uid"] == card_uid_str].iloc[0]
        user_name = str(row["user_name"]).strip()
        user_id = str(row["user_id"]).strip()

        if user_name and user_id:
            message_toSend = f"{user_name}-{user_id}\n"
        else:
            message_toSend = "ERR\n"
    else:
        message_toSend = "ERR\n"

    send_message(ser, message_toSend)
        
    