import secrets
import string
import sqlite3
from cryptography.fernet import Fernet
from getpass import getpass
import zxcvbn
import pyperclip
import json
from datetime import datetime
import qrcode
import os
import hashlib
import argon2
import sys
import time
import threading
from typing import Dict, List, Optional, Union
import unicodedata
import re
import base64
from dataclasses import dataclass
import enum

# ==================== CONSTANTS & ENUMS ====================
class PasswordStrength(enum.IntEnum):
    WEAK = 0
    FAIR = 1
    GOOD = 2
    STRONG = 3
    VERY_STRONG = 4

class ExportFormat(enum.Enum):
    JSON = "json"
    CSV = "csv"
    ENCRYPTED_JSON = "encrypted_json"

@dataclass
class PasswordEntry:
    service: str
    username: str
    password: str
    notes: str
    created_at: str
    last_used: Optional[str]
    strength_score: PasswordStrength

# ==================== SECURITY CONFIG ====================
DEFAULT_PW_LENGTH = 16
MIN_PW_LENGTH = 8
MAX_PW_LENGTH = 128
MAX_ATTEMPTS = 5
CLIPBOARD_TIMEOUT = 30  # seconds
ARGON2_CONFIG = {
    "time_cost": 3,
    "memory_cost": 65536,
    "parallelism": 4,
    "hash_len": 32,
    "salt_len": 16
}

# ==================== PASSWORD MANAGER ====================
class PasswordManager:
    def __init__(self):
        self.db_name = "passwords.db"
        self.key_file = "secret.key"
        self.master_pw_hash = None
        self.cipher = None
        self._initialize_security()
        self._initialize_database()
        
    def _initialize_security(self):
        """Initialize encryption keys and security parameters"""
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        with open(self.key_file, 'rb') as f:
            key = f.read()
        self.cipher = Fernet(key)
        
    def _initialize_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT NOT NULL,
                    username TEXT,
                    password TEXT NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    strength_score INTEGER,
                    length INTEGER,
                    complexity TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auth (
                    hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    last_changed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_logs (
                    event TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip TEXT,
                    user_agent TEXT
                )
            ''')
            
            conn.commit()
        
        if not self._master_password_exists():
            self._setup_master_password()
        else:
            self.authenticate()
    
    def _master_password_exists(self) -> bool:
        """Check if master password is set"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM auth")
            return cursor.fetchone()[0] > 0
    
    def _setup_master_password(self):
        """Set up master password with security checks"""
        print("\n=== SETUP MASTER PASSWORD ===")
        print(f"Requirements: Minimum {MIN_PW_LENGTH} characters with mix of:")
        print("- Uppercase and lowercase letters")
        print("- Numbers")
        print("- Special characters")
        
        while True:
            master_pw = getpass("Enter master password: ")
            confirm_pw = getpass("Confirm master password: ")
            
            if master_pw != confirm_pw:
                print("Error: Passwords don't match")
                continue
                
            if len(master_pw) < MIN_PW_LENGTH:
                print(f"Error: Minimum length is {MIN_PW_LENGTH} characters")
                continue
                
            strength = self._analyze_password(master_pw)
            if strength['score'] < PasswordStrength.STRONG:
                print("Error: Password too weak")
                print("Suggestions:")
                for suggestion in strength['feedback'].get('suggestions', []):
                    print(f"- {suggestion}")
                continue
                
            break
        
        salt = secrets.token_bytes(ARGON2_CONFIG['salt_len'])
        hasher = argon2.PasswordHasher(**ARGON2_CONFIG)
        pw_hash = hasher.hash(master_pw.encode() + salt)
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO auth (hash, salt) VALUES (?, ?)", 
                (pw_hash, salt.hex())
            )
            cursor.execute(
                "INSERT INTO security_logs (event) VALUES (?)",
                ("Master password set",)
            )
            conn.commit()
        
        print("\nMaster password configured successfully!")
        self.master_pw_hash = pw_hash
    
    def authenticate(self):
        """Secure authentication with attempt limiting"""
        print("\n=== PASSWORD VAULT LOGIN ===")
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hash, salt FROM auth LIMIT 1")
            result = cursor.fetchone()
        
        if not result:
            print("No master password found. Setting up...")
            self._setup_master_password()
            return
            
        stored_hash, salt_hex = result
        salt = bytes.fromhex(salt_hex)
        
        for attempt in range(1, MAX_ATTEMPTS + 1):
            master_pw = getpass(f"Attempt {attempt}/{MAX_ATTEMPTS}: Enter master password: ")
            
            try:
                hasher = argon2.PasswordHasher()
                hasher.verify(stored_hash, master_pw.encode() + salt)
                self.master_pw_hash = stored_hash
                
                # Log successful login
                with sqlite3.connect(self.db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO security_logs (event) VALUES (?)",
                        ("Successful login",)
                    )
                    conn.commit()
                
                print("\nAuthentication successful!")
                return
            except argon2.exceptions.VerifyMismatchError:
                if attempt < MAX_ATTEMPTS:
                    print(f"Invalid password. {MAX_ATTEMPTS - attempt} attempts remaining.")
                else:
                    print("Maximum attempts reached. Exiting for security.")
                    self._log_security_event("Failed login - account locked")
                    time.sleep(2)  # Delay to prevent brute force
                    sys.exit(1)
            except Exception as e:
                print(f"Authentication error: {str(e)}")
                sys.exit(1)
    
    def _log_security_event(self, event: str):
        """Log security-related events"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO security_logs (event) VALUES (?)",
                (event,)
            )
            conn.commit()
    
    def generate_password(
        self,
        length: int = DEFAULT_PW_LENGTH,
        use_upper: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        avoid_ambiguous: bool = True,
        avoid_similar: bool = True,
        require_each_type: bool = True,
        custom_chars: str = ""
    ) -> str:
        """
        Generate a secure random password with customizable parameters
        
        Args:
            length: Desired password length (8-128)
            use_upper: Include uppercase letters
            use_digits: Include numbers
            use_symbols: Include special characters
            avoid_ambiguous: Exclude ambiguous characters (l,1,I,0,O)
            avoid_similar: Exclude similar characters (i,j,1,l, etc.)
            require_each_type: Ensure at least one of each selected character type
            custom_chars: Additional custom characters to include
            
        Returns:
            Generated password string
        """
        # Validate length
        if not MIN_PW_LENGTH <= length <= MAX_PW_LENGTH:
            raise ValueError(f"Password length must be between {MIN_PW_LENGTH} and {MAX_PW_LENGTH}")
        
        # Build character set
        chars = string.ascii_lowercase
        char_sets = []
        
        if use_upper:
            chars += string.ascii_uppercase
            char_sets.append(string.ascii_uppercase)
        if use_digits:
            chars += string.digits
            char_sets.append(string.digits)
        if use_symbols:
            chars += string.punctuation
            char_sets.append(string.punctuation)
        if custom_chars:
            chars += custom_chars
            char_sets.append(custom_chars)
        
        # Remove ambiguous characters if requested
        if avoid_ambiguous:
            ambiguous = 'l1IoO0'
            chars = ''.join(c for c in chars if c not in ambiguous)
            char_sets = [''.join(c for c in s if c not in ambiguous) for s in char_sets]
        
        # Remove similar characters if requested
        if avoid_similar:
            similar = 'ij1l|'
            chars = ''.join(c for c in chars if c not in similar)
            char_sets = [''.join(c for c in s if c not in similar) for s in char_sets]
        
        # Generate password with required character types
        while True:
            password = ''.join(secrets.choice(chars) for _ in range(length))
            
            # Check if we need to enforce character types
            if not require_each_type:
                break
                
            # Verify all required character types are present
            checks_passed = True
            for char_set in char_sets:
                if not any(c in char_set for c in password):
                    checks_passed = False
                    break
            
            if checks_passed:
                break
        
        return password
    
    def _analyze_password(self, password: str) -> Dict:
        """Comprehensive password strength analysis"""
        result = zxcvbn.zxcvbn(password)
        
        # Additional custom checks
        length = len(password)
        unique_chars = len(set(password))
        entropy = self._calculate_entropy(password)
        
        return {
            'score': PasswordStrength(min(result['score'], 4)),  # Cap at 4
            'length': length,
            'unique_chars': unique_chars,
            'entropy': entropy,
            'crack_time': result['crack_times_display']['offline_slow_hashing_1e4_per_second'],
            'feedback': result['feedback'],
            'warning': result['feedback'].get('warning', ''),
            'suggestions': result['feedback'].get('suggestions', [])
        }
    
    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits"""
        char_set = 0
        
        if any(c.islower() for c in password):
            char_set += 26
        if any(c.isupper() for c in password):
            char_set += 26
        if any(c.isdigit() for c in password):
            char_set += 10
        if any(c in string.punctuation for c in password):
            char_set += 32
        
        if char_set == 0:
            return 0.0
            
        length = len(password)
        return length * (char_set ** 0.5)  # Simplified entropy calculation
    
    def store_password(
        self,
        service: str,
        password: str,
        username: str = "",
        notes: str = "",
        auto_generated: bool = False
    ):
        """Securely store a password with metadata"""
        if not service:
            raise ValueError("Service name is required")
            
        if not password:
            raise ValueError("Password cannot be empty")
            
        encrypted_pw = self.cipher.encrypt(password.encode())
        analysis = self._analyze_password(password)
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO passwords (
                    service, username, password, notes, strength_score, length, complexity
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                service,
                username,
                encrypted_pw,
                notes,
                int(analysis['score']),
                len(password),
                self._get_complexity_description(password)
            ))
            
            conn.commit()
        
        self._log_security_event(f"Password stored for {service}")
    
    def _get_complexity_description(self, password: str) -> str:
        """Generate human-readable complexity description"""
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in string.punctuation for c in password)
        
        parts = []
        if has_upper and has_lower:
            parts.append("mixed case")
        elif has_upper:
            parts.append("uppercase")
        elif has_lower:
            parts.append("lowercase")
            
        if has_digit:
            parts.append("digits")
        if has_symbol:
            parts.append("symbols")
            
        return ", ".join(parts) if parts else "simple"
    
    def get_password(self, service: str) -> Optional[PasswordEntry]:
        """Retrieve a password entry"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT service, username, password, notes, created_at, last_used, strength_score
                FROM passwords 
                WHERE service = ?
                ORDER BY last_used DESC, created_at DESC
                LIMIT 1
            ''', (service,))
            
            result = cursor.fetchone()
            
            if not result:
                return None
                
            service, username, encrypted_pw, notes, created_at, last_used, strength_score = result
            password = self.cipher.decrypt(encrypted_pw).decode()
            
            # Update last used timestamp
            cursor.execute('''
                UPDATE passwords 
                SET last_used = CURRENT_TIMESTAMP
                WHERE service = ? AND username = ?
            ''', (service, username))
            conn.commit()
            
            return PasswordEntry(
                service=service,
                username=username,
                password=password,
                notes=notes,
                created_at=created_at,
                last_used=last_used,
                strength_score=PasswordStrength(strength_score)
            )
    
    def export_passwords(
        self,
        format: ExportFormat = ExportFormat.JSON,
        file_path: Optional[str] = None,
        encrypt: bool = False
    ) -> str:
        """Export passwords to a file with optional encryption"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT service, username, password, notes, created_at, last_used, strength_score
                FROM passwords
                ORDER BY service, username
            ''')
            
            passwords = []
            for row in cursor.fetchall():
                service, username, encrypted_pw, notes, created_at, last_used, strength_score = row
                password = self.cipher.decrypt(encrypted_pw).decode()
                
                passwords.append({
                    'service': service,
                    'username': username,
                    'password': password,
                    'notes': notes,
                    'created_at': created_at,
                    'last_used': last_used,
                    'strength_score': strength_score
                })
        
        # Generate default filename if not provided
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"passwords_export_{timestamp}.{format.value}"
        
        # Handle different export formats
        if format == ExportFormat.JSON:
            data = json.dumps(passwords, indent=2)
            if encrypt:
                data = self.cipher.encrypt(data.encode()).decode()
            with open(file_path, 'w') as f:
                f.write(data)
                
        elif format == ExportFormat.CSV:
            import csv
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'service', 'username', 'password', 'notes',
                    'created_at', 'last_used', 'strength_score'
                ])
                writer.writeheader()
                writer.writerows(passwords)
                
        elif format == ExportFormat.ENCRYPTED_JSON:
            data = json.dumps(passwords, indent=2)
            encrypted_data = self.cipher.encrypt(data.encode())
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
        
        self._log_security_event(f"Passwords exported to {file_path}")
        return file_path
    
    def generate_qr_code(
        self,
        data: str,
        file_path: Optional[str] = None,
        size: int = 10,
        border: int = 4,
        error_correction: str = 'L'
    ) -> str:
        """Generate QR code for secure sharing"""
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"qr_code_{timestamp}.png"
        
        # Map error correction levels
        ecc_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=ecc_map.get(error_correction, qrcode.constants.ERROR_CORRECT_L),
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)
        return file_path
    
    def clear_clipboard(self):
        """Clear clipboard after timeout"""
        time.sleep(CLIPBOARD_TIMEOUT)
        pyperclip.copy('')
        print("\nClipboard has been cleared for security.")
    
    def interactive_menu(self):
        """Main interactive menu with enhanced UI"""
        while True:
            print("\n" + "="*40)
            print("=== ADVANCED PASSWORD MANAGER ===".center(40))
            print("="*40)
            print("1. Generate New Password")
            print("2. Store Existing Password")
            print("3. Retrieve Password")
            print("4. Password Database Tools")
            print("5. Security Settings")
            print("6. Exit")
            
            try:
                choice = input("\nEnter your choice (1-6): ").strip()
                
                if choice == '1':
                    self._generate_password_flow()
                elif choice == '2':
                    self._store_password_flow()
                elif choice == '3':
                    self._retrieve_password_flow()
                elif choice == '4':
                    self._database_tools_menu()
                elif choice == '5':
                    self._security_settings_menu()
                elif choice == '6':
                    print("\nExiting. Your passwords are secure!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            except Exception as e:
                print(f"\nError: {str(e)}")
                self._log_security_event(f"Error in menu: {str(e)}")
    
    def _generate_password_flow(self):
        """Interactive password generation workflow"""
        print("\n=== PASSWORD GENERATOR ===")
        
        # Get parameters
        while True:
            try:
                length = int(input(f"Length ({MIN_PW_LENGTH}-{MAX_PW_LENGTH}, default {DEFAULT_PW_LENGTH}): ") or DEFAULT_PW_LENGTH)
                if not MIN_PW_LENGTH <= length <= MAX_PW_LENGTH:
                    print(f"Please enter a value between {MIN_PW_LENGTH} and {MAX_PW_LENGTH}")
                    continue
                break
            except ValueError:
                print("Please enter a valid number")
        
        use_upper = input("Include uppercase letters? (Y/n): ").lower() != 'n'
        use_digits = input("Include digits? (Y/n): ").lower() != 'n'
        use_symbols = input("Include symbols? (Y/n): ").lower() != 'n'
        avoid_ambiguous = input("Avoid ambiguous characters? (Y/n): ").lower() != 'n'
        avoid_similar = input("Avoid similar characters? (Y/n): ").lower() != 'n'
        require_each = input("Require at least one of each type? (Y/n): ").lower() != 'n'
        
        # Generate and analyze password
        password = self.generate_password(
            length=length,
            use_upper=use_upper,
            use_digits=use_digits,
            use_symbols=use_symbols,
            avoid_ambiguous=avoid_ambiguous,
            avoid_similar=avoid_similar,
            require_each_type=require_each
        )
        
        analysis = self._analyze_password(password)
        
        # Display results
        print("\n" + "="*40)
        print("Generated Password:", password)
        print("\nPassword Analysis:")
        print(f"- Strength: {analysis['score']}/4 ({PasswordStrength(analysis['score']).name.replace('_', ' ')})")
        print(f"- Length: {analysis['length']} characters")
        print(f"- Unique characters: {analysis['unique_chars']}")
        print(f"- Estimated entropy: {analysis['entropy']:.1f} bits")
        print(f"- Estimated crack time: {analysis['crack_time']}")
        
        if analysis['warning']:
            print("\nWarning:", analysis['warning'])
        
        if analysis['suggestions']:
            print("\nSuggestions:")
            for suggestion in analysis['suggestions']:
                print(f"- {suggestion}")
        
        # Copy to clipboard
        pyperclip.copy(password)
        print("\nPassword copied to clipboard (will clear after 30 seconds).")
        threading.Thread(target=self.clear_clipboard, daemon=True).start()
        
        # Offer to store
        store = input("\nStore this password? (Y/n): ").lower() != 'n'
        if store:
            service = input("Service/Website: ").strip()
            if not service:
                print("Service name is required")
                return
                
            username = input("Username (optional): ").strip()
            notes = input("Notes (optional): ").strip()
            
            try:
                self.store_password(service, password, username, notes, auto_generated=True)
                print("Password stored securely!")
            except Exception as e:
                print(f"Error storing password: {str(e)}")
    
    def _store_password_flow(self):
        """Store an existing password"""
        print("\n=== STORE PASSWORD ===")
        
        service = input("Service/Website: ").strip()
        if not service:
            print("Service name is required")
            return
            
        username = input("Username (optional): ").strip()
        password = getpass("Password: ").strip()
        if not password:
            print("Password cannot be empty")
            return
            
        notes = input("Notes (optional): ").strip()
        
        try:
            self.store_password(service, password, username, notes)
            print("\nPassword stored successfully!")
        except Exception as e:
            print(f"\nError storing password: {str(e)}")
    
    def _retrieve_password_flow(self):
        """Retrieve a stored password"""
        print("\n=== RETRIEVE PASSWORD ===")
        
        service = input("Enter service name: ").strip()
        if not service:
            print("Service name is required")
            return
            
        entry = self.get_password(service)
        if not entry:
            print(f"No password found for service: {service}")
            return
            
        print("\n" + "="*40)
        print("Password Details:")
        print(f"Service: {entry.service}")
        if entry.username:
            print(f"Username: {entry.username}")
        print(f"Password: {entry.password}")
        if entry.notes:
            print(f"Notes: {entry.notes}")
        print(f"Created: {entry.created_at}")
        if entry.last_used:
            print(f"Last used: {entry.last_used}")
        print(f"Strength: {entry.strength_score.name.replace('_', ' ')}")
        
        # Copy to clipboard
        pyperclip.copy(entry.password)
        print("\nPassword copied to clipboard (will clear after 30 seconds).")
        threading.Thread(target=self.clear_clipboard, daemon=True).start()
        
        # QR code option
        if input("\nGenerate QR code for this password? (y/N): ").lower() == 'y':
            data = f"Service: {entry.service}\n"
            if entry.username:
                data += f"Username: {entry.username}\n"
            data += f"Password: {entry.password}"
            
            file_path = self.generate_qr_code(data)
            print(f"QR code saved to: {file_path}")
    
    def _database_tools_menu(self):
        """Database management tools"""
        while True:
            print("\n=== DATABASE TOOLS ===")
            print("1. Export Passwords")
            print("2. Show Password Stats")
            print("3. Back to Main Menu")
            
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == '1':
                self._export_passwords_flow()
            elif choice == '2':
                self._show_password_stats()
            elif choice == '3':
                break
            else:
                print("Invalid choice")
    
    def _export_passwords_flow(self):
        """Export passwords workflow"""
        print("\n=== EXPORT PASSWORDS ===")
        print("1. JSON (readable)")
        print("2. CSV (spreadsheet)")
        print("3. Encrypted JSON (secure)")
        print("4. Back")
        
        choice = input("\nEnter format (1-4): ").strip()
        
        if choice == '4':
            return
            
        formats = {
            '1': ExportFormat.JSON,
            '2': ExportFormat.CSV,
            '3': ExportFormat.ENCRYPTED_JSON
        }
        
        if choice not in formats:
            print("Invalid choice")
            return
            
        file_path = input("File path (leave blank for default): ").strip()
        
        try:
            exported_file = self.export_passwords(
                format=formats[choice],
                file_path=file_path if file_path else None
            )
            print(f"\nPasswords exported successfully to: {exported_file}")
        except Exception as e:
            print(f"\nExport failed: {str(e)}")
    
    def _show_password_stats(self):
        """Display password database statistics"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Basic counts
            cursor.execute("SELECT COUNT(*) FROM passwords")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT service) FROM passwords")
            unique_services = cursor.fetchone()[0]
            
            # Strength distribution
            cursor.execute('''
                SELECT strength_score, COUNT(*) 
                FROM passwords 
                GROUP BY strength_score 
                ORDER BY strength_score DESC
            ''')
            strength_dist = cursor.fetchall()
            
            # Length stats
            cursor.execute("SELECT AVG(length), MIN(length), MAX(length) FROM passwords")
            avg_len, min_len, max_len = cursor.fetchone()
            
        print("\n=== PASSWORD DATABASE STATISTICS ===")
        print(f"Total passwords stored: {total}")
        print(f"Unique services: {unique_services}")
        print(f"Average password length: {avg_len:.1f} characters")
        print(f"Length range: {min_len} to {max_len} characters")
        
        print("\nPassword Strength Distribution:")
        for score, count in strength_dist:
            print(f"- {PasswordStrength(score).name.replace('_', ' ')}: {count} ({count/total:.1%})")
    
    def _security_settings_menu(self):
        """Security-related settings"""
        while True:
            print("\n=== SECURITY SETTINGS ===")
            print("1. Change Master Password")
            print("2. View Security Logs")
            print("3. Back to Main Menu")
            
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == '1':
                self._change_master_password()
            elif choice == '2':
                self._view_security_logs()
            elif choice == '3':
                break
            else:
                print("Invalid choice")
    
    def _change_master_password(self):
        """Change the master password"""
        print("\n=== CHANGE MASTER PASSWORD ===")
        
        # Verify current password
        current = getpass("Current master password: ")
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hash, salt FROM auth LIMIT 1")
            stored_hash, salt_hex = cursor.fetchone()
        
        salt = bytes.fromhex(salt_hex)
        hasher = argon2.PasswordHasher()
        
        try:
            hasher.verify(stored_hash, current.encode() + salt)
        except:
            print("\nIncorrect current password")
            return
            
        # Get new password
        print("\nEnter new master password")
        while True:
            new_pw = getpass("New master password: ")
            confirm = getpass("Confirm new master password: ")
            
            if new_pw != confirm:
                print("Passwords don't match. Try again.")
                continue
                
            if len(new_pw) < MIN_PW_LENGTH:
                print(f"Password must be at least {MIN_PW_LENGTH} characters")
                continue
                
            strength = self._analyze_password(new_pw)
            if strength['score'] < PasswordStrength.STRONG:
                print("Password too weak. Suggestions:")
                for suggestion in strength['suggestions']:
                    print(f"- {suggestion}")
                continue
                
            break
        
        # Generate new salt and hash
        new_salt = secrets.token_bytes(ARGON2_CONFIG['salt_len'])
        new_hash = hasher.hash(new_pw.encode() + new_salt)
        
        # Update in database
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE auth 
                SET hash = ?, salt = ?, last_changed = CURRENT_TIMESTAMP
            ''', (new_hash, new_salt.hex()))
            cursor.execute(
                "INSERT INTO security_logs (event) VALUES (?)",
                ("Master password changed",)
            )
            conn.commit()
        
        self.master_pw_hash = new_hash
        print("\nMaster password changed successfully!")
    
    def _view_security_logs(self):
        """Display security event logs"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT event, timestamp 
                FROM security_logs 
                ORDER BY timestamp DESC 
                LIMIT 50
            ''')
            logs = cursor.fetchall()
        
        print("\n=== SECURITY EVENT LOG (Last 50 entries) ===")
        for event, timestamp in logs:
            print(f"{timestamp}: {event}")

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":

    print("""
        ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗██╗   ██╗███╗   ███╗
        ██╔══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██║   ██║████╗ ████║
        ██████╔╝██║   ██║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
        ██╔═══╝ ██║   ██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
        ██║     ╚██████╔╝██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
        ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
        """)
    print("Quantum-Resistant Password Vault v2.0")
    print("-------------------------------------")

    
    try:
        manager = PasswordManager()
        manager.interactive_menu()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)