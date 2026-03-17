from services.phonebook_service import *
from utils.csv_loader import load_from_csv

def menu():
    while True:
        print("\n1. Add user")
        print("2. Load from CSV")
        print("3. Update user")
        print("4. Show users")
        print("5. Delete user")
        print("6. Exit")

        choice = input("Choose: ")

        if choice == "1":
            add_user(input("Name: "), input("Phone: ")) 
           

        elif choice == "2":
            load_from_csv(input("CSV path: "))
            print("Users successfully loaded from the CSV file")

        elif choice == "3":
            update_user(
                input("Current name: "),
                new_username=input("New name: ") or None,
                new_phone=input("New phone: ") or None
            )
            print("User updated successfully")

        elif choice == "4":
            users = get_users(input("Search: ") or None)
            for u in users:
                print(u)

        elif choice == "5":
            delete_user(username=input("Name to delete: "))
            print("user deleted successfully")

        elif choice == "6":
            break

menu()