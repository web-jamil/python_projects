# import os
# import re

# class Contact:
#     def __init__(self, name, phone, email):
#         self.name = name
#         self.phone = phone
#         self.email = email

#     def __str__(self):
#         return f"Name: {self.name}, Phone: {self.phone}, Email: {self.email}"

# class ContactBook:
#     def __init__(self, filename="contacts.txt"):
#         self.filename = filename
#         self.contacts = self.load_contacts()

#     def load_contacts(self):
#         """Load contacts from file with error handling"""
#         contacts = {}
#         if os.path.exists(self.filename):
#             try:
#                 with open(self.filename, 'r') as file:
#                     for line in file:
#                         line = line.strip()
#                         if line:  # Skip empty lines
#                             try:
#                                 name, phone, email = line.split(",")
#                                 contacts[name.lower()] = Contact(name.strip(), phone.strip(), email.strip())
#                             except ValueError:
#                                 print(f"[Warning] Skipping malformed line: {line}")
#             except Exception as e:
#                 print(f"[Error] Failed to load contacts: {e}")
#         return contacts

#     def save_contacts(self):
#         """Save contacts to file atomically"""
#         try:
#             temp_file = self.filename + ".tmp"
#             with open(temp_file, 'w') as file:
#                 for contact in sorted(self.contacts.values(), key=lambda x: x.name):
#                     file.write(f"{contact.name},{contact.phone},{contact.email}\n")
#             # Atomic file operation
#             if os.path.exists(self.filename):
#                 os.replace(temp_file, self.filename)
#             else:
#                 os.rename(temp_file, self.filename)
#         except Exception as e:
#             print(f"[Error] Failed to save contacts: {e}")
#             if os.path.exists(temp_file):
#                 os.remove(temp_file)

#     def add_contact(self, name, phone, email):
#         """Add a new contact with validation"""
#         name_key = name.lower()
#         if name_key in self.contacts:
#             print(f"[Error] Contact '{name}' already exists!")
#             return False
        
#         if not self.is_valid_phone(phone):
#             print("[Error] Invalid phone number. Must be 10 digits.")
#             return False
            
#         if not self.is_valid_email(email):
#             print("[Error] Invalid email format. Should be like 'example@domain.com'")
#             return False
            
#         self.contacts[name_key] = Contact(name, phone, email)
#         self.save_contacts()
#         print(f"[Success] Contact '{name}' added successfully!")
#         return True

#     def update_contact(self, name, phone=None, email=None):
#         """Update existing contact details"""
#         name_key = name.lower()
#         if name_key not in self.contacts:
#             print(f"[Error] Contact '{name}' not found!")
#             return False
            
#         contact = self.contacts[name_key]
        
#         if phone and not self.is_valid_phone(phone):
#             print("[Error] Invalid phone number. Must be 10 digits.")
#             return False
            
#         if email and not self.is_valid_email(email):
#             print("[Error] Invalid email format. Should be like 'example@domain.com'")
#             return False
            
#         if phone:
#             contact.phone = phone
#         if email:
#             contact.email = email
            
#         self.save_contacts()
#         print(f"[Success] Contact '{name}' updated successfully!")
#         return True

#     def delete_contact(self, name):
#         """Delete a contact"""
#         name_key = name.lower()
#         if name_key in self.contacts:
#             del self.contacts[name_key]
#             self.save_contacts()
#             print(f"[Success] Contact '{name}' deleted successfully!")
#             return True
#         else:
#             print(f"[Error] Contact '{name}' not found!")
#             return False

#     def search_contact(self, name):
#         """Search for a contact by name"""
#         name_key = name.lower()
#         if name_key in self.contacts:
#             print("\n--- Contact Found ---")
#             print(self.contacts[name_key])
#             print("--------------------")
#             return True
#         else:
#             print(f"[Info] No contact found for '{name}'")
#             return False

#     def list_contacts(self):
#         """List all contacts alphabetically"""
#         if not self.contacts:
#             print("[Info] No contacts available.")
#             return
            
#         print("\n--- All Contacts ---")
#         for contact in sorted(self.contacts.values(), key=lambda x: x.name):
#             print(contact)
#         print(f"Total: {len(self.contacts)} contacts")
#         print("-------------------")

#     @staticmethod
#     def is_valid_phone(phone):
#         """Validate phone number (10 digits)"""
#         cleaned = ''.join(c for c in phone if c.isdigit())
#         return len(cleaned) == 10

#     @staticmethod
#     def is_valid_email(email):
#         """Basic email validation"""
#         return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) is not None

# def print_menu():
#     """Display the main menu"""
#     print("\n" + "="*40)
#     print("CONTACT BOOK MANAGEMENT SYSTEM".center(40))
#     print("="*40)
#     print("1. Add New Contact")
#     print("2. Update Existing Contact")
#     print("3. Delete Contact")
#     print("4. Search Contact")
#     print("5. List All Contacts")
#     print("6. Exit")
#     print("="*40)

# def get_input(prompt, required=True):
#     """Get user input with validation"""
#     while True:
#         value = input(prompt).strip()
#         if not value and required:
#             print("[Error] This field is required!")
#             continue
#         return value

# def main():
#     contact_book = ContactBook()
    
#     while True:
#         print_menu()
#         choice = get_input("Enter your choice (1-6): ")
        
#         if choice == '1':  # Add Contact
#             print("\n--- Add New Contact ---")
#             name = get_input("Name: ")
#             phone = get_input("Phone (10 digits): ")
#             email = get_input("Email: ")
#             contact_book.add_contact(name, phone, email)
            
#         elif choice == '2':  # Update Contact
#             print("\n--- Update Contact ---")
#             name = get_input("Name of contact to update: ")
#             if contact_book.search_contact(name):
#                 phone = get_input("New phone (press Enter to keep current): ", required=False)
#                 email = get_input("New email (press Enter to keep current): ", required=False)
#                 if not phone and not email:
#                     print("[Info] No changes made.")
#                 else:
#                     contact_book.update_contact(name, phone or None, email or None)
            
#         elif choice == '3':  # Delete Contact
#             print("\n--- Delete Contact ---")
#             name = get_input("Name of contact to delete: ")
#             contact_book.delete_contact(name)
            
#         elif choice == '4':  # Search Contact
#             print("\n--- Search Contact ---")
#             name = get_input("Name to search: ")
#             contact_book.search_contact(name)
            
#         elif choice == '5':  # List Contacts
#             contact_book.list_contacts()
            
#         elif choice == '6':  # Exit
#             print("\n[Info] Thank you for using Contact Book!")
#             print("Exiting the program...")
#             break
            
#         else:
#             print("[Error] Invalid choice! Please enter 1-6.")

# if __name__ == "__main__":
#     main()

"""

import json
import os
import re
import getpass
from datetime import datetime

class Contact:
    def __init__(self, name, phone, email, country_code="+1"):
        self.name = name
        self.phone = phone
        self.email = email
        self.country_code = country_code

    def __str__(self):
        return f"Name: {self.name}, Phone: {self.country_code}{self.phone}, Email: {self.email}"

    def to_dict(self):
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "country_code": self.country_code
        }

    @staticmethod
    def from_dict(data):
        return Contact(
            data["name"],
            data["phone"],
            data["email"],
            data.get("country_code", "+1")
        )

class ContactBook:
    def __init__(self, filename="contacts.json"):
        self.filename = filename
        self.contacts = self.load_contacts()
        self.country_codes = {
            "US": "+1", "UK": "+44", "IN": "+91", 
            "AU": "+61", "DE": "+49", "FR": "+33"
        }

    def load_contacts(self):
        if not os.path.exists(self.filename):
            return {}
            
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                return {contact["name"]: Contact.from_dict(contact) for contact in data}
        except Exception as e:
            print(f"Error loading contacts: {e}")
            return {}

    def save_contacts(self):
        try:
            with open(self.filename, 'w') as file:
                json.dump([contact.to_dict() for contact in self.contacts.values()], 
                          file, indent=2)
        except Exception as e:
            print(f"Error saving contacts: {e}")

    def add_contact(self, contact):
        if contact.name in self.contacts:
            print(f"Contact '{contact.name}' already exists!")
            return False
            
        self.contacts[contact.name] = contact
        self.save_contacts()
        print(f"Contact '{contact.name}' added successfully!")
        return True

    def update_contact(self, name, **kwargs):
        if name not in self.contacts:
            print(f"Contact '{name}' not found!")
            return False
            
        contact = self.contacts[name]
        for key, value in kwargs.items():
            if value:  # Only update if value is provided
                setattr(contact, key, value)
                
        self.save_contacts()
        print(f"Contact '{name}' updated successfully!")
        return True

    def delete_contact(self, name):
        if name not in self.contacts:
            print(f"Contact '{name}' not found!")
            return False
            
        del self.contacts[name]
        self.save_contacts()
        print(f"Contact '{name}' deleted successfully!")
        return True

    def search_contacts(self, query):
        results = []
        query = query.lower()
        for contact in self.contacts.values():
            if (query in contact.name.lower() or 
                query in contact.phone or 
                query in contact.email.lower()):
                results.append(contact)
        return results

    def list_contacts(self, sort_by="name"):
        return sorted(
            self.contacts.values(), 
            key=lambda x: getattr(x, sort_by.lower())
        )

    def backup_contacts(self, backup_file=None):
        backup_file = backup_file or f"contacts_backup_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(backup_file, 'w') as file:
                json.dump([contact.to_dict() for contact in self.contacts.values()], 
                          file, indent=2)
            print(f"Backup created successfully at {backup_file}")
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False

    @staticmethod
    def validate_phone(phone):
        return bool(re.match(r'^\d{10,15}$', phone))

    @staticmethod
    def validate_email(email):
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

    def get_country_code(self):
        print("\nAvailable Country Codes:")
        for code, prefix in self.country_codes.items():
            print(f"{code}: {prefix}")
            
        while True:
            choice = input("Enter country code (e.g., US, UK) or custom prefix (e.g., +33): ").upper()
            if choice in self.country_codes:
                return self.country_codes[choice]
            elif re.match(r'^\+\d{1,3}$', choice):
                return choice
            print("Invalid country code! Try again.")

def print_menu():
    print("\n" + "="*50)
    print("ADVANCED CONTACT BOOK MANAGEMENT SYSTEM".center(50))
    print("="*50)
    print("1. Add New Contact")
    print("2. Update Contact")
    print("3. Delete Contact")
    print("4. Search Contacts")
    print("5. List All Contacts")
    print("6. Create Backup")
    print("7. Exit")
    print("="*50)

def authenticate():
    password = getpass.getpass("Enter admin password: ")
    return password == "admin123"  # Change this in production!

def get_contact_details(contact_book):
    name = input("Enter full name: ").strip()
    while not name:
        print("Name cannot be empty!")
        name = input("Enter full name: ").strip()

    country_code = contact_book.get_country_code()
    
    phone = input(f"Enter phone number (without {country_code}): ").strip()
    while not contact_book.validate_phone(phone):
        print("Invalid phone number! Must be 10-15 digits.")
        phone = input(f"Enter phone number (without {country_code}): ").strip()

    email = input("Enter email address: ").strip()
    while not contact_book.validate_email(email):
        print("Invalid email address!")
        email = input("Enter email address: ").strip()

    return Contact(name, phone, email, country_code)

def main():
    if not authenticate():
        print("Authentication failed!")
        return

    contact_book = ContactBook()
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == '1':  # Add Contact
            contact = get_contact_details(contact_book)
            contact_book.add_contact(contact)

        elif choice == '2':  # Update Contact
            name = input("Enter name of contact to update: ").strip()
            if name in contact_book.contacts:
                print("\nLeave blank to keep current value")
                country_code = input(f"New country code [current: {contact_book.contacts[name].country_code}]: ").strip()
                phone = input(f"New phone [current: {contact_book.contacts[name].phone}]: ").strip()
                email = input(f"New email [current: {contact_book.contacts[name].email}]: ").strip()
                
                updates = {}
                if country_code:
                    updates["country_code"] = contact_book.get_country_code() if country_code.upper() == "CHOOSE" else country_code
                if phone:
                    updates["phone"] = phone
                if email:
                    updates["email"] = email
                
                contact_book.update_contact(name, **updates)
            else:
                print(f"Contact '{name}' not found!")

        elif choice == '3':  # Delete Contact
            name = input("Enter name of contact to delete: ").strip()
            contact_book.delete_contact(name)

        elif choice == '4':  # Search Contacts
            query = input("Enter search term: ").strip()
            results = contact_book.search_contacts(query)
            if results:
                print("\n=== Search Results ===")
                for contact in results:
                    print(contact)
                print(f"Found {len(results)} contacts")
            else:
                print("No matching contacts found")

        elif choice == '5':  # List Contacts
            sort_by = input("Sort by (name/phone/email/country_code): ").strip().lower()
            contacts = contact_book.list_contacts(sort_by if sort_by in ["name", "phone", "email", "country_code"] else "name")
            print("\n=== All Contacts ===")
            for contact in contacts:
                print(contact)
            print(f"Total: {len(contacts)} contacts")

        elif choice == '6':  # Backup
            backup_file = input("Enter backup filename (press Enter for default): ").strip()
            contact_book.backup_contacts(backup_file if backup_file else None)

        elif choice == '7':  # Exit
            print("Exiting contact book. Goodbye!")
            break

        else:
            print("Invalid choice! Please enter 1-7")

if __name__ == "__main__":
    main()"
"""




import json
import os
import re
import getpass
from datetime import datetime

class Contact:
    def __init__(self, name, phone, email, country_code="+1", job_title=None, salary=None):
        self.name = name
        self.phone = phone
        self.email = email
        self.country_code = country_code
        self.job_title = job_title
        self.salary = salary
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        salary_info = f", Salary: ${self.salary:,.2f}" if self.salary else ""
        job_info = f", Position: {self.job_title}" if self.job_title else ""
        return (f"Name: {self.name}, Phone: {self.country_code}{self.phone}, "
                f"Email: {self.email}{job_info}{salary_info}, "
                f"Last Updated: {self.last_updated}")

    def to_dict(self):
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "country_code": self.country_code,
            "job_title": self.job_title,
            "salary": self.salary,
            "last_updated": self.last_updated
        }

    @staticmethod
    def from_dict(data):
        return Contact(
            data["name"],
            data["phone"],
            data["email"],
            data.get("country_code", "+1"),
            data.get("job_title"),
            data.get("salary")
        )

class ContactBook:
    def __init__(self, filename="contacts.json"):
        self.filename = filename
        self.contacts = self.load_contacts()
        self.country_codes = {
            "US": "+1", "UK": "+44", "IN": "+91",
            "AU": "+61", "DE": "+49", "FR": "+33",
            "JP": "+81", "BR": "+55", "CN": "+86"
        }
        self.job_categories = [
            "Manager", "Developer", "Designer",
            "Analyst", "Director", "Engineer",
            "Consultant", "Other"
        ]

    def load_contacts(self):
        if not os.path.exists(self.filename):
            return {}
            
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                return {contact["name"]: Contact.from_dict(contact) for contact in data}
        except Exception as e:
            print(f"Error loading contacts: {e}")
            return {}

    def save_contacts(self):
        try:
            with open(self.filename, 'w') as file:
                json.dump([contact.to_dict() for contact in self.contacts.values()], 
                         file, indent=2)
        except Exception as e:
            print(f"Error saving contacts: {e}")

    def add_contact(self, contact):
        if contact.name in self.contacts:
            print(f"Contact '{contact.name}' already exists!")
            return False
            
        self.contacts[contact.name] = contact
        self.save_contacts()
        print(f"Contact '{contact.name}' added successfully!")
        return True

    def update_contact(self, name, **kwargs):
        if name not in self.contacts:
            print(f"Contact '{name}' not found!")
            return False
            
        contact = self.contacts[name]
        for key, value in kwargs.items():
            if value is not None:  # Only update if value is provided
                setattr(contact, key, value)
        contact.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        self.save_contacts()
        print(f"Contact '{name}' updated successfully!")
        return True

    def delete_contact(self, name):
        if name not in self.contacts:
            print(f"Contact '{name}' not found!")
            return False
            
        del self.contacts[name]
        self.save_contacts()
        print(f"Contact '{name}' deleted successfully!")
        return True

    def search_contacts(self, query):
        results = []
        query = query.lower()
        for contact in self.contacts.values():
            if (query in contact.name.lower() or 
                query in contact.phone or 
                query in contact.email.lower() or
                (contact.job_title and query in contact.job_title.lower())):
                results.append(contact)
        return results

    def list_contacts(self, sort_by="name"):
        valid_sort_fields = ["name", "phone", "email", "job_title", "salary", "last_updated"]
        sort_by = sort_by if sort_by in valid_sort_fields else "name"
        return sorted(
            self.contacts.values(), 
            key=lambda x: str(getattr(x, sort_by)).lower()
        )

    def backup_contacts(self, backup_file=None):
        backup_file = backup_file or f"contacts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(backup_file, 'w') as file:
                json.dump([contact.to_dict() for contact in self.contacts.values()], 
                         file, indent=2)
            print(f"Backup created successfully at {backup_file}")
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False

    def get_job_stats(self):
        stats = {
            "total_contacts": len(self.contacts),
            "jobs": {},
            "salary_stats": {
                "total": 0,
                "average": 0,
                "max": 0,
                "min": float('inf')
            }
        }
        
        salary_count = 0
        total_salary = 0
        
        for contact in self.contacts.values():
            if contact.job_title:
                stats["jobs"][contact.job_title] = stats["jobs"].get(contact.job_title, 0) + 1
            
            if contact.salary:
                salary_count += 1
                total_salary += contact.salary
                stats["salary_stats"]["max"] = max(stats["salary_stats"]["max"], contact.salary)
                stats["salary_stats"]["min"] = min(stats["salary_stats"]["min"], contact.salary)
        
        if salary_count > 0:
            stats["salary_stats"]["total"] = total_salary
            stats["salary_stats"]["average"] = total_salary / salary_count
            stats["salary_stats"]["count"] = salary_count
        else:
            stats["salary_stats"]["min"] = 0
            
        return stats

    @staticmethod
    def validate_phone(phone):
        return bool(re.match(r'^\d{10,15}$', phone))

    @staticmethod
    def validate_email(email):
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

    @staticmethod
    def validate_salary(salary):
        try:
            return float(salary) >= 0
        except ValueError:
            return False

    def get_country_code(self):
        print("\nAvailable Country Codes:")
        for code, prefix in self.country_codes.items():
            print(f"{code}: {prefix}")
            
        while True:
            choice = input("Enter country code (e.g., US, UK) or custom prefix (e.g., +33): ").upper()
            if choice in self.country_codes:
                return self.country_codes[choice]
            elif re.match(r'^\+\d{1,3}$', choice):
                return choice
            print("Invalid country code! Try again.")

    def get_job_title(self):
        print("\nJob Categories:")
        for i, category in enumerate(self.job_categories, 1):
            print(f"{i}. {category}")
            
        while True:
            choice = input("Select job category (1-8) or enter custom title: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(self.job_categories):
                return self.job_categories[int(choice)-1]
            elif choice:
                return choice.title()
            print("Invalid selection!")

def print_menu():
    print("\n" + "="*60)
    print("PROFESSIONAL CONTACT BOOK WITH JOB TRACKING".center(60))
    print("="*60)
    print("1. Add New Contact")
    print("2. Update Contact")
    print("3. Delete Contact")
    print("4. Search Contacts")
    print("5. List All Contacts")
    print("6. View Job Statistics")
    print("7. Create Backup")
    print("8. Exit")
    print("="*60)

def authenticate():
    password = getpass.getpass("Enter admin password: ")
    return password == "secure123"  # Change this in production!

def get_contact_details(contact_book):
    name = input("Enter full name: ").strip()
    while not name:
        print("Name cannot be empty!")
        name = input("Enter full name: ").strip()

    country_code = contact_book.get_country_code()
    
    phone = input(f"Enter phone number (without {country_code}): ").strip()
    while not contact_book.validate_phone(phone):
        print("Invalid phone number! Must be 10-15 digits.")
        phone = input(f"Enter phone number (without {country_code}): ").strip()

    email = input("Enter email address: ").strip()
    while not contact_book.validate_email(email):
        print("Invalid email address!")
        email = input("Enter email address: ").strip()

    job_title = contact_book.get_job_title()
    
    salary = None
    salary_input = input("Enter annual salary (leave empty if unknown): $").strip()
    if salary_input:
        while not contact_book.validate_salary(salary_input):
            print("Invalid salary! Must be a positive number.")
            salary_input = input("Enter annual salary: $").strip()
        salary = float(salary_input)

    return Contact(name, phone, email, country_code, job_title, salary)

def main():
    if not authenticate():
        print("Authentication failed! Access denied.")
        return

    contact_book = ContactBook()
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == '1':  # Add Contact
            contact = get_contact_details(contact_book)
            contact_book.add_contact(contact)

        elif choice == '2':  # Update Contact
            name = input("Enter name of contact to update: ").strip()
            if name in contact_book.contacts:
                print("\nLeave blank to keep current value")
                print(f"[Current: {contact_book.contacts[name]}]")
                
                updates = {}
                if input("Update country code? (y/n): ").lower() == 'y':
                    updates["country_code"] = contact_book.get_country_code()
                
                phone = input(f"New phone [current: {contact_book.contacts[name].phone}]: ").strip()
                if phone:
                    updates["phone"] = phone
                
                email = input(f"New email [current: {contact_book.contacts[name].email}]: ").strip()
                if email:
                    updates["email"] = email
                
                if input("Update job title? (y/n): ").lower() == 'y':
                    updates["job_title"] = contact_book.get_job_title()
                
                salary = input(f"New salary [current: {contact_book.contacts[name].salary or 'Not set'}]: $").strip()
                if salary:
                    updates["salary"] = float(salary)
                
                contact_book.update_contact(name, **updates)
            else:
                print(f"Contact '{name}' not found!")

        elif choice == '3':  # Delete Contact
            name = input("Enter name of contact to delete: ").strip()
            contact_book.delete_contact(name)

        elif choice == '4':  # Search Contacts
            query = input("Enter search term (name, phone, email, or job title): ").strip()
            results = contact_book.search_contacts(query)
            if results:
                print("\n=== Search Results ===")
                for contact in results:
                    print(contact)
                print(f"Found {len(results)} contacts")
            else:
                print("No matching contacts found")

        elif choice == '5':  # List Contacts
            sort_by = input("Sort by (name/phone/email/job_title/salary/last_updated): ").strip().lower()
            contacts = contact_book.list_contacts(sort_by)
            print("\n=== All Contacts ===")
            for contact in contacts:
                print(contact)
            print(f"\nTotal: {len(contacts)} contacts")
            print(f"Sorted by: {sort_by}")

        elif choice == '6':  # Job Statistics
            stats = contact_book.get_job_stats()
            print("\n=== Employment Statistics ===")
            print(f"Total Contacts: {stats['total_contacts']}")
            print(f"Contacts with Salary Data: {stats['salary_stats'].get('count', 0)}")
            
            if stats['salary_stats']['count'] > 0:
                print("\nSalary Statistics:")
                print(f"Total Salary: ${stats['salary_stats']['total']:,.2f}")
                print(f"Average Salary: ${stats['salary_stats']['average']:,.2f}")
                print(f"Highest Salary: ${stats['salary_stats']['max']:,.2f}")
                print(f"Lowest Salary: ${stats['salary_stats']['min']:,.2f}")
            
            if stats['jobs']:
                print("\nJob Title Distribution:")
                for job, count in sorted(stats['jobs'].items(), key=lambda x: x[1], reverse=True):
                    print(f"{job}: {count} contacts")

        elif choice == '7':  # Backup
            backup_file = input("Enter backup filename (press Enter for default): ").strip()
            contact_book.backup_contacts(backup_file if backup_file else None)

        elif choice == '8':  # Exit
            print("Exiting contact book. Goodbye!")
            break

        else:
            print("Invalid choice! Please enter 1-8")

if __name__ == "__main__":
    main()