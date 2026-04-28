import csv

from services.phonebook_service import upsert_contact


def _parse_row(row):
    values = [value.strip() for value in row if value is not None]
    if not values:
        return None

    if values[0].lower() == 'name':
        return None

    if len(values) < 3:
        return None

    name = values[0]
    surname = values[1]
    phone = values[2]
    phone_type = values[3] if len(values) >= 4 and values[3] else 'mobile'
    email = values[4] if len(values) >= 5 and values[4] else None
    birthday = values[5] if len(values) >= 6 and values[5] else None
    group_name = values[6] if len(values) >= 7 and values[6] else None

    return {
        'name': name,
        'surname': surname,
        'phone': phone,
        'phone_type': phone_type,
        'email': email,
        'birthday': birthday,
        'group_name': group_name,
    }


def load_from_csv(path):
    with open(path, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)

        for row in reader:
            contact = _parse_row(row)
            if not contact:
                continue

            upsert_contact(**contact)