import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import sqlite3
import hashlib
import secrets
from datetime import datetime
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
            "session_timeout": 1800,
            "password_salt_length": 32,
            "password_min_length": 8,
            "max_login_attempts": 5,
            "lockout_time": 300,
            "theme": "clam",
            "font": ("Arial", 10)
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

# Database Connection
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

# Password Hashing
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

# User Repository
class UserRepository:
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
            row = cursor.fetchone()
            return dict(row) if row else None
    
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
        user = self.get_user(username)
        
        if not user:
            return False
            
        attempts = user['failed_attempts']
        last_attempt = datetime.fromisoformat(user['last_failed_attempt']) if user['last_failed_attempt'] else None
        
        if attempts >= config['max_login_attempts'] and last_attempt:
            time_since_last_attempt = (datetime.now() - last_attempt).total_seconds()
            return time_since_last_attempt < config['lockout_time']
        
        return False

# Conversion Repository
class ConversionRepository:
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

# User Manager
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

# GUI Application
class MileToKmConverterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = ConfigManager()
        self.setup_ui()
        
        # Initialize database and services
        self.db_connection = DatabaseConnection(self.config.config['database'])
        self.password_hasher = PasswordHasher()
        self.user_repo = UserRepository(self.db_connection)
        self.conversion_repo = ConversionRepository(self.db_connection)
        
        self.user_manager = UserManager(self.user_repo, self.password_hasher)
        self.conversion_service = ConversionService(self.conversion_repo)
        
        # Start with login screen
        self.show_login_screen()
    
    def setup_ui(self):
        self.root.title("Mile to Kilometer Converter")
        self.root.geometry("600x400")
        
        # Apply theme
        style = ttk.Style()
        style.theme_use(self.config.config['theme'])
        
        # Configure fonts
        style.configure('.', font=self.config.config['font'])
        style.configure('TButton', padding=5)
        style.configure('TEntry', padding=5)
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.update_status("Ready")
    
    def update_status(self, message: str):
        self.status_var.set(message)
    
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Login", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.main_frame, text="Username:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.username_entry = ttk.Entry(self.main_frame)
        self.username_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.main_frame, text="Password:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.main_frame, show="*")
        self.password_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(
            self.main_frame, 
            text="Login", 
            command=self.handle_login
        ).grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            self.main_frame, 
            text="Register", 
            command=self.show_register_screen
        ).grid(row=4, column=0, columnspan=2, pady=5)
        
        self.username_entry.focus()
    
    def show_register_screen(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Register", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.main_frame, text="Username:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.reg_username_entry = ttk.Entry(self.main_frame)
        self.reg_username_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.main_frame, text="Password:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.reg_password_entry = ttk.Entry(self.main_frame, show="*")
        self.reg_password_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.main_frame, text=f"(Minimum {self.config.config['password_min_length']} characters)").grid(row=3, column=1, sticky=tk.W)
        
        ttk.Button(
            self.main_frame, 
            text="Register", 
            command=self.handle_register
        ).grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            self.main_frame, 
            text="Back to Login", 
            command=self.show_login_screen
        ).grid(row=5, column=0, columnspan=2, pady=5)
        
        self.reg_username_entry.focus()
    
    def show_main_screen(self):
        self.clear_frame()
        
        # Menu bar
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Logout", command=self.handle_logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Conversion History", command=self.show_history)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Admin menu (if admin)
        if self.user_manager.current_user['username'] == "admin":
            admin_menu = tk.Menu(menubar, tearoff=0)
            admin_menu.add_command(label="View Users", command=self.show_all_users)
            admin_menu.add_command(label="System Config", command=self.show_system_config)
            menubar.add_cascade(label="Admin", menu=admin_menu)
        
        self.root.config(menu=menubar)
        
        # Main content
        ttk.Label(self.main_frame, text="Mile to Kilometer Converter", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.main_frame, text="Miles:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.miles_entry = ttk.Entry(self.main_frame)
        self.miles_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(
            self.main_frame, 
            text="Convert", 
            command=self.handle_conversion
        ).grid(row=2, column=0, columnspan=2, pady=10)
        
        self.result_var = tk.StringVar()
        ttk.Label(self.main_frame, textvariable=self.result_var, font=("Arial", 12)).grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            self.main_frame, 
            text="View History", 
            command=self.show_history
        ).grid(row=4, column=0, columnspan=2, pady=5)
        
        self.miles_entry.focus()
        self.update_status(f"Logged in as: {self.user_manager.current_user['username']}")
    
    def show_history(self):
        history = self.conversion_service.get_history(self.user_manager.current_user['id'])
        
        history_window = tk.Toplevel(self.root)
        history_window.title("Conversion History")
        history_window.geometry("500x400")
        
        # Create a frame for the Treeview and scrollbar
        tree_frame = ttk.Frame(history_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a Treeview with scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("miles", "kilometers", "date")
        self.history_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=tree_scroll.set
        )
        
        # Configure columns
        self.history_tree.heading("miles", text="Miles")
        self.history_tree.heading("kilometers", text="Kilometers")
        self.history_tree.heading("date", text="Date/Time")
        
        self.history_tree.column("miles", width=100, anchor=tk.CENTER)
        self.history_tree.column("kilometers", width=100, anchor=tk.CENTER)
        self.history_tree.column("date", width=200, anchor=tk.CENTER)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.history_tree.yview)
        
        # Add data to the treeview
        for entry in history:
            self.history_tree.insert("", tk.END, values=(
                entry['miles'],
                f"{entry['kilometers']:.2f}",
                entry['converted_at']
            ))
    
    def show_all_users(self):
        with self.db_connection as conn:
            cursor = conn.execute("SELECT id, username, created_at, last_login FROM users")
            users = cursor.fetchall()
            
            users_window = tk.Toplevel(self.root)
            users_window.title("All Users")
            users_window.geometry("500x300")
            
            tree_frame = ttk.Frame(users_window)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            tree_scroll = ttk.Scrollbar(tree_frame)
            tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            columns = ("id", "username", "created", "last_login")
            users_tree = ttk.Treeview(
                tree_frame,
                columns=columns,
                show="headings",
                yscrollcommand=tree_scroll.set
            )
            
            users_tree.heading("id", text="ID")
            users_tree.heading("username", text="Username")
            users_tree.heading("created", text="Created")
            users_tree.heading("last_login", text="Last Login")
            
            users_tree.column("id", width=50, anchor=tk.CENTER)
            users_tree.column("username", width=150, anchor=tk.W)
            users_tree.column("created", width=150, anchor=tk.CENTER)
            users_tree.column("last_login", width=150, anchor=tk.CENTER)
            
            users_tree.pack(fill=tk.BOTH, expand=True)
            tree_scroll.config(command=users_tree.yview)
            
            for user in users:
                users_tree.insert("", tk.END, values=(
                    user['id'],
                    user['username'],
                    user['created_at'],
                    user['last_login'] if user['last_login'] else "Never"
                ))
    
    def show_system_config(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("System Configuration")
        config_window.geometry("400x300")
        
        tree_frame = ttk.Frame(config_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("setting", "value")
        config_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=tree_scroll.set
        )
        
        config_tree.heading("setting", text="Setting")
        config_tree.heading("value", text="Value")
        
        config_tree.column("setting", width=150, anchor=tk.W)
        config_tree.column("value", width=200, anchor=tk.W)
        
        config_tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=config_tree.yview)
        
        for key, value in self.config.config.items():
            config_tree.insert("", tk.END, values=(key, str(value)))
    
    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        success, message = self.user_manager.login(username, password)
        
        if success:
            self.show_main_screen()
        else:
            messagebox.showerror("Login Failed", message)
    
    def handle_register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        
        success, message = self.user_manager.register(username, password)
        
        if success:
            messagebox.showinfo("Registration Successful", message)
            self.show_login_screen()
        else:
            messagebox.showerror("Registration Failed", message)
    
    def handle_conversion(self):
        try:
            miles = float(self.miles_entry.get())
            kilometers = self.conversion_service.record_conversion(
                self.user_manager.current_user['id'], miles
            )
            self.result_var.set(f"{miles} miles = {kilometers:.2f} kilometers")
            self.miles_entry.delete(0, tk.END)
            self.update_status("Conversion successful")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def handle_logout(self):
        self.user_manager.logout()
        self.root.config(menu=tk.Menu(self.root))  # Clear menu bar
        self.show_login_screen()
        self.update_status("Logged out")

# Main Entry Point
if __name__ == "__main__":
    root = tk.Tk()
    app = MileToKmConverterApp(root)
    root.mainloop()