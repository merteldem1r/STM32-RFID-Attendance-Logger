import csv

def Initialize_DB():
    with open ("./db/uid.csv", "w", newline="") as csvfile:
        field_names = ["card_uid", "user_name", "user_id"]
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        
        
def save_db(card_uid_str: str):
    # check DB if exists
    
    # if not appeng to the DB
    
    user_dict = [{"card_uid": f"{card_uid_str}",
                    "user_name": "", "user_id": ""}]
    field_names = ["card_uid", "user_name", "user_id"]
    saved_card_uid_list = []
    
    with open("./db/uid.csv") as csv_file:
        file = csv.DictReader(csv_file)
        for col in file:
            saved_card_uid_list.append(col['card_uid'])
    
    if card_uid_str not in saved_card_uid_list:
        with open("./db/uid.csv", "a") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writerows(user_dict)
            saved_card_uid_list.append(card_uid_str)

