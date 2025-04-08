import sqlite3
import datetime
from tabulate import tabulate
import getpass

# Initialize database
conn = sqlite3.connect('medical_store.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    batch_no TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    supplier TEXT,
    category TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    medical_history TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    medicine_id INTEGER,
    quantity INTEGER NOT NULL,
    sale_date TEXT NOT NULL,
    total_price REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    full_name TEXT
)
''')

conn.commit()

class Medicine:
    def __init__(self, name, batch_no, expiry_date, price, quantity, supplier, category):
        self.name = name
        self.batch_no = batch_no
        self.expiry_date = expiry_date
        self.price = price
        self.quantity = quantity
        self.supplier = supplier
        self.category = category

    def save(self):
        cursor.execute('''
        INSERT INTO medicines (name, batch_no, expiry_date, price, quantity, supplier, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.name, self.batch_no, self.expiry_date, self.price, self.quantity, self.supplier, self.category))
        conn.commit()

    @staticmethod
    def get_all():
        cursor.execute('SELECT * FROM medicines')
        return cursor.fetchall()

    @staticmethod
    def search_by_name(name):
        cursor.execute('SELECT * FROM medicines WHERE name LIKE ?', (f'%{name}%',))
        return cursor.fetchall()

    @staticmethod
    def update_quantity(medicine_id, quantity):
        cursor.execute('UPDATE medicines SET quantity = quantity - ? WHERE id = ?', (quantity, medicine_id))
        conn.commit()

    @staticmethod
    def get_expiring_soon(days=30):
        today = datetime.date.today()
        future_date = today + datetime.timedelta(days=days)
        cursor.execute('SELECT * FROM medicines WHERE expiry_date BETWEEN ? AND ?', 
                      (today.strftime('%Y-%m-%d'), future_date.strftime('%Y-%m-%d')))
        return cursor.fetchall()

class Customer:
    def __init__(self, name, phone=None, email=None, address=None, medical_history=None):
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.medical_history = medical_history

    def save(self):
        cursor.execute('''
        INSERT INTO customers (name, phone, email, address, medical_history)
        VALUES (?, ?, ?, ?, ?)
        ''', (self.name, self.phone, self.email, self.address, self.medical_history))
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def search_by_name(name):
        cursor.execute('SELECT * FROM customers WHERE name LIKE ?', (f'%{name}%',))
        return cursor.fetchall()

class Sale:
    @staticmethod
    def create(customer_id, medicine_id, quantity, total_price):
        sale_date = datetime.date.today().strftime('%Y-%m-%d')
        cursor.execute('''
        INSERT INTO sales (customer_id, medicine_id, quantity, sale_date, total_price)
        VALUES (?, ?, ?, ?, ?)
        ''', (customer_id, medicine_id, quantity, sale_date, total_price))
        conn.commit()

    @staticmethod
    def get_sales_report(start_date, end_date):
        cursor.execute('''
        SELECT s.sale_date, m.name, s.quantity, s.total_price, c.name
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE s.sale_date BETWEEN ? AND ?
        ''', (start_date, end_date))
        return cursor.fetchall()

class User:
    @staticmethod
    def create(username, password, role, full_name):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('''
        INSERT INTO users (username, password, role, full_name)
        VALUES (?, ?, ?, ?)
        ''', (username, hashed_password, role, full_name))
        conn.commit()

    @staticmethod
    def authenticate(username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        return cursor.fetchone()

def display_menu(role):
    print("\n=== Medical Store Management System ===")
    print("1. Medicine Management")
    print("2. Customer Management")
    print("3. Sales/Billing")
    print("4. Reports")
    if role == 'admin':
        print("5. User Management")
    print("0. Exit")
    print("=====================================")

def medicine_management():
    while True:
        print("\n--- Medicine Management ---")
        print("1. Add New Medicine")
        print("2. View All Medicines")
        print("3. Search Medicine")
        print("4. Check Expiring Medicines")
        print("0. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            print("\nAdd New Medicine:")
            name = input("Name: ")
            batch_no = input("Batch No: ")
            expiry_date = input("Expiry Date (YYYY-MM-DD): ")
            price = float(input("Price: "))
            quantity = int(input("Quantity: "))
            supplier = input("Supplier: ")
            category = input("Category: ")

            medicine = Medicine(name, batch_no, expiry_date, price, quantity, supplier, category)
            medicine.save()
            print("Medicine added successfully!")

        elif choice == '2':
            medicines = Medicine.get_all()
            print("\nAll Medicines:")
            print(tabulate(medicines, headers=["ID", "Name", "Batch", "Expiry", "Price", "Qty", "Supplier", "Category"]))

        elif choice == '3':
            name = input("Enter medicine name to search: ")
            results = Medicine.search_by_name(name)
            print("\nSearch Results:")
            print(tabulate(results, headers=["ID", "Name", "Batch", "Expiry", "Price", "Qty", "Supplier", "Category"]))

        elif choice == '4':
            days = int(input("Check medicines expiring within how many days? (default 30): ") or 30)
            expiring = Medicine.get_expiring_soon(days)
            print("\nExpiring Soon:")
            print(tabulate(expiring, headers=["ID", "Name", "Batch", "Expiry", "Price", "Qty", "Supplier", "Category"]))

        elif choice == '0':
            break

        else:
            print("Invalid choice!")

def customer_management():
    while True:
        print("\n--- Customer Management ---")
        print("1. Add New Customer")
        print("2. Search Customer")
        print("0. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            print("\nAdd New Customer:")
            name = input("Name: ")
            phone = input("Phone: ")
            email = input("Email: ")
            address = input("Address: ")
            medical_history = input("Medical History: ")

            customer = Customer(name, phone, email, address, medical_history)
            customer.save()
            print("Customer added successfully!")

        elif choice == '2':
            name = input("Enter customer name to search: ")
            results = Customer.search_by_name(name)
            print("\nSearch Results:")
            print(tabulate(results, headers=["ID", "Name", "Phone", "Email", "Address", "Medical History"]))

        elif choice == '0':
            break

        else:
            print("Invalid choice!")

def sales_management():
    while True:
        print("\n--- Sales Management ---")
        print("1. New Bill")
        print("2. View Today's Sales")
        print("0. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            # Search or add customer
            customer_name = input("Customer Name (leave blank for walk-in): ")
            customer_id = None
            if customer_name:
                customers = Customer.search_by_name(customer_name)
                if customers:
                    print("\nSelect Customer:")
                    for idx, customer in enumerate(customers, 1):
                        print(f"{idx}. {customer[1]} ({customer[2]})")
                    selection = int(input("Enter customer number (0 to add new): "))
                    if selection > 0:
                        customer_id = customers[selection-1][0]
                else:
                    add_new = input("Customer not found. Add new? (y/n): ")
                    if add_new.lower() == 'y':
                        customer = Customer(customer_name)
                        customer_id = customer.save()

            # Add medicines to bill
            cart = []
            while True:
                print("\nCurrent Cart:")
                if cart:
                    for item in cart:
                        print(f"{item['name']} - {item['quantity']} x {item['price']} = {item['quantity']*item['price']}")
                else:
                    print("Empty")

                med_name = input("Enter medicine name (or 'done' to finish): ")
                if med_name.lower() == 'done':
                    break

                medicines = Medicine.search_by_name(med_name)
                if not medicines:
                    print("Medicine not found!")
                    continue

                print("\nSelect Medicine:")
                for idx, med in enumerate(medicines, 1):
                    print(f"{idx}. {med[1]} (Batch: {med[2]}, Qty: {med[5]}, Price: {med[4]})")

                selection = int(input("Enter medicine number: ")) - 1
                selected_med = medicines[selection]

                quantity = int(input(f"Enter quantity (available: {selected_med[5]}): "))
                if quantity > selected_med[5]:
                    print("Not enough stock!")
                    continue

                cart.append({
                    'id': selected_med[0],
                    'name': selected_med[1],
                    'price': selected_med[4],
                    'quantity': quantity
                })

            # Process sale
            if cart:
                total = sum(item['price'] * item['quantity'] for item in cart)
                print(f"\nTotal Amount: {total}")
                payment = float(input("Amount Received: "))
                change = payment - total
                print(f"Change: {change}")

                confirm = input("Confirm sale? (y/n): ")
                if confirm.lower() == 'y':
                    for item in cart:
                        Sale.create(customer_id, item['id'], item['quantity'], item['price']*item['quantity'])
                        Medicine.update_quantity(item['id'], item['quantity'])
                    print("Sale completed successfully!")
            else:
                print("No items in cart!")

        elif choice == '2':
            today = datetime.date.today().strftime('%Y-%m-%d')
            sales = Sale.get_sales_report(today, today)
            if sales:
                print("\nToday's Sales:")
                print(tabulate(sales, headers=["Date", "Medicine", "Qty", "Amount", "Customer"]))
            else:
                print("No sales today.")

        elif choice == '0':
            break

        else:
            print("Invalid choice!")

def reports():
    while True:
        print("\n--- Reports ---")
        print("1. Sales Report")
        print("2. Stock Report")
        print("0. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            start_date = input("Start Date (YYYY-MM-DD): ")
            end_date = input("End Date (YYYY-MM-DD): ")
            sales = Sale.get_sales_report(start_date, end_date)
            if sales:
                print("\nSales Report:")
                print(tabulate(sales, headers=["Date", "Medicine", "Qty", "Amount", "Customer"]))
            else:
                print("No sales in this period.")

        elif choice == '2':
            medicines = Medicine.get_all()
            print("\nStock Report:")
            print(tabulate(medicines, headers=["ID", "Name", "Batch", "Expiry", "Price", "Qty", "Supplier", "Category"]))

        elif choice == '0':
            break

        else:
            print("Invalid choice!")

def user_management():
    while True:
        print("\n--- User Management ---")
        print("1. Add New User")
        print("2. List Users")
        print("0. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            print("\nAdd New User:")
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            role = input("Role (admin/staff): ")
            full_name = input("Full Name: ")

            User.create(username, password, role, full_name)
            print("User added successfully!")

        elif choice == '2':
            cursor.execute('SELECT id, username, role, full_name FROM users')
            users = cursor.fetchall()
            print("\nAll Users:")
            print(tabulate(users, headers=["ID", "Username", "Role", "Full Name"]))

        elif choice == '0':
            break

        else:
            print("Invalid choice!")

def main():
    # Create admin user if none exists
    cursor.execute('SELECT * FROM users')
    if not cursor.fetchall():
        User.create('admin', 'admin123', 'admin', 'Administrator')

    # Login
    while True:
        print("\n=== Login ===")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        user = User.authenticate(username, password)
        if user:
            print(f"\nWelcome, {user[3]} ({user[2]})!")
            break
        print("Invalid username or password!")

    role = user[2]

    # Main menu
    while True:
        display_menu(role)
        choice = input("Enter your choice: ")

        if choice == '1':
            medicine_management()
        elif choice == '2':
            customer_management()
        elif choice == '3':
            sales_management()
        elif choice == '4':
            reports()
        elif choice == '5' and role == 'admin':
            user_management()
        elif choice == '0':
            print("Thank you for using Medical Store Management System!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    import hashlib  # Import moved here to avoid error in User class
    main()
    conn.close()