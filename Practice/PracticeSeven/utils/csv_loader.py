import csv
from services.phonebook_service import add_user

def load_from_csv(path):
    with open(path, newline='') as file:
        reader = csv.reader(file)

        for row in reader:
            username, phone = row
            add_user(username, phone)