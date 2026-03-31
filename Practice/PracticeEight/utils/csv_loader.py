import csv
from services.phonebook_service import insert_many_users


def load_from_csv(path):
    names = []
    surnames = []
    phones = []

    with open(path, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)

        for row in reader:
            if len(row) >= 3:
                name, surname, phone = row[0], row[1], row[2]
                names.append(name)
                surnames.append(surname)
                phones.append(phone)

    insert_many_users(names, surnames, phones)