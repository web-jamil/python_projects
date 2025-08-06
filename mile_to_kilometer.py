import json
import sqlite3
import hashlib
import os
import secrets
import string
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

# Configuration Management
class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.CONFIG_FILE = "converter_config.json"
        self._config = self._load_config()
    
    def _load_config(self) -> Dict:
        default_config = {
            "database": "converter.db",
            "session_timeout": 1800,  # 30 minutes in seconds
            "password_salt_length": 32,
            "password_min_length": 8,
            "max_login_attempts": 5,
            "lockout_time": 300  # 5 minutes in seconds
        }
        
        try:
            with open(self.CONFIG_FILE, "r") as f:
                loaded_config = json.load(f)
                return {**default_config, **loaded_config}
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(default_config, f, indent=4)
            return default_config
    
    @property
    def config(self) -> Dict:
        return self._config
    
    def update_config(self, new_settings: Dict) -> None:
        self._config = {**self._config, **new_settings}
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self._config, f, indent=4)

# Database Abstraction Layer
class DatabaseConnection:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
            self.connection.close()

# Abstract Base Classes
class Authenticator(ABC):
    @abstractmethod
    def authenticate(self, username: str, password: str) -> bool:
        pass

class UserRepository(ABC):
    @abstractmethod
    def create_user(self, username: str, password_hash: str, salt: str) -> bool:
        pass
    
    @abstractmethod
    def get_user(self, username: str) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def update_last_login(self, user_id: int) -> None:
        pass
    
    @abstractmethod
    def record_failed_attempt(self, username: str) -> None:
        pass
    
    @abstractmethod
    def is_locked_out(self, username: str) -> bool:
        pass

class ConversionRepository(ABC):
    @abstractmethod
    def record_conversion(self, user_id: int, miles: float, kilometers: float) -> None:
        pass
    
    @abstractmethod
    def get_conversion_history(self, user_id: int) -> List[Dict]:
        pass

# Concrete Implementations
class SQLiteUserRepository(UserRepository):
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        with self.db_connection as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT,
                failed_attempts INTEGER DEFAULT 0,
                last_failed_attempt TEXT
            )
            """)
            
            conn.execute("""
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                login_time TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)
    
    def create_user(self, username: str, password_hash: str, salt: str) -> bool:
        try:
            with self.db_connection as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
                    (username, password_hash, salt, datetime.now().isoformat())
                )
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        with self.db_connection as conn:
            cursor = conn.execute(
                "SELECT id, username, password_hash, salt, failed_attempts, last_failed_attempt FROM users WHERE username = ?",
                (username,)
            )
            return dict(cursor.fetchone()) if cursor.fetchone() else None
    
    def update_last_login(self, user_id: int) -> None:
        with self.db_connection as conn:
            conn.execute(
                "UPDATE users SET last_login = ?, failed_attempts = 0 WHERE id = ?",
                (datetime.now().isoformat(), user_id)
            )
    
    def record_failed_attempt(self, username: str) -> None:
        with self.db_connection as conn:
            conn.execute(
                """UPDATE users 
                SET failed_attempts = failed_attempts + 1, 
                    last_failed_attempt = ?
                WHERE username = ?""",
                (datetime.now().isoformat(), username)
            )
    
    def is_locked_out(self, username: str) -> bool:
        config = ConfigManager().config
        with self.db_connection as conn:
            cursor = conn.execute(
                """SELECT failed_attempts, last_failed_attempt 
                FROM users 
                WHERE username = ?""",
                (username,)
            )
            user_data = cursor.fetchone()
            
            if not user_data:
                return False
                
            attempts = user_data['failed_attempts']
            last_attempt = datetime.fromisoformat(user_data['last_failed_attempt']) if user_data['last_failed_attempt'] else None
            
            if attempts >= config['max_login_attempts'] and last_attempt:
                time_since_last_attempt = (datetime.now() - last_attempt).total_seconds()
                return time_since_last_attempt < config['lockout_time']
            
            return False

class SQLiteConversionRepository(ConversionRepository):
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        with self.db_connection as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                miles REAL NOT NULL,
                kilometers REAL NOT NULL,
                converted_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)
    
    def record_conversion(self, user_id: int, miles: float, kilometers: float) -> None:
        with self.db_connection as conn:
            conn.execute(
                "INSERT INTO conversions (user_id, miles, kilometers, converted_at) VALUES (?, ?, ?, ?)",
                (user_id, miles, kilometers, datetime.now().isoformat())
            )
    
    def get_conversion_history(self, user_id: int) -> List[Dict]:
        with self.db_connection as conn:
            cursor = conn.execute(
                "SELECT miles, kilometers, converted_at FROM conversions WHERE user_id = ? ORDER BY converted_at DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

# Security Components
class PasswordHasher:
    def __init__(self):
        self.config = ConfigManager().config
    
    def generate_salt(self) -> str:
        return secrets.token_hex(self.config['password_salt_length'])
    
    def hash_password(self, password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
    
    def validate_password(self, password: str, stored_hash: str, salt: str) -> bool:
        return self.hash_password(password, salt) == stored_hash

# User Management
class UserManager:
    def __init__(self, user_repo: UserRepository, password_hasher: PasswordHasher):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.current_user = None
    
    def register(self, username: str, password: str) -> Tuple[bool, str]:
        if len(password) < ConfigManager().config['password_min_length']:
            return False, f"Password must be at least {ConfigManager().config['password_min_length']} characters"
        
        salt = self.password_hasher.generate_salt()
        password_hash = self.password_hasher.hash_password(password, salt)
        
        if self.user_repo.create_user(username, password_hash, salt):
            return True, "Registration successful"
        return False, "Username already exists"
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        if self.user_repo.is_locked_out(username):
            return False, "Account temporarily locked due to too many failed attempts"
        
        user = self.user_repo.get_user(username)
        if not user:
            return False, "Invalid username or password"
        
        if not self.password_hasher.validate_password(password, user['password_hash'], user['salt']):
            self.user_repo.record_failed_attempt(username)
            return False, "Invalid username or password"
        
        self.user_repo.update_last_login(user['id'])
        self.current_user = {
            'id': user['id'],
            'username': user['username']
        }
        return True, "Login successful"
    
    def logout(self) -> None:
        self.current_user = None
    
    @property
    def is_authenticated(self) -> bool:
        return self.current_user is not None

# Conversion Service
class ConversionService:
    def __init__(self, conversion_repo: ConversionRepository):
        self.conversion_repo = conversion_repo
    
    def miles_to_km(self, miles: float) -> float:
        return miles * 1.60934
    
    def record_conversion(self, user_id: int, miles: float) -> float:
        kilometers = self.miles_to_km(miles)
        self.conversion_repo.record_conversion(user_id, miles, kilometers)
        return kilometers
    
    def get_history(self, user_id: int) -> List[Dict]:
        return self.conversion_repo.get_conversion_history(user_id)

# Application Core
class Application:
    def __init__(self):
        config = ConfigManager().config
        self.db_connection = DatabaseConnection(config['database'])
        
        # Initialize repositories
        user_repo = SQLiteUserRepository(self.db_connection)
        conversion_repo = SQLiteConversionRepository(self.db_connection)
        
        # Initialize services
        self.password_hasher = PasswordHasher()
        self.user_manager = UserManager(user_repo, self.password_hasher)
        self.conversion_service = ConversionService(conversion_repo)
    
    def run(self):
        while True:
            self._display_menu()
            choice = input("Enter your choice: ")
            
            if choice == "1":
                self._handle_login()
            elif choice == "2":
                self._handle_registration()
            elif choice == "3":
                self._handle_conversion()
            elif choice == "4":
                self._handle_history()
            elif choice == "5":
                self._handle_logout()
            elif choice == "6":
                if self.user_manager.is_authenticated and self.user_manager.current_user['username'] == 'admin':
                    self._handle_admin()
                else:
                    print("Invalid choice. Please try again.")
            elif choice == "7":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _display_menu(self):
        print("\n=== Mile to Kilometer Converter ===")
        print("1. Login")
        print("2. Register")
        print("3. Convert Miles to Kilometers")
        print("4. View Conversion History")
        print("5. Logout")
        if self.user_manager.is_authenticated and self.user_manager.current_user['username'] == 'admin':
            print("6. Admin Panel")
        print("7. Exit")
        
        if self.user_manager.is_authenticated:
            print(f"\nLogged in as: {self.user_manager.current_user['username']}")
    
    def _handle_login(self):
        if self.user_manager.is_authenticated:
            print("You are already logged in.")
            return
        
        username = input("Username: ")
        password = input("Password: ")
        
        success, message = self.user_manager.login(username, password)
        print(message)
    
    def _handle_registration(self):
        if self.user_manager.is_authenticated:
            print("Please logout first to register a new account.")
            return
        
        username = input("Choose a username: ")
        password = input("Choose a password: ")
        
        success, message = self.user_manager.register(username, password)
        print(message)
    
    def _handle_conversion(self):
        if not self.user_manager.is_authenticated:
            print("Please login to perform conversions.")
            return
        
        try:
            miles = float(input("Enter miles to convert: "))
            kilometers = self.conversion_service.record_conversion(
                self.user_manager.current_user['id'], miles
            )
            print(f"{miles} miles = {kilometers:.2f} kilometers")
        except ValueError:
            print("Please enter a valid number.")
    
    def _handle_history(self):
        if not self.user_manager.is_authenticated:
            print("Please login to view your history.")
            return
        
        history = self.conversion_service.get_history(self.user_manager.current_user['id'])
        if not history:
            print("No conversion history found.")
        else:
            print("\n=== Conversion History ===")
            for entry in history:
                print(f"{entry['converted_at']}: {entry['miles']} miles = {entry['kilometers']:.2f} km")
    
    def _handle_logout(self):
        if self.user_manager.is_authenticated:
            self.user_manager.logout()
            print("Logged out successfully.")
        else:
            print("You're not logged in.")
    
    def _handle_admin(self):
        print("\n=== Admin Panel ===")
        print("1. View all users")
        print("2. View system configuration")
        print("3. Back to main menu")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            self._view_all_users()
        elif choice == "2":
            self._view_system_config()
        elif choice == "3":
            return
        else:
            print("Invalid choice.")
    
    def _view_all_users(self):
        with self.db_connection as conn:
            cursor = conn.execute("SELECT id, username, created_at, last_login FROM users")
            users = cursor.fetchall()
            
            if not users:
                print("No users found.")
                return
            
            print("\n=== All Users ===")
            for user in users:
                print(f"ID: {user['id']}, Username: {user['username']}, Created: {user['created_at']}, Last Login: {user['last_login']}")
    
    def _view_system_config(self):
        config = ConfigManager().config
        print("\n=== System Configuration ===")
        for key, value in config.items():
            print(f"{key}: {value}")

# Main Entry Point
if __name__ == "__main__":
    app = Application()
    app.run()