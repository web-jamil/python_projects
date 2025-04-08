import sqlite3
from datetime import datetime
from tabulate import tabulate
import hashlib
import getpass
from abc import ABC, abstractmethod

class Database:
    """Singleton database connection handler"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = sqlite3.connect('medicine_store.db')
            cls._instance.cursor = cls._instance.conn.cursor()
            cls._instance.initialize_db()
        return cls._instance
    
    def initialize_db(self):
        """Initialize database tables"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'staff')),
            is_active INTEGER DEFAULT 1
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            supplier TEXT,
            batch_number TEXT,
            manufacturing_date TEXT,
            expiry_date TEXT,
            reorder_level INTEGER DEFAULT 10,
            last_updated TEXT
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            sale_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            sale_date TEXT NOT NULL,
            sold_by INTEGER NOT NULL,
            customer_name TEXT,
            FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id),
            FOREIGN KEY (sold_by) REFERENCES users(user_id)
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            purchase_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            purchase_date TEXT NOT NULL,
            purchased_by INTEGER NOT NULL,
            supplier_name TEXT,
            FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id),
            FOREIGN KEY (purchased_by) REFERENCES users(user_id)
        ''')
        
        # Create admin user if not exists
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
        if self.cursor.fetchone()[0] == 0:
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute('''
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash, 'System Administrator', 'admin'))
        
        self.conn.commit()
    
    def execute_query(self, query, params=()):
        """Execute a SQL query with parameters"""
        self.cursor.execute(query, params)
        return self.cursor
    
    def commit(self):
        """Commit changes to the database"""
        self.conn.commit()
    
    def close(self):
        """Close the database connection"""
        self.conn.close()

class Model(ABC):
    """Abstract base class for all models"""
    @abstractmethod
    def save(self):
        pass
    
    @abstractmethod
    def delete(self):
        pass
    
    @classmethod
    @abstractmethod
    def get_all(cls):
        pass
    
    @classmethod
    @abstractmethod
    def get_by_id(cls, id):
        pass

class User(Model):
    """User model representing system users"""
    def __init__(self, user_id=None, username=None, password_hash=None, 
                 full_name=None, role=None, is_active=True):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.role = role
        self.is_active = is_active
    
    def save(self):
        db = Database()
        if self.user_id is None:
            # New user
            db.execute_query('''
            INSERT INTO users (username, password_hash, full_name, role, is_active)
            VALUES (?, ?, ?, ?, ?)
            ''', (self.username, self.password_hash, self.full_name, self.role, self.is_active))
        else:
            # Update existing user
            db.execute_query('''
            UPDATE users SET username=?, password_hash=?, full_name=?, role=?, is_active=?
            WHERE user_id=?
            ''', (self.username, self.password_hash, self.full_name, self.role, self.is_active, self.user_id))
        db.commit()
    
    def delete(self):
        if self.user_id is not None:
            db = Database()
            db.execute_query("DELETE FROM users WHERE user_id=?", (self.user_id,))
            db.commit()
    
    @classmethod
    def get_all(cls):
        db = Database()
        cursor = db.execute_query("SELECT * FROM users")
        return [cls(*row) for row in cursor.fetchall()]
    
    @classmethod
    def get_by_id(cls, user_id):
        db = Database()
        cursor = db.execute_query("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        return cls(*row) if row else None
    
    @classmethod
    def get_by_username(cls, username):
        db = Database()
        cursor = db.execute_query("SELECT * FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        return cls(*row) if row else None
    
    def authenticate(self, password):
        """Verify password against stored hash"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

class Medicine(Model):
    """Medicine model representing inventory items"""
    def __init__(self, medicine_id=None, name=None, description=None, category=None,
                 price=None, quantity=None, supplier=None, batch_number=None,
                 manufacturing_date=None, expiry_date=None, reorder_level=10, last_updated=None):
        self.medicine_id = medicine_id
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.quantity = quantity
        self.supplier = supplier
        self.batch_number = batch_number
        self.manufacturing_date = manufacturing_date
        self.expiry_date = expiry_date
        self.reorder_level = reorder_level
        self.last_updated = last_updated or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save(self):
        db = Database()
        if self.medicine_id is None:
            # New medicine
            db.execute_query('''
            INSERT INTO medicines (
                name, description, category, price, quantity, supplier, 
                batch_number, manufacturing_date, expiry_date, reorder_level, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.name, self.description, self.category, self.price, self.quantity,
                self.supplier, self.batch_number, self.manufacturing_date, 
                self.expiry_date, self.reorder_level, self.last_updated
            ))
        else:
            # Update existing medicine
            db.execute_query('''
            UPDATE medicines SET 
                name=?, description=?, category=?, price=?, quantity=?,
                supplier=?, batch_number=?, manufacturing_date=?, expiry_date=?,
                reorder_level=?, last_updated=?
            WHERE medicine_id=?
            ''', (
                self.name, self.description, self.category, self.price, self.quantity,
                self.supplier, self.batch_number, self.manufacturing_date,
                self.expiry_date, self.reorder_level, self.last_updated, self.medicine_id
            ))
        db.commit()
    
    def delete(self):
        if self.medicine_id is not None:
            db = Database()
            db.execute_query("DELETE FROM medicines WHERE medicine_id=?", (self.medicine_id,))
            db.commit()
    
    @classmethod
    def get_all(cls):
        db = Database()
        cursor = db.execute_query("SELECT * FROM medicines ORDER BY name")
        return [cls(*row) for row in cursor.fetchall()]
    
    @classmethod
    def get_by_id(cls, medicine_id):
        db = Database()
        cursor = db.execute_query("SELECT * FROM medicines WHERE medicine_id=?", (medicine_id,))
        row = cursor.fetchone()
        return cls(*row) if row else None
    
    @classmethod
    def search(cls, term):
        db = Database()
        cursor = db.execute_query('''
        SELECT * FROM medicines 
        WHERE name LIKE ? OR category LIKE ? OR batch_number LIKE ?
        ''', (f"%{term}%", f"%{term}%", f"%{term}%"))
        return [cls(*row) for row in cursor.fetchall()]
    
    @classmethod
    def get_expired(cls):
        db = Database()
        cursor = db.execute_query("SELECT * FROM medicines WHERE expiry_date < ?", 
                                (datetime.now().strftime("%Y-%m-%d"),))
        return [cls(*row) for row in cursor.fetchall()]
    
    def is_low_stock(self):
        return self.quantity < self.reorder_level
    
    def is_expired(self):
        return datetime.strptime(self.expiry_date, "%Y-%m-%d") < datetime.now()

class Sale(Model):
    """Sale model representing sales transactions"""
    def __init__(self, sale_id=None, medicine_id=None, quantity=None, sale_price=None,
                 total_amount=None, sale_date=None, sold_by=None, customer_name=None):
        self.sale_id = sale_id
        self.medicine_id = medicine_id
        self.quantity = quantity
        self.sale_price = sale_price
        self.total_amount = total_amount
        self.sale_date = sale_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sold_by = sold_by
        self.customer_name = customer_name
    
    def save(self):
        db = Database()
        if self.sale_id is None:
            # New sale
            db.execute_query('''
            INSERT INTO sales (
                medicine_id, quantity, sale_price, total_amount, sale_date, sold_by, customer_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.medicine_id, self.quantity, self.sale_price, 
                self.total_amount, self.sale_date, self.sold_by, self.customer_name
            ))
            
            # Update inventory
            medicine = Medicine.get_by_id(self.medicine_id)
            if medicine:
                medicine.quantity -= self.quantity
                medicine.save()
        else:
            # Update existing sale (not typically done)
            db.execute_query('''
            UPDATE sales SET 
                medicine_id=?, quantity=?, sale_price=?, total_amount=?,
                sale_date=?, sold_by=?, customer_name=?
            WHERE sale_id=?
            ''', (
                self.medicine_id, self.quantity, self.sale_price, 
                self.total_amount, self.sale_date, self.sold_by, 
                self.customer_name, self.sale_id
            ))
        db.commit()
    
    def delete(self):
        if self.sale_id is not None:
            db = Database()
            db.execute_query("DELETE FROM sales WHERE sale_id=?", (self.sale_id,))
            db.commit()
    
    @classmethod
    def get_all(cls):
        db = Database()
        cursor = db.execute_query('''
        SELECT s.* FROM sales s
        JOIN medicines m ON s.medicine_id = m.medicine_id
        ORDER BY s.sale_date DESC
        ''')
        return [cls(*row) for row in cursor.fetchall()]
    
    @classmethod
    def get_by_id(cls, sale_id):
        db = Database()
        cursor = db.execute_query("SELECT * FROM sales WHERE sale_id=?", (sale_id,))
        row = cursor.fetchone()
        return cls(*row) if row else None
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        db = Database()
        cursor = db.execute_query('''
        SELECT s.* FROM sales s
        WHERE DATE(s.sale_date) BETWEEN ? AND ?
        ORDER BY s.sale_date DESC
        ''', (start_date, end_date))
        return [cls(*row) for row in cursor.fetchall()]
    
    @classmethod
    def get_today_sales(cls):
        today = datetime.now().strftime("%Y-%m-%d")
        return cls.get_by_date_range(today, today)
    
    @classmethod
    def get_monthly_sales(cls):
        month = datetime.now().strftime("%Y-%m")
        db = Database()
        cursor = db.execute_query('''
        SELECT s.* FROM sales s
        WHERE strftime('%Y-%m', s.sale_date) = ?
        ORDER BY s.sale_date DESC
        ''', (month,))
        return [cls(*row) for row in cursor.fetchall()]

class Purchase(Model):
    """Purchase model representing inventory purchases"""
    def __init__(self, purchase_id=None, medicine_id=None, quantity=None, 
                 purchase_price=None, total_amount=None, purchase_date=None, 
                 purchased_by=None, supplier_name=None):
        self.purchase_id = purchase_id
        self.medicine_id = medicine_id
        self.quantity = quantity
        self.purchase_price = purchase_price
        self.total_amount = total_amount
        self.purchase_date = purchase_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.purchased_by = purchased_by
        self.supplier_name = supplier_name
    
    def save(self):
        db = Database()
        if self.purchase_id is None:
            # New purchase
            db.execute_query('''
            INSERT INTO purchases (
                medicine_id, quantity, purchase_price, total_amount, purchase_date, purchased_by, supplier_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.medicine_id, self.quantity, self.purchase_price, 
                self.total_amount, self.purchase_date, self.purchased_by, self.supplier_name
            ))
            
            # Update inventory and price (20% markup)
            medicine = Medicine.get_by_id(self.medicine_id)
            if medicine:
                medicine.quantity += self.quantity
                medicine.price = self.purchase_price * 1.2
                medicine.save()
        else:
            # Update existing purchase (not typically done)
            db.execute_query('''
            UPDATE purchases SET 
                medicine_id=?, quantity=?, purchase_price=?, total_amount=?,
                purchase_date=?, purchased_by=?, supplier_name=?
            WHERE purchase_id=?
            ''', (
                self.medicine_id, self.quantity, self.purchase_price, 
                self.total_amount, self.purchase_date, self.purchased_by, 
                self.supplier_name, self.purchase_id
            ))
        db.commit()
    
    def delete(self):
        if self.purchase_id is not None:
            db = Database()
            db.execute_query("DELETE FROM purchases WHERE purchase_id=?", (self.purchase_id,))
            db.commit()
    
    @classmethod
    def get_all(cls):
        db = Database()
        cursor = db.execute_query('''
        SELECT p.* FROM purchases p
        JOIN medicines m ON p.medicine_id = m.medicine_id
        ORDER BY p.purchase_date DESC
        ''')
        return [cls(*row) for row in cursor.fetchall()]
    
    @classmethod
    def get_by_id(cls, purchase_id):
        db = Database()
        cursor = db.execute_query("SELECT * FROM purchases WHERE purchase_id=?", (purchase_id,))
        row = cursor.fetchone()
        return cls(*row) if row else None
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        db = Database()
        cursor = db.execute_query('''
        SELECT p.* FROM purchases p
        WHERE DATE(p.purchase_date) BETWEEN ? AND ?
        ORDER BY p.purchase_date DESC
        ''', (start_date, end_date))
        return [cls(*row) for row in cursor.fetchall()]
    
    @classmethod
    def get_today_purchases(cls):
        today = datetime.now().strftime("%Y-%m-%d")
        return cls.get_by_date_range(today, today)
    
    @classmethod
    def get_monthly_purchases(cls):
        month = datetime.now().strftime("%Y-%m")
        db = Database()
        cursor = db.execute_query('''
        SELECT p.* FROM purchases p
        WHERE strftime('%Y-%m', p.purchase_date) = ?
        ORDER BY p.purchase_date DESC
        ''', (month,))
        return [cls(*row) for row in cursor.fetchall()]

class MedicineStoreController:
    """Main controller for the medicine store system"""
    def __init__(self):
        self.current_user = None
    
    def login(self):
        """Authenticate user"""
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        
        user = User.get_by_username(username)
        if user and user.authenticate(password) and user.is_active:
            self.current_user = user
            print(f"\nWelcome, {user.full_name} ({user.role})!")
            return True
        else:
            print("Invalid credentials or inactive account!")
            return False
    
    def run(self):
        """Main application loop"""
        if not self.login():
            return
        
        while True:
            print("\nMedicine Store Management System")
            print("1. Medicine Management")
            print("2. Sales")
            print("3. Purchases")
            print("4. Reports")
            
            if self.current_user.role == 'admin':
                print("5. User Management")
                print("6. Exit")
                max_choice = 6
            else:
                print("5. Exit")
                max_choice = 5
            
            try:
                choice = int(input("Enter choice: "))
                
                if choice == 1:
                    self.medicine_management()
                elif choice == 2:
                    self.sales_management()
                elif choice == 3:
                    self.purchases_management()
                elif choice == 4:
                    self.reports_management()
                elif choice == 5 and self.current_user.role == 'admin':
                    self.user_management()
                elif choice == max_choice:
                    print("Exiting system...")
                    break
                else:
                    print("Invalid choice!")
            except ValueError:
                print("Please enter a valid number!")
    
    def medicine_management(self):
        """Handle medicine management operations"""
        print("\nMedicine Management")
        print("1. Add Medicine")
        print("2. Update Medicine")
        print("3. List Medicines")
        print("4. Search Medicine")
        print("5. Check Expired Medicines")
        
        try:
            choice = int(input("Enter choice: "))
            
            if choice == 1:
                self.add_medicine()
            elif choice == 2:
                self.update_medicine()
            elif choice == 3:
                self.list_medicines()
            elif choice == 4:
                self.search_medicine()
            elif choice == 5:
                self.check_expired_medicines()
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a valid number!")
    
    def add_medicine(self):
        """Add a new medicine to inventory"""
        print("\nAdd New Medicine")
        medicine = Medicine()
        medicine.name = input("Medicine Name: ")
        medicine.description = input("Description: ")
        medicine.category = input("Category: ")
        medicine.price = float(input("Price: "))
        medicine.quantity = int(input("Initial Quantity: "))
        medicine.supplier = input("Supplier: ")
        medicine.batch_number = input("Batch Number: ")
        medicine.manufacturing_date = input("Manufacturing Date (YYYY-MM-DD): ")
        medicine.expiry_date = input("Expiry Date (YYYY-MM-DD): ")
        medicine.reorder_level = int(input("Reorder Level: "))
        
        medicine.save()
        print("Medicine added successfully!")
    
    def update_medicine(self):
        """Update existing medicine details"""
        medicine_id = int(input("Enter Medicine ID to update: "))
        medicine = Medicine.get_by_id(medicine_id)
        
        if not medicine:
            print("Medicine not found!")
            return
        
        print("\nCurrent Medicine Details:")
        print(f"1. Name: {medicine.name}")
        print(f"2. Description: {medicine.description}")
        print(f"3. Category: {medicine.category}")
        print(f"4. Price: {medicine.price}")
        print(f"5. Quantity: {medicine.quantity}")
        print(f"6. Supplier: {medicine.supplier}")
        print(f"7. Batch Number: {medicine.batch_number}")
        print(f"8. Manufacturing Date: {medicine.manufacturing_date}")
        print(f"9. Expiry Date: {medicine.expiry_date}")
        print(f"10. Reorder Level: {medicine.reorder_level}")
        
        try:
            field = int(input("\nEnter field number to update (1-10): "))
            new_value = input("Enter new value: ")
            
            if field == 1:
                medicine.name = new_value
            elif field == 2:
                medicine.description = new_value
            elif field == 3:
                medicine.category = new_value
            elif field == 4:
                medicine.price = float(new_value)
            elif field == 5:
                medicine.quantity = int(new_value)
            elif field == 6:
                medicine.supplier = new_value
            elif field == 7:
                medicine.batch_number = new_value
            elif field == 8:
                medicine.manufacturing_date = new_value
            elif field == 9:
                medicine.expiry_date = new_value
            elif field == 10:
                medicine.reorder_level = int(new_value)
            else:
                print("Invalid field number!")
                return
            
            medicine.save()
            print("Medicine updated successfully!")
        except ValueError:
            print("Invalid input for the selected field!")
    
    def list_medicines(self):
        """Display all medicines in inventory"""
        medicines = Medicine.get_all()
        
        if not medicines:
            print("No medicines found!")
            return
        
        headers = ["ID", "Name", "Category", "Price", "Qty", "Expiry", "Supplier"]
        data = []
        for med in medicines:
            data.append([
                med.medicine_id, med.name, med.category, f"${med.price:.2f}", 
                f"{med.quantity} {'(LOW)' if med.is_low_stock() else ''}",
                med.expiry_date, med.supplier
            ])
        
        print("\nMedicine Inventory:")
        print(tabulate(data, headers=headers, tablefmt="grid"))
    
    def search_medicine(self):
        """Search medicines by name, category, or batch"""
        search_term = input("Enter search term (name/category/batch): ")
        medicines = Medicine.search(search_term)
        
        if not medicines:
            print("No matching medicines found!")
            return
        
        headers = ["ID", "Name", "Description", "Category", "Price", "Qty", "Expiry"]
        data = []
        for med in medicines:
            desc = med.description[:30] + "..." if len(med.description) > 30 else med.description
            data.append([
                med.medicine_id, med.name, desc, med.category, 
                f"${med.price:.2f}", med.quantity, med.expiry_date
            ])
        
        print("\nSearch Results:")
        print(tabulate(data, headers=headers, tablefmt="grid"))
    
    def check_expired_medicines(self):
        """Display expired medicines"""
        expired = Medicine.get_expired()
        
        if not expired:
            print("No expired medicines found!")
            return
        
        headers = ["ID", "Name", "Batch", "Expiry", "Qty", "Price"]
        data = []
        for med in expired:
            data.append([
                med.medicine_id, med.name, med.batch_number, 
                med.expiry_date, med.quantity, f"${med.price:.2f}"
            ])
        
        print("\nExpired Medicines:")
        print(tabulate(data, headers=headers, tablefmt="grid"))
    
    def sales_management(self):
        """Handle sales operations"""
        print("\nSales")
        print("1. Make Sale")
        print("2. View Sales Report")
        
        try:
            choice = int(input("Enter choice: "))
            
            if choice == 1:
                self.make_sale()
            elif choice == 2:
                self.view_sales_report()
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a valid number!")
    
    def make_sale(self):
        """Process a new sale"""
        print("\nNew Sale")
        self.list_medicines()
        
        try:
            medicine_id = int(input("Enter Medicine ID: "))
            quantity = int(input("Enter Quantity: "))
            
            medicine = Medicine.get_by_id(medicine_id)
            if not medicine:
                print("Invalid Medicine ID!")
                return
            
            if medicine.quantity < quantity:
                print(f"Insufficient stock! Only {medicine.quantity} available.")
                return
            
            total = medicine.price * quantity
            customer = input("Customer Name (optional): ")
            
            sale = Sale(
                medicine_id=medicine_id,
                quantity=quantity,
                sale_price=medicine.price,
                total_amount=total,
                sold_by=self.current_user.user_id,
                customer_name=customer
            )
            sale.save()
            
            print(f"Sale completed! Total: ${total:.2f}")
        except ValueError:
            print("Invalid input!")
    
    def view_sales_report(self):
        """Display sales reports"""
        print("\nSales Report Options:")
        print("1. Today's Sales")
        print("2. This Month's Sales")
        print("3. Custom Date Range")
        
        try:
            choice = int(input("Enter choice: "))
            
            if choice == 1:
                sales = Sale.get_today_sales()
            elif choice == 2:
                sales = Sale.get_monthly_sales()
            elif choice == 3:
                start_date = input("Enter start date (YYYY-MM-DD): ")
                end_date = input("Enter end date (YYYY-MM-DD): ")
                sales = Sale.get_by_date_range(start_date, end_date)
            else:
                print("Invalid choice!")
                return
            
            if not sales:
                print("No sales found for the selected period!")
                return
            
            headers = ["Sale ID", "Medicine", "Qty", "Unit Price", "Total", "Date", "Customer"]
            data = []
            for sale in sales:
                medicine = Medicine.get_by_id(sale.medicine_id)
                med_name = medicine.name if medicine else "Unknown"
                data.append([
                    sale.sale_id, med_name, sale.quantity, 
                    f"${sale.sale_price:.2f}", f"${sale.total_amount:.2f}", 
                    sale.sale_date, sale.customer_name or "N/A"
                ])
            
            print("\nSales Report:")
            print(tabulate(data, headers=headers, tablefmt="grid"))
            
            # Show summary
            total_sales = sum(sale.total_amount for sale in sales)
            print(f"\nTotal Sales: ${total_sales:.2f}")
            print(f"Number of Transactions: {len(sales)}")
        except ValueError:
            print("Invalid input!")
    
    def purchases_management(self):
        """Handle purchase operations"""
        print("\nPurchases")
        print("1. Record Purchase")
        print("2. View Purchases Report")
        
        try:
            choice = int(input("Enter choice: "))
            
            if choice == 1:
                self.record_purchase()
            elif choice == 2:
                self.view_purchases_report()
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a valid number!")
    
    def record_purchase(self):
        """Record a new inventory purchase"""
        print("\nRecord Purchase")
        self.list_medicines()
        
        try:
            medicine_id = int(input("Enter Medicine ID: "))
            quantity = int(input("Enter Quantity: "))
            purchase_price = float(input("Enter Purchase Price per unit: "))
            supplier = input("Supplier Name: ")
            
            total = purchase_price * quantity
            
            purchase = Purchase(
                medicine_id=medicine_id,
                quantity=quantity,
                purchase_price=purchase_price,
                total_amount=total,
                purchased_by=self.current_user.user_id,
                supplier_name=supplier
            )
            purchase.save()
            
            print(f"Purchase recorded! Total: ${total:.2f}")
        except ValueError:
            print("Invalid input!")
    
    def view_purchases_report(self):
        """Display purchases reports"""
        print("\nPurchases Report Options:")
        print("1. Today's Purchases")
        print("2. This Month's Purchases")
        print("3. Custom Date Range")
        
        try:
            choice = int(input("Enter choice: "))
            
            if choice == 1:
                purchases = Purchase.get_today_purchases()
            elif choice == 2:
                purchases = Purchase.get_monthly_purchases()
            elif choice == 3:
                start_date = input("Enter start date (YYYY-MM-DD): ")
                end_date = input("Enter end date (YYYY-MM-DD): ")
                purchases = Purchase.get_by_date_range(start_date, end_date)
            else:
                print("Invalid choice!")
                return
            
            if not purchases:
                print("No purchases found for the selected period!")
                return
            
            headers = ["Purchase ID", "Medicine", "Qty", "Unit Cost", "Total", "Date", "Supplier"]
            data = []
            for purchase in purchases:
                medicine = Medicine.get_by_id(purchase.medicine_id)
                med_name = medicine.name if medicine else "Unknown"
                data.append([
                    purchase.purchase_id, med_name, purchase.quantity, 
                    f"${purchase.purchase_price:.2f}", f"${purchase.total_amount:.2f}", 
                    purchase.purchase_date, purchase.supplier_name
                ])
            
            print("\nPurchases Report:")
            print(tabulate(data, headers=headers, tablefmt="grid"))
            
            # Show summary
            total_purchases = sum(purchase.total_amount for purchase in purchases)
            print(f"\nTotal Purchases: ${total_purchases:.2f}")
            print(f"Number of Purchase Orders: {len(purchases)}")
        except ValueError:
            print("Invalid input!")
    
    def reports_management(self):
        """Handle reporting operations"""
        print("\nReports")
        print("1. Inventory Report")
        print("2. Sales Report")
        print("3. Purchases Report")
        print("4. Expired Medicines Report")
        
        try:
            choice = int(input("Enter choice: "))
            
            if choice == 1:
                self.list_medicines()
            elif choice == 2:
                self.view_sales_report()
            elif choice == 3:
                self.view_purchases_report()
            elif choice == 4:
                self.check_expired_medicines()
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a valid number!")
    
    def user_management(self):
        """Handle user management (admin only)"""
        if self.current_user.role != 'admin':
            print("Access denied! Admin privileges required.")
            return
        
        print("\nUser Management")
        print("1. List Users")
        print("2. Add User")
        print("3. Update User")
        print("4. Deactivate/Activate User")
        
        try:
            choice = int(input("Enter choice: "))
            
            if choice == 1:
                self.list_users()
            elif choice == 2:
                self.add_user()
            elif choice == 3:
                self.update_user()
            elif choice == 4:
                self.toggle_user_status()
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a valid number!")
    
    def list_users(self):
        """Display all system users"""
        users = User.get_all()
        
        if not users:
            print("No users found!")
            return
        
        headers = ["ID", "Username", "Full Name", "Role", "Status"]
        data = []
        for user in users:
            status = "Active" if user.is_active else "Inactive"
            data.append([
                user.user_id, user.username, user.full_name, user.role, status
            ])
        
        print("\nUser List:")
        print(tabulate(data, headers=headers, tablefmt="grid"))
    
    def add_user(self):
        """Add a new system user"""
        print("\nAdd New User")
        user = User()
        user.username = input("Username: ")
        password = getpass.getpass("Password: ")
        user.password_hash = hashlib.sha256(password.encode()).hexdigest()
        user.full_name = input("Full Name: ")
        user.role = input("Role (admin/manager/staff): ").lower()
        
        if user.role not in ['admin', 'manager', 'staff']:
            print("Invalid role! Must be admin, manager, or staff.")
            return
        
        user.save()
        print("User added successfully!")
    
    def update_user(self):
        """Update existing user details"""
        user_id = int(input("Enter User ID to update: "))
        user = User.get_by_id(user_id)
        
        if not user:
            print("User not found!")
            return
        
        print("\nCurrent User Details:")
        print(f"1. Username: {user.username}")
        print(f"2. Full Name: {user.full_name}")
        print(f"3. Role: {user.role}")
        
        try:
            field = int(input("\nEnter field number to update (1-3): "))
            new_value = input("Enter new value: ")
            
            if field == 1:
                user.username = new_value
            elif field == 2:
                user.full_name = new_value
            elif field == 3:
                if new_value.lower() not in ['admin', 'manager', 'staff']:
                    print("Invalid role! Must be admin, manager, or staff.")
                    return
                user.role = new_value.lower()
            else:
                print("Invalid field number!")
                return
            
            user.save()
            print("User updated successfully!")
        except ValueError:
            print("Invalid input!")
    
    def toggle_user_status(self):
        """Activate or deactivate a user"""
        user_id = int(input("Enter User ID to activate/deactivate: "))
        user = User.get_by_id(user_id)
        
        if not user:
            print("User not found!")
            return
        
        user.is_active = not user.is_active
        user.save()
        
        status = "activated" if user.is_active else "deactivated"
        print(f"User {status} successfully!")

if __name__ == "__main__":
    app = MedicineStoreController()
    app.run()