# import json
# import os

# # Room class to represent a single room in the hotel
# class Room:
#     def __init__(self, room_id, room_type, price, is_available=True):
#         self.room_id = room_id
#         self.room_type = room_type
#         self.price = price
#         self.is_available = is_available

#     def __str__(self):
#         return f"Room ID: {self.room_id}, Type: {self.room_type}, Price: {self.price}, Available: {'Yes' if self.is_available else 'No'}"


# # Customer class to represent a customer who books a room
# class Customer:
#     def __init__(self, customer_id, name, contact_info, booked_room_id=None):
#         self.customer_id = customer_id
#         self.name = name
#         self.contact_info = contact_info
#         self.booked_room_id = booked_room_id

#     def __str__(self):
#         return f"Customer ID: {self.customer_id}, Name: {self.name}, Contact Info: {self.contact_info}, Room Booked: {self.booked_room_id}"


# # Hotel class to manage the hotel system
# class Hotel:
#     def __init__(self):
#         self.rooms = []  # List to store all rooms
#         self.customers = []  # List to store all customers
#         self.load_data()

#     def load_data(self):
#         """Load room and customer data from JSON files."""
#         if os.path.exists("rooms_data.json"):
#             with open("rooms_data.json", "r") as file:
#                 data = json.load(file)
#                 for room_data in data:
#                     room = Room(room_data["room_id"], room_data["room_type"], room_data["price"], room_data["is_available"])
#                     self.rooms.append(room)
        
#         if os.path.exists("customers_data.json"):
#             with open("customers_data.json", "r") as file:
#                 data = json.load(file)
#                 for customer_data in data:
#                     customer = Customer(customer_data["customer_id"], customer_data["name"], customer_data["contact_info"], customer_data["booked_room_id"])
#                     self.customers.append(customer)

#     def save_data(self):
#         """Save room and customer data to JSON files."""
#         room_data = [{"room_id": room.room_id, "room_type": room.room_type, "price": room.price, "is_available": room.is_available} for room in self.rooms]
#         customer_data = [{"customer_id": customer.customer_id, "name": customer.name, "contact_info": customer.contact_info, "booked_room_id": customer.booked_room_id} for customer in self.customers]
        
#         with open("rooms_data.json", "w") as file:
#             json.dump(room_data, file, indent=4)
        
#         with open("customers_data.json", "w") as file:
#             json.dump(customer_data, file, indent=4)

#     def add_room(self, room_type, price):
#         """Add a new room to the hotel."""
#         room_id = len(self.rooms) + 1  # Automatically generate a room ID based on the count of existing rooms
#         new_room = Room(room_id, room_type, price)
#         self.rooms.append(new_room)
#         print(f"Room {room_id} added successfully.")

#     def remove_room(self, room_id):
#         """Remove a room from the hotel."""
#         for room in self.rooms:
#             if room.room_id == room_id:
#                 self.rooms.remove(room)
#                 print(f"Room {room_id} removed successfully.")
#                 return
#         print("Room not found.")

#     def display_rooms(self):
#         """Display all rooms in the hotel."""
#         if not self.rooms:
#             print("No rooms available.")
#         else:
#             print("Available Rooms:")
#             for room in self.rooms:
#                 print(room)

#     def check_availability(self):
#         """Display available rooms."""
#         available_rooms = [room for room in self.rooms if room.is_available]
#         if available_rooms:
#             print("Available Rooms:")
#             for room in available_rooms:
#                 print(room)
#         else:
#             print("No rooms available currently.")

#     def book_room(self, customer_name, contact_info, room_id):
#         """Book a room for a customer."""
#         for room in self.rooms:
#             if room.room_id == room_id:
#                 if room.is_available:
#                     room.is_available = False  # Mark the room as not available
#                     customer_id = len(self.customers) + 1
#                     new_customer = Customer(customer_id, customer_name, contact_info, room_id)
#                     self.customers.append(new_customer)
#                     print(f"Room {room_id} booked successfully for {customer_name}.")
#                     return
#                 else:
#                     print("Room is already booked.")
#                     return
#         print("Room not found.")

#     def checkout(self, customer_id):
#         """Check out a customer and free up the room."""
#         for customer in self.customers:
#             if customer.customer_id == customer_id:
#                 room_id = customer.booked_room_id
#                 for room in self.rooms:
#                     if room.room_id == room_id:
#                         room.is_available = True  # Mark the room as available
#                         self.customers.remove(customer)
#                         print(f"Customer {customer_id} has checked out. Room {room_id} is now available.")
#                         return
#         print("Customer not found.")

#     def generate_report(self):
#         """Generate a report of the rooms and customers."""
#         print("\nHotel Report:")
#         print("Rooms Information:")
#         self.display_rooms()
#         print("\nCustomer Information:")
#         for customer in self.customers:
#             print(customer)


# # Hotel Management System with User Interface
# class HotelManagementSystem:
#     def __init__(self):
#         self.hotel = Hotel()
#         self.run()

#     def display_menu(self):
#         """Display the menu to the user."""
#         print("\nHotel Management System")
#         print("1. Add Room")
#         print("2. Remove Room")
#         print("3. Display All Rooms")
#         print("4. Check Room Availability")
#         print("5. Book Room")
#         print("6. Check Out")
#         print("7. Generate Report")
#         print("8. Exit")

#     def get_choice(self):
#         """Get the user's menu choice."""
#         while True:
#             try:
#                 choice = int(input("Enter your choice (1-8): "))
#                 if choice in range(1, 9):
#                     return choice
#                 else:
#                     print("Invalid choice. Please choose a number between 1 and 8.")
#             except ValueError:
#                 print("Invalid input. Please enter a valid number.")

#     def handle_choice(self, choice):
#         """Handle the user's menu choice."""
#         if choice == 1:  # Add Room
#             room_type = input("Enter room type (Single/Double/Suite): ")
#             price = float(input("Enter room price per night: "))
#             self.hotel.add_room(room_type, price)

#         elif choice == 2:  # Remove Room
#             room_id = int(input("Enter room ID to remove: "))
#             self.hotel.remove_room(room_id)

#         elif choice == 3:  # Display All Rooms
#             self.hotel.display_rooms()

#         elif choice == 4:  # Check Room Availability
#             self.hotel.check_availability()

#         elif choice == 5:  # Book Room
#             customer_name = input("Enter customer name: ")
#             contact_info = input("Enter customer contact info: ")
#             room_id = int(input("Enter room ID to book: "))
#             self.hotel.book_room(customer_name, contact_info, room_id)

#         elif choice == 6:  # Check Out
#             customer_id = int(input("Enter customer ID to check out: "))
#             self.hotel.checkout(customer_id)

#         elif choice == 7:  # Generate Report
#             self.hotel.generate_report()

#         elif choice == 8:  # Exit
#             self.hotel.save_data()
#             print("Exiting the system. All data has been saved.")
#             exit()

#     def run(self):
#         """Run the Hotel Management System."""
#         while True:
#             self.display_menu()
#             choice = self.get_choice()
#             self.handle_choice(choice)


# if __name__ == "__main__":
#     HotelManagementSystem()



import sqlite3
import hashlib
import secrets
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from enum import Enum, auto
import json
from tabulate import tabulate
import getpass

# --------------------------
# Enums for Type Safety
# --------------------------
class RoomType(Enum):
    SINGLE = auto()
    DOUBLE = auto()
    SUITE = auto()
    DELUXE = auto()
    PRESIDENTIAL = auto()

class BookingStatus(Enum):
    CONFIRMED = auto()
    CHECKED_IN = auto()
    CHECKED_OUT = auto()
    CANCELLED = auto()
    NO_SHOW = auto()

class PaymentMethod(Enum):
    CASH = auto()
    CREDIT_CARD = auto()
    DEBIT_CARD = auto()
    BANK_TRANSFER = auto()
    DIGITAL_WALLET = auto()

class UserRole(Enum):
    ADMIN = auto()
    MANAGER = auto()
    RECEPTIONIST = auto()
    HOUSEKEEPING = auto()
    GUEST = auto()

# --------------------------
# Domain Models
# --------------------------
@dataclass
class User:
    user_id: int
    username: str
    password_hash: str
    salt: str
    role: UserRole
    full_name: str
    email: str
    phone: str
    last_login: Optional[datetime]
    is_active: bool

@dataclass
class Guest:
    guest_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    id_proof: str
    registration_date: date
    loyalty_points: int

@dataclass
class Room:
    room_id: int
    room_number: str
    room_type: RoomType
    floor: int
    capacity: int
    amenities: List[str]
    rate_per_night: float
    is_available: bool
    last_maintenance_date: date

@dataclass
class Booking:
    booking_id: int
    guest_id: int
    room_id: int
    check_in_date: date
    check_out_date: date
    booking_date: datetime
    status: BookingStatus
    total_amount: float
    payment_method: Optional[PaymentMethod]
    special_requests: str

@dataclass
class Payment:
    payment_id: int
    booking_id: int
    amount: float
    payment_date: datetime
    payment_method: PaymentMethod
    transaction_id: str
    status: str  # "Completed", "Pending", "Failed"
    notes: str

@dataclass
class Service:
    service_id: int
    name: str
    description: str
    price: float
    is_available: bool

@dataclass
class ServiceRequest:
    request_id: int
    booking_id: int
    service_id: int
    request_time: datetime
    completion_time: Optional[datetime]
    status: str  # "Pending", "In Progress", "Completed"
    notes: str

# --------------------------
# Abstract Repositories
# --------------------------
class IUserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User: pass
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]: pass
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]: pass
    @abstractmethod
    def update(self, user: User): pass
    @abstractmethod
    def delete(self, user_id: int): pass
    @abstractmethod
    def list_all(self) -> List[User]: pass

class IGuestRepository(ABC):
    @abstractmethod
    def add(self, guest: Guest) -> Guest: pass
    @abstractmethod
    def get_by_id(self, guest_id: int) -> Optional[Guest]: pass
    @abstractmethod
    def search(self, query: str) -> List[Guest]: pass
    @abstractmethod
    def update(self, guest: Guest): pass
    @abstractmethod
    def delete(self, guest_id: int): pass

class IRoomRepository(ABC):
    @abstractmethod
    def add(self, room: Room) -> Room: pass
    @abstractmethod
    def get_by_id(self, room_id: int) -> Optional[Room]: pass
    @abstractmethod
    def get_by_number(self, room_number: str) -> Optional[Room]: pass
    @abstractmethod
    def list_available(self, start_date: date, end_date: date, room_type: Optional[RoomType] = None) -> List[Room]: pass
    @abstractmethod
    def update(self, room: Room): pass
    @abstractmethod
    def list_all(self) -> List[Room]: pass

class IBookingRepository(ABC):
    @abstractmethod
    def add(self, booking: Booking) -> Booking: pass
    @abstractmethod
    def get_by_id(self, booking_id: int) -> Optional[Booking]: pass
    @abstractmethod
    def get_by_guest(self, guest_id: int) -> List[Booking]: pass
    @abstractmethod
    def get_by_dates(self, start_date: date, end_date: date) -> List[Booking]: pass
    @abstractmethod
    def update(self, booking: Booking): pass
    @abstractmethod
    def cancel(self, booking_id: int): pass

# --------------------------
# SQLite Implementations
# --------------------------
class SQLiteUserRepository(IUserRepository):
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        
    def add(self, user: User) -> User:
        sql = """INSERT INTO users 
                (username, password_hash, salt, role, full_name, email, phone, last_login, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor = self.conn.cursor()
        cursor.execute(sql, (
            user.username,
            user.password_hash,
            user.salt,
            user.role.name,
            user.full_name,
            user.email,
            user.phone,
            user.last_login.isoformat() if user.last_login else None,
            user.is_active
        ))
        user.user_id = cursor.lastrowid
        self.conn.commit()
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        sql = "SELECT * FROM users WHERE user_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()
        return self._row_to_user(row) if row else None
    
    def get_by_username(self, username: str) -> Optional[User]:
        sql = "SELECT * FROM users WHERE username = ?"
        cursor = self.conn.cursor()
        cursor.execute(sql, (username,))
        row = cursor.fetchone()
        return self._row_to_user(row) if row else None
    
    def update(self, user: User):
        sql = """UPDATE users SET 
                username = ?, password_hash = ?, salt = ?, role = ?, full_name = ?, 
                email = ?, phone = ?, last_login = ?, is_active = ?
                WHERE user_id = ?"""
        self.conn.execute(sql, (
            user.username,
            user.password_hash,
            user.salt,
            user.role.name,
            user.full_name,
            user.email,
            user.phone,
            user.last_login.isoformat() if user.last_login else None,
            user.is_active,
            user.user_id
        ))
        self.conn.commit()
    
    def delete(self, user_id: int):
        self.conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        self.conn.commit()
    
    def list_all(self) -> List[User]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        return [self._row_to_user(row) for row in cursor.fetchall()]
    
    def _row_to_user(self, row) -> User:
        return User(
            user_id=row[0],
            username=row[1],
            password_hash=row[2],
            salt=row[3],
            role=UserRole[row[4]],
            full_name=row[5],
            email=row[6],
            phone=row[7],
            last_login=datetime.fromisoformat(row[8]) if row[8] else None,
            is_active=bool(row[9])
        )

# Similar implementations for other repositories...
# SQLiteGuestRepository, SQLiteRoomRepository, etc.

# --------------------------
# Security Service
# --------------------------
class SecurityService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.user_repo.get_by_username(username)
        if not user or not user.is_active:
            return None
        
        if not self._verify_password(password, user.password_hash, user.salt):
            return None
        
        # Update last login
        user.last_login = datetime.now()
        self.user_repo.update(user)
        
        return user
    
    def create_user(self, username: str, password: str, role: UserRole, 
                  full_name: str, email: str, phone: str) -> User:
        if not self._validate_username(username):
            raise ValueError("Invalid username format")
        
        if not self._validate_password(password):
            raise ValueError("Password must be at least 8 characters")
        
        salt = self._generate_salt()
        password_hash = self._hash_password(password, salt)
        
        user = User(
            user_id=0,
            username=username,
            password_hash=password_hash,
            salt=salt,
            role=role,
            full_name=full_name,
            email=email,
            phone=phone,
            last_login=None,
            is_active=True
        )
        
        return self.user_repo.add(user)
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        if not self._verify_password(current_password, user.password_hash, user.salt):
            return False
        
        if not self._validate_password(new_password):
            raise ValueError("Password must be at least 8 characters")
        
        new_salt = self._generate_salt()
        new_hash = self._hash_password(new_password, new_salt)
        
        user.password_hash = new_hash
        user.salt = new_salt
        self.user_repo.update(user)
        return True
    
    def _generate_salt(self) -> str:
        return secrets.token_hex(16)
    
    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
    
    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        new_hash = self._hash_password(password, salt)
        return secrets.compare_digest(stored_hash, new_hash)
    
    def _validate_username(self, username: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9_]{4,20}$', username))
    
    def _validate_password(self, password: str) -> bool:
        return len(password) >= 8

# --------------------------
# Hotel Management Service
# --------------------------
class HotelService:
    def __init__(self, 
                 room_repo: IRoomRepository,
                 booking_repo: IBookingRepository,
                 guest_repo: IGuestRepository):
        self.room_repo = room_repo
        self.booking_repo = booking_repo
        self.guest_repo = guest_repo
    
    def check_room_availability(self, 
                              start_date: date, 
                              end_date: date, 
                              room_type: Optional[RoomType] = None) -> List[Room]:
        return self.room_repo.list_available(start_date, end_date, room_type)
    
    def make_booking(self, 
                    guest_id: int,
                    room_id: int,
                    check_in_date: date,
                    check_out_date: date,
                    special_requests: str = "") -> Booking:
        # Validate dates
        if check_in_date >= check_out_date:
            raise ValueError("Check-out date must be after check-in date")
        
        if check_in_date < date.today():
            raise ValueError("Check-in date cannot be in the past")
        
        # Check room availability
        available_rooms = self.room_repo.list_available(check_in_date, check_out_date)
        if not any(room.room_id == room_id for room in available_rooms):
            raise ValueError("Room is not available for the selected dates")
        
        # Get room details
        room = self.room_repo.get_by_id(room_id)
        if not room:
            raise ValueError("Room not found")
        
        # Calculate duration and total amount
        duration = (check_out_date - check_in_date).days
        total_amount = duration * room.rate_per_night
        
        # Create booking
        booking = Booking(
            booking_id=0,
            guest_id=guest_id,
            room_id=room_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            booking_date=datetime.now(),
            status=BookingStatus.CONFIRMED,
            total_amount=total_amount,
            payment_method=None,
            special_requests=special_requests
        )
        
        return self.booking_repo.add(booking)
    
    def cancel_booking(self, booking_id: int) -> bool:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            return False
        
        if booking.status != BookingStatus.CONFIRMED:
            return False
        
        if booking.check_in_date <= date.today():
            return False
        
        booking.status = BookingStatus.CANCELLED
        self.booking_repo.update(booking)
        return True
    
    def check_in(self, booking_id: int) -> bool:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            return False
        
        if booking.status != BookingStatus.CONFIRMED:
            return False
        
        if booking.check_in_date != date.today():
            return False
        
        booking.status = BookingStatus.CHECKED_IN
        self.booking_repo.update(booking)
        
        # Mark room as unavailable
        room = self.room_repo.get_by_id(booking.room_id)
        if room:
            room.is_available = False
            self.room_repo.update(room)
        
        return True
    
    def check_out(self, booking_id: int, payment_method: PaymentMethod) -> bool:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            return False
        
        if booking.status != BookingStatus.CHECKED_IN:
            return False
        
        booking.status = BookingStatus.CHECKED_OUT
        booking.payment_method = payment_method
        self.booking_repo.update(booking)
        
        # Mark room as available
        room = self.room_repo.get_by_id(booking.room_id)
        if room:
            room.is_available = True
            self.room_repo.update(room)
        
        return True

# --------------------------
# Database Initialization
# --------------------------
def initialize_database(db_path: str = "hotel.db"):
    conn = sqlite3.connect(db_path)
    
    # Create tables
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        last_login TEXT,
        is_active BOOLEAN DEFAULT 1
    )''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS guests (
        guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT NOT NULL,
        address TEXT,
        id_proof TEXT NOT NULL,
        registration_date TEXT NOT NULL,
        loyalty_points INTEGER DEFAULT 0
    )''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS rooms (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT UNIQUE NOT NULL,
        room_type TEXT NOT NULL,
        floor INTEGER NOT NULL,
        capacity INTEGER NOT NULL,
        amenities TEXT,  -- JSON array
        rate_per_night REAL NOT NULL,
        is_available BOOLEAN DEFAULT 1,
        last_maintenance_date TEXT
    )''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        check_in_date TEXT NOT NULL,
        check_out_date TEXT NOT NULL,
        booking_date TEXT NOT NULL,
        status TEXT NOT NULL,
        total_amount REAL NOT NULL,
        payment_method TEXT,
        special_requests TEXT,
        FOREIGN KEY (guest_id) REFERENCES guests (guest_id),
        FOREIGN KEY (room_id) REFERENCES rooms (room_id)
    )''')
    
    # Create admin user if not exists
    security = SecurityService(SQLiteUserRepository(conn))
    if not security.authenticate("admin", "admin123"):
        security.create_user(
            username="admin",
            password="admin123",
            role=UserRole.ADMIN,
            full_name="System Administrator",
            email="admin@hotel.com",
            phone="1234567890"
        )
    
    conn.commit()
    conn.close()

# --------------------------
# CLI Interface
# --------------------------
class HotelCLI:
    def __init__(self):
        self.db = sqlite3.connect("hotel.db")
        self.user_repo = SQLiteUserRepository(self.db)
        self.security = SecurityService(self.user_repo)
        self.current_user = None
    
    def run(self):
        print("Hotel Management System")
        print("----------------------")
        
        if not self._login():
            return
        
        while True:
            self._show_main_menu()
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self._manage_bookings()
            elif choice == '2':
                self._manage_rooms()
            elif choice == '3' and self.current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
                self._manage_users()
            elif choice == '4':
                self._change_password()
            elif choice.lower() == 'x':
                print("Exiting system...")
                break
            else:
                print("Invalid choice!")
    
    def _login(self) -> bool:
        print("\nLogin")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        
        self.current_user = self.security.authenticate(username, password)
        if self.current_user:
            print(f"\nWelcome, {self.current_user.full_name} ({self.current_user.role.name})!")
            return True
        else:
            print("Invalid credentials!")
            return False
    
    def _show_main_menu(self):
        print("\nMain Menu")
        print("1. Manage Bookings")
        print("2. Manage Rooms")
        if self.current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
            print("3. Manage Users")
        print("4. Change Password")
        print("X. Exit")
    
    def _manage_bookings(self):
        # Implementation for booking management
        pass
    
    def _manage_rooms(self):
        # Implementation for room management
        pass
    
    def _manage_users(self):
        # Implementation for user management
        pass
    
    def _change_password(self):
        print("\nChange Password")
        current = getpass.getpass("Current password: ")
        new = getpass.getpass("New password: ")
        confirm = getpass.getpass("Confirm new password: ")
        
        if new != confirm:
            print("Passwords don't match!")
            return
        
        try:
            if self.security.change_password(self.current_user.user_id, current, new):
                print("Password changed successfully!")
            else:
                print("Current password is incorrect!")
        except ValueError as e:
            print(f"Error: {e}")

# --------------------------
# Main Application
# --------------------------
if __name__ == "__main__":
    # Initialize database
    initialize_database()
    
    # Run the CLI
    try:
        cli = HotelCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if hasattr(cli, 'db'):
            cli.db.close()