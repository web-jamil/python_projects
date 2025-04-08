
import sqlite3
from datetime import datetime
from tabulate import tabulate
import hashlib
import getpass
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import re
from dataclasses import dataclass

# --------------------------
# Database Layer (Singleton)
# --------------------------
class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = sqlite3.connect('hospital.db')
            cls._instance.cursor = cls._instance.conn.cursor()
            cls._instance.initialize_db()
        return cls._instance
    
    def initialize_db(self):
        """Initialize database tables with proper constraints"""
        tables = [
            '''CREATE TABLE IF NOT EXISTS Departments (
                department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                head_doctor_id INTEGER
            )''',
            
            '''CREATE TABLE IF NOT EXISTS Staff (
                staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                hire_date TEXT NOT NULL,
                department_id INTEGER,
                position TEXT NOT NULL,
                salary REAL NOT NULL,
                FOREIGN KEY (department_id) REFERENCES Departments(department_id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS Doctors (
                doctor_id INTEGER PRIMARY KEY,
                specialization TEXT NOT NULL,
                license_number TEXT UNIQUE NOT NULL,
                FOREIGN KEY (doctor_id) REFERENCES Staff(staff_id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS Patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                dob TEXT NOT NULL,
                gender TEXT CHECK(gender IN ('M', 'F', 'O')),
                blood_type TEXT,
                address TEXT,
                phone TEXT NOT NULL,
                email TEXT UNIQUE,
                registration_date TEXT NOT NULL
            )''',
            
            '''CREATE TABLE IF NOT EXISTS Appointments (
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                status TEXT DEFAULT 'Scheduled' CHECK(status IN ('Scheduled', 'Completed', 'Cancelled')),
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS MedicalRecords (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                diagnosis TEXT NOT NULL,
                treatment TEXT,
                prescription TEXT,
                record_date TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS Billing (
                bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                date_issued TEXT NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Paid', 'Overdue')),
                payment_method TEXT,
                FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS Rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT UNIQUE NOT NULL,
                room_type TEXT NOT NULL,
                department_id INTEGER,
                status TEXT DEFAULT 'Available' CHECK(status IN ('Available', 'Occupied', 'Maintenance')),
                FOREIGN KEY (department_id) REFERENCES Departments(department_id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS Admissions (
                admission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                admission_date TEXT NOT NULL,
                discharge_date TEXT,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Discharged', 'Transferred')),
                FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
                FOREIGN KEY (room_id) REFERENCES Rooms(room_id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                staff_id INTEGER UNIQUE,
                role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'nurse', 'receptionist', 'accountant')),
                last_login TEXT,
                FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
            )'''
        ]
        
        for table in tables:
            self.cursor.execute(table)
        
        # Create admin user if not exists
        self.cursor.execute("SELECT COUNT(*) FROM Users WHERE username='admin'")
        if self.cursor.fetchone()[0] == 0:
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute('''
            INSERT INTO Users (username, password_hash, role)
            VALUES (?, ?, ?)
            ''', ('admin', password_hash, 'admin'))
        
        self.conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL query with parameters"""
        try:
            return self.cursor.execute(query, params)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
    
    def commit(self):
        """Commit changes to the database"""
        self.conn.commit()
    
    def close(self):
        """Close the database connection"""
        self.conn.close()

# --------------------------
# Domain Models
# --------------------------
@dataclass
class Department:
    department_id: int
    name: str
    description: str
    head_doctor_id: Optional[int]

@dataclass
class Staff:
    staff_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    hire_date: str
    department_id: Optional[int]
    position: str
    salary: float

@dataclass
class Doctor(Staff):
    specialization: str
    license_number: str

@dataclass
class Patient:
    patient_id: int
    first_name: str
    last_name: str
    dob: str
    gender: str
    blood_type: Optional[str]
    address: str
    phone: str
    email: Optional[str]
    registration_date: str

@dataclass
class Appointment:
    appointment_id: int
    patient_id: int
    doctor_id: int
    appointment_date: str
    start_time: str
    end_time: str
    status: str
    notes: Optional[str]

@dataclass
class MedicalRecord:
    record_id: int
    patient_id: int
    doctor_id: int
    diagnosis: str
    treatment: Optional[str]
    prescription: Optional[str]
    record_date: str

@dataclass
class Billing:
    bill_id: int
    patient_id: int
    amount: float
    date_issued: str
    due_date: str
    status: str
    payment_method: Optional[str]

@dataclass
class Room:
    room_id: int
    room_number: str
    room_type: str
    department_id: Optional[int]
    status: str

@dataclass
class Admission:
    admission_id: int
    patient_id: int
    room_id: int
    admission_date: str
    discharge_date: Optional[str]
    reason: str
    status: str

@dataclass
class User:
    user_id: int
    username: str
    password_hash: str
    staff_id: Optional[int]
    role: str
    last_login: Optional[str]

# --------------------------
# Repository Pattern
# --------------------------
class Repository(ABC):
    @abstractmethod
    def get_by_id(self, id: int):
        pass
    
    @abstractmethod
    def get_all(self) -> List:
        pass
    
    @abstractmethod
    def add(self, entity):
        pass
    
    @abstractmethod
    def update(self, entity):
        pass
    
    @abstractmethod
    def delete(self, id: int):
        pass

class DepartmentRepository(Repository):
    def get_by_id(self, department_id: int) -> Optional[Department]:
        db = Database()
        cursor = db.execute_query('''
        SELECT department_id, name, description, head_doctor_id 
        FROM Departments WHERE department_id=?
        ''', (department_id,))
        row = cursor.fetchone()
        return Department(*row) if row else None
    
    def get_all(self) -> List[Department]:
        db = Database()
        cursor = db.execute_query('''
        SELECT department_id, name, description, head_doctor_id FROM Departments
        ''')
        return [Department(*row) for row in cursor.fetchall()]
    
    def add(self, department: Department) -> Department:
        db = Database()
        cursor = db.execute_query('''
        INSERT INTO Departments (name, description, head_doctor_id)
        VALUES (?, ?, ?)
        ''', (department.name, department.description, department.head_doctor_id))
        db.commit()
        department.department_id = cursor.lastrowid
        return department
    
    def update(self, department: Department):
        db = Database()
        db.execute_query('''
        UPDATE Departments SET name=?, description=?, head_doctor_id=?
        WHERE department_id=?
        ''', (department.name, department.description, department.head_doctor_id, department.department_id))
        db.commit()
    
    def delete(self, department_id: int):
        db = Database()
        db.execute_query("DELETE FROM Departments WHERE department_id=?", (department_id,))
        db.commit()

class DoctorRepository(Repository):
    def get_by_id(self, doctor_id: int) -> Optional[Doctor]:
        db = Database()
        cursor = db.execute_query('''
        SELECT s.staff_id, s.first_name, s.last_name, s.email, s.phone, s.address, 
               s.hire_date, s.department_id, s.position, s.salary,
               d.specialization, d.license_number
        FROM Staff s
        JOIN Doctors d ON s.staff_id = d.doctor_id
        WHERE s.staff_id=?
        ''', (doctor_id,))
        row = cursor.fetchone()
        return Doctor(*row) if row else None
    
    def get_all(self) -> List[Doctor]:
        db = Database()
        cursor = db.execute_query('''
        SELECT s.staff_id, s.first_name, s.last_name, s.email, s.phone, s.address, 
               s.hire_date, s.department_id, s.position, s.salary,
               d.specialization, d.license_number
        FROM Staff s
        JOIN Doctors d ON s.staff_id = d.doctor_id
        ''')
        return [Doctor(*row) for row in cursor.fetchall()]
    
    def add(self, doctor: Doctor) -> Doctor:
        db = Database()
        
        # First add to Staff table
        cursor = db.execute_query('''
        INSERT INTO Staff (
            first_name, last_name, email, phone, address, 
            hire_date, department_id, position, salary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            doctor.first_name, doctor.last_name, doctor.email, doctor.phone, doctor.address,
            doctor.hire_date, doctor.department_id, doctor.position, doctor.salary
        ))
        staff_id = cursor.lastrowid
        
        # Then add to Doctors table
        db.execute_query('''
        INSERT INTO Doctors (doctor_id, specialization, license_number)
        VALUES (?, ?, ?)
        ''', (staff_id, doctor.specialization, doctor.license_number))
        
        db.commit()
        doctor.staff_id = staff_id
        return doctor
    
    def update(self, doctor: Doctor):
        db = Database()
        
        # Update Staff table
        db.execute_query('''
        UPDATE Staff SET 
            first_name=?, last_name=?, email=?, phone=?, address=?,
            hire_date=?, department_id=?, position=?, salary=?
        WHERE staff_id=?
        ''', (
            doctor.first_name, doctor.last_name, doctor.email, doctor.phone, doctor.address,
            doctor.hire_date, doctor.department_id, doctor.position, doctor.salary,
            doctor.staff_id
        ))
        
        # Update Doctors table
        db.execute_query('''
        UPDATE Doctors SET specialization=?, license_number=?
        WHERE doctor_id=?
        ''', (doctor.specialization, doctor.license_number, doctor.staff_id))
        
        db.commit()
    
    def delete(self, doctor_id: int):
        db = Database()
        db.execute_query("DELETE FROM Doctors WHERE doctor_id=?", (doctor_id,))
        db.execute_query("DELETE FROM Staff WHERE staff_id=?", (doctor_id,))
        db.commit()

# Other repositories would follow the same pattern...
# (PatientRepository, AppointmentRepository, etc.)

# --------------------------
# Services Layer
# --------------------------
class HospitalService:
    def __init__(self):
        self.department_repo = DepartmentRepository()
        self.doctor_repo = DoctorRepository()
        # Initialize other repositories as needed
    
    def add_department(self, name: str, description: str, head_doctor_id: Optional[int] = None) -> Department:
        """Add a new department to the hospital"""
        if not name:
            raise ValueError("Department name cannot be empty")
        
        department = Department(
            department_id=None,
            name=name,
            description=description,
            head_doctor_id=head_doctor_id
        )
        
        return self.department_repo.add(department)
    
    def assign_head_doctor(self, department_id: int, doctor_id: int):
        """Assign a doctor as head of a department"""
        department = self.department_repo.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")
        
        doctor = self.doctor_repo.get_by_id(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        
        department.head_doctor_id = doctor_id
        self.department_repo.update(department)
    
    def get_available_doctors(self, date: str, time: str) -> List[Doctor]:
        """Get doctors available at a specific date and time"""
        # Implementation would check against appointments
        pass
    
    # Additional service methods would go here...

# --------------------------
# Authentication Service
# --------------------------
class AuthService:
    def __init__(self):
        self.db = Database()
    
    def login(self, username: str, password: str) -> Optional[User]:
        """Authenticate user and return user object if successful"""
        cursor = self.db.execute_query('''
        SELECT user_id, username, password_hash, staff_id, role, last_login
        FROM Users WHERE username=?
        ''', (username,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        user = User(*row)
        if user.password_hash != hashlib.sha256(password.encode()).hexdigest():
            return None
        
        # Update last login
        self.db.execute_query('''
        UPDATE Users SET last_login=?
        WHERE user_id=?
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user.user_id))
        self.db.commit()
        
        return user
    
    def create_user(self, username: str, password: str, role: str, staff_id: Optional[int] = None) -> User:
        """Create a new system user"""
        if not self._validate_username(username):
            raise ValueError("Invalid username format")
        
        if not self._validate_password(password):
            raise ValueError("Password must be at least 8 characters")
        
        if role not in ['admin', 'doctor', 'nurse', 'receptionist', 'accountant']:
            raise ValueError("Invalid role")
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor = self.db.execute_query('''
        INSERT INTO Users (username, password_hash, staff_id, role)
        VALUES (?, ?, ?, ?)
        ''', (username, password_hash, staff_id, role))
        self.db.commit()
        
        return User(
            user_id=cursor.lastrowid,
            username=username,
            password_hash=password_hash,
            staff_id=staff_id,
            role=role,
            last_login=None
        )
    
    def _validate_username(self, username: str) -> bool:
        """Validate username format"""
        return bool(re.match(r'^[a-zA-Z0-9_]{4,20}$', username))
    
    def _validate_password(self, password: str) -> bool:
        """Validate password strength"""
        return len(password) >= 8

# --------------------------
# UI Layer (Console)
# --------------------------
class HospitalUI:
    def __init__(self):
        self.auth_service = AuthService()
        self.hospital_service = HospitalService()
        self.current_user = None
    
    def run(self):
        """Main application loop"""
        print("Hospital Management System")
        print("------------------------")
        
        if not self._login():
            return
        
        while True:
            self._show_main_menu()
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self._department_management()
            elif choice == '2':
                self._staff_management()
            elif choice == '3':
                self._patient_management()
            elif choice == '4':
                self._appointment_management()
            elif choice == '5' and self.current_user.role == 'admin':
                self._user_management()
            elif choice.lower() == 'x':
                print("Exiting system...")
                break
            else:
                print("Invalid choice!")
    
    def _login(self) -> bool:
        """Handle user login"""
        print("\nLogin")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        
        self.current_user = self.auth_service.login(username, password)
        if self.current_user:
            print(f"\nWelcome, {self.current_user.username} ({self.current_user.role})!")
            return True
        else:
            print("Invalid credentials!")
            return False
    
    def _show_main_menu(self):
        """Display main menu based on user role"""
        print("\nMain Menu")
        print("1. Department Management")
        print("2. Staff Management")
        print("3. Patient Management")
        print("4. Appointment Management")
        
        if self.current_user.role == 'admin':
            print("5. User Management")
        
        print("X. Exit")
    
    def _department_management(self):
        """Handle department operations"""
        while True:
            print("\nDepartment Management")
            print("1. List Departments")
            print("2. Add Department")
            print("3. Update Department")
            print("4. Assign Head Doctor")
            print("5. Back to Main Menu")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self._list_departments()
            elif choice == '2':
                self._add_department()
            elif choice == '3':
                self._update_department()
            elif choice == '4':
                self._assign_head_doctor()
            elif choice == '5':
                break
            else:
                print("Invalid choice!")
    
    def _list_departments(self):
        """Display all departments"""
        departments = self.hospital_service.department_repo.get_all()
        
        if not departments:
            print("No departments found!")
            return
        
        headers = ["ID", "Name", "Description", "Head Doctor"]
        data = []
        for dept in departments:
            head_doctor = "None"
            if dept.head_doctor_id:
                doctor = self.hospital_service.doctor_repo.get_by_id(dept.head_doctor_id)
                head_doctor = f"{doctor.first_name} {doctor.last_name}" if doctor else "Unknown"
            
            data.append([
                dept.department_id, dept.name, 
                dept.description[:50] + "..." if len(dept.description) > 50 else dept.description,
                head_doctor
            ])
        
        print("\nHospital Departments:")
        print(tabulate(data, headers=headers, tablefmt="grid"))
    
    def _add_department(self):
        """Add a new department"""
        print("\nAdd New Department")
        name = input("Department Name: ")
        description = input("Description: ")
        
        try:
            department = self.hospital_service.add_department(name, description)
            print(f"Department '{department.name}' added successfully with ID: {department.department_id}")
        except ValueError as e:
            print(f"Error: {e}")
    
    def _update_department(self):
        """Update department details"""
        department_id = input("Enter Department ID to update: ")
        
        try:
            department_id = int(department_id)
            department = self.hospital_service.department_repo.get_by_id(department_id)
            
            if not department:
                print("Department not found!")
                return
            
            print("\nCurrent Department Details:")
            print(f"Name: {department.name}")
            print(f"Description: {department.description}")
            print(f"Head Doctor ID: {department.head_doctor_id or 'Not assigned'}")
            
            print("\nEnter new details (leave blank to keep current):")
            new_name = input(f"Name [{department.name}]: ") or department.name
            new_desc = input(f"Description [{department.description}]: ") or department.description
            
            department.name = new_name
            department.description = new_desc
            self.hospital_service.department_repo.update(department)
            print("Department updated successfully!")
        except ValueError:
            print("Invalid Department ID!")
    
    def _assign_head_doctor(self):
        """Assign a head doctor to a department"""
        department_id = input("Enter Department ID: ")
        doctor_id = input("Enter Doctor ID: ")
        
        try:
            department_id = int(department_id)
            doctor_id = int(doctor_id)
            
            self.hospital_service.assign_head_doctor(department_id, doctor_id)
            print("Head doctor assigned successfully!")
        except ValueError as e:
            print(f"Error: {e}")
    
    # Other UI methods would follow similar patterns...
    # _staff_management(), _patient_management(), etc.

# --------------------------
# Main Application
# --------------------------
if __name__ == "__main__":
    try:
        app = HospitalUI()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure database connection is closed
        Database().close()




