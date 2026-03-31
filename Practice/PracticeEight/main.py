from services.phonebook_service import *
from utils.csv_loader import load_from_csv


def menu():
    while True:
        print("\n========= PHONEBOOK MENU =========")
        print("1. Add or update user")
        print("2. Load users from CSV")
        print("3. Show all users / search by pattern")
        print("4. Show users with pagination")
        print("5. Update user manually")
        print("6. Delete user by name, surname, or phone")
        print("7. Exit")

        choice = input("Choose: ")

        if choice == "1":
            name = input("Name: ")
            surname = input("Surname: ")
            phone = input("Phone: ")
            add_or_update_user(name, surname, phone)

        elif choice == "2":
            path = input("CSV path: ")
            load_from_csv(path)

        elif choice == "3":
            pattern = input("Search (name, surname, or phone; leave empty for all): ") or None
            users = get_users(pattern)
            for u in users:
                print(u)

        elif choice == "4":
            limit = int(input("Limit: "))
            offset = int(input("Offset: "))
            users = get_users_paginated(limit, offset)
            for u in users:
                print(u)

        elif choice == "5":
            update_user(
                old_name=input("Current name: "),
                old_surname=input("Current surname: "),
                new_name=input("New name: ") or None,
                new_surname=input("New surname: ") or None,
                new_phone=input("New phone: ") or None
            )

        elif choice == "6":
            value = input("Enter name, surname, or phone to delete: ")
            delete_user(value)

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid choice!")


menu()