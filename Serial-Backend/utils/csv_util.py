import csv


def Initialize_DB():
    with open ("./db/uid.csv", "w", newline="") as csvfile:
        field_names = ["card_uid", "user_name", "user_id"]
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        
        
def save_db(data_list: list[str]):
    card_uid_num = data_list[1:]
    card_uid_str = ' '.join(card_uid_num)
    user_dict = [{"card_uid": f"{card_uid_str}",
                    "user_name": "", "user_id": ""}]
    field_names = ["card_uid", "user_name", "user_id"]
    with open("./db/uid.csv", "a") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writerows(user_dict)
