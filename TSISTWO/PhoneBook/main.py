from services.phonebook_service import (
    add_phone_to_contact,
    count_contacts,
    delete_user,
    export_contacts_to_json,
    get_contact_details,
    get_contacts,
    move_contact_to_group,
    read_contacts_from_json,
    replace_contact,
    save_contact_record,
    search_contacts,
    update_user,
)
from utils.csv_loader import load_from_csv


def _print_contact(contact, index=None):
    prefix = f'{index}. ' if index is not None else ''
    phone_text = ', '.join(f"{item['type']}: {item['phone']}" for item in contact.get('phones', []))
    print(
        f"{prefix}{contact.get('name', '')} {contact.get('surname', '')} | "
        f"group: {contact.get('group', 'Other')} | "
        f"email: {contact.get('email') or '-'} | "
        f"birthday: {contact.get('birthday') or '-'} | "
        f"added: {contact.get('created_at') or '-'}"
    )
    print(f"   phones: {phone_text or '-'}")


def _print_contacts(contacts):
    if not contacts:
        print('No contacts found.')
        return

    for index, contact in enumerate(contacts, start=1):
        _print_contact(contact, index)


def _prompt_optional_date(label):
    value = input(label).strip()
    return value or None


def _paginate_contacts():
    query = input('Search text (leave empty for all): ').strip() or None
    group_name = input('Filter by group (leave empty for all): ').strip() or None
    sort_by = input('Sort by name / birthday / date added [name]: ').strip() or 'name'
    page_size = int(input('Page size [5]: ').strip() or '5')
    page = 0

    while True:
        total = count_contacts(query=query, group_name=group_name)
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = max(0, min(page, total_pages - 1))
        offset = page * page_size
        contacts = get_contacts(query=query, group_name=group_name, sort_by=sort_by, limit=page_size, offset=offset)

        print(f'\nPage {page + 1} of {total_pages} | total contacts: {total}')
        _print_contacts(contacts)

        action = input('next / prev / quit: ').strip().lower()
        if action == 'next':
            if page + 1 < total_pages:
                page += 1
            else:
                print('Already on the last page.')
        elif action == 'prev':
            if page > 0:
                page -= 1
            else:
                print('Already on the first page.')
        elif action == 'quit':
            break
        else:
            print('Unknown command.')


def _import_json_contacts():
    path = input('JSON path: ').strip()
    contacts = read_contacts_from_json(path)

    for contact in contacts:
        normalized = {
            'name': contact.get('name'),
            'surname': contact.get('surname'),
            'email': contact.get('email'),
            'birthday': contact.get('birthday'),
            'group_name': contact.get('group') or contact.get('group_name'),
            'phones': contact.get('phones', []),
        }

        existing = get_contact_details(normalized['name'], normalized['surname'])
        if existing:
            decision = input(
                f"Duplicate contact {normalized['name']} {normalized['surname']}. Skip or overwrite? [skip/overwrite]: "
            ).strip().lower()
            if decision == 'overwrite':
                replace_contact(normalized)
                print(f"Overwritten: {normalized['name']} {normalized['surname']}")
            else:
                print(f"Skipped: {normalized['name']} {normalized['surname']}")
            continue

        save_contact_record(normalized)
        print(f"Imported: {normalized['name']} {normalized['surname']}")


def menu():
    while True:
        print('\n========= PHONEBOOK MENU =========')
        print('1. Add or update contact')
        print('2. Load contacts from CSV')
        print('3. Search contacts by text')
        print('4. Filter / sort / paginate contacts')
        print('5. Update contact manually')
        print('6. Delete contact by name, surname, or phone')
        print('7. Add phone to contact')
        print('8. Move contact to group')
        print('9. Export contacts to JSON')
        print('10. Import contacts from JSON')
        print('11. Exit')

        choice = input('Choose: ').strip()

        if choice == '1':
            name = input('Name: ')
            surname = input('Surname: ')
            phone = input('Phone (optional): ').strip() or None
            phone_type = input('Phone type home / work / mobile [mobile]: ').strip() or 'mobile'
            email = input('Email (optional): ').strip() or None
            birthday = _prompt_optional_date('Birthday YYYY-MM-DD (optional): ')
            group_name = input('Group Family / Work / Friend / Other (optional): ').strip() or None
            save_contact_record({
                'name': name,
                'surname': surname,
                'phone': phone,
                'phone_type': phone_type,
                'email': email,
                'birthday': birthday,
                'group_name': group_name,
            })
            print('Contact saved successfully.')

        elif choice == '2':
            path = input('CSV path: ')
            load_from_csv(path)
            print('Contacts loaded from CSV.')

        elif choice == '3':
            pattern = input('Search text (name, surname, email, or phone): ').strip()
            _print_contacts(search_contacts(pattern))

        elif choice == '4':
            _paginate_contacts()

        elif choice == '5':
            update_user(
                old_name=input('Current name: '),
                old_surname=input('Current surname: '),
                new_name=input('New name: ').strip() or None,
                new_surname=input('New surname: ').strip() or None,
                new_phone=input('New phone (optional): ').strip() or None,
                new_phone_type=input('New phone type home / work / mobile [mobile]: ').strip() or None,
                new_email=input('New email (optional): ').strip() or None,
                new_birthday=_prompt_optional_date('New birthday YYYY-MM-DD (optional): '),
                new_group=input('New group (optional): ').strip() or None,
            )

        elif choice == '6':
            value = input('Enter name, surname, full name, or phone to delete: ')
            delete_user(value)
            print('Contact deleted successfully.')

        elif choice == '7':
            contact_name = input('Contact name or full name: ')
            phone = input('Phone: ')
            phone_type = input('Phone type home / work / mobile [mobile]: ').strip() or 'mobile'
            add_phone_to_contact(contact_name, phone, phone_type)
            print('Phone added successfully.')

        elif choice == '8':
            contact_name = input('Contact name or full name: ')
            group_name = input('New group: ')
            move_contact_to_group(contact_name, group_name)
            print('Contact moved successfully.')

        elif choice == '9':
            path = input('JSON export path: ')
            export_contacts_to_json(path)
            print('Contacts exported successfully.')

        elif choice == '10':
            _import_json_contacts()

        elif choice == '11':
            print('Goodbye!')
            break

        else:
            print('Invalid choice!')


menu()