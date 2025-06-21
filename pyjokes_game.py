import pyjokes
import json
import getpass
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
import random
from colorama import Fore, Style, init
from abc import ABC, abstractmethod
import textwrap
import time
import pickle
import requests
import openai
from typing import Optional, Dict, List, Tuple, Deque
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
from logging.handlers import RotatingFileHandler
import threading
import queue

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('joke_teller.log', maxBytes=1_000_000, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = timedelta(minutes=15)
TOKEN_EXPIRY = timedelta(hours=1)
MAX_JOKE_LENGTH = 120
MAX_JOKES_PER_MINUTE = 10

class JokeCategory(Enum):
    NEUTRAL = auto()
    CHUCK = auto()
    PROGRAMMING = auto()
    DAD = auto()
    CUSTOM = auto()

class UserRole(Enum):
    USER = auto()
    PREMIUM = auto()
    ADMIN = auto()
    MODERATOR = auto()

class JokeSentiment(Enum):
    POSITIVE = auto()
    NEUTRAL = auto()
    NEGATIVE = auto()

@dataclass
class Joke:
    content: str
    category: JokeCategory
    language: str
    sentiment: Optional[JokeSentiment] = None
    rating: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class UserSession:
    username: str
    role: UserRole
    login_time: datetime
    last_activity: datetime
    token: str
    expiry: datetime
    ip_address: str

class RateLimiter:
    """Token bucket rate limiter implementation"""
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        refill_amount = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + refill_amount)
        self.last_refill = now

class JokeAPI:
    """Wrapper for multiple joke APIs with fallback"""
    def __init__(self):
        self.rate_limiter = RateLimiter(capacity=10, refill_rate=1/60)  # 10 requests per minute
        self.cache = {}
        self.cache_size = 100
        self.cache_lock = threading.Lock()

    def get_joke(self, category: JokeCategory = JokeCategory.NEUTRAL, 
                language: str = 'en') -> Optional[Joke]:
        """Get a joke from available APIs with caching"""
        cache_key = (category, language)
        
        # Check cache first
        with self.cache_lock:
            if cache_key in self.cache:
                logger.debug("Returning cached joke")
                return self.cache[cache_key]

        if not self.rate_limiter.consume():
            logger.warning("Rate limit exceeded")
            return None

        try:
            # Try OpenAI first for premium jokes
            if category == JokeCategory.CUSTOM:
                joke = self._get_ai_joke()
            else:
                # Fallback to pyjokes
                joke_content = pyjokes.get_joke(language=language, 
                                              category=category.name.lower())
                joke = Joke(content=joke_content, category=category, language=language)
            
            # Analyze sentiment
            joke.sentiment = self._analyze_sentiment(joke.content)
            
            # Update cache
            with self.cache_lock:
                if len(self.cache) >= self.cache_size:
                    self.cache.popitem()
                self.cache[cache_key] = joke
            
            return joke
        except Exception as e:
            logger.error(f"Error getting joke: {e}")
            return None

    def _get_ai_joke(self) -> Optional[Joke]:
        """Generate joke using OpenAI API"""
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt="Tell me a funny joke that would appeal to software engineers:",
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.7,
            )
            joke_content = response.choices[0].text.strip()
            return Joke(content=joke_content, category=JokeCategory.CUSTOM, language='en')
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None

    def _analyze_sentiment(self, text: str) -> JokeSentiment:
        """Simple sentiment analysis (would use proper NLP in production)"""
        text = text.lower()
        positive_words = {'fun', 'laugh', 'happy', 'joy', 'hilarious'}
        negative_words = {'die', 'kill', 'hate', 'stupid', 'dumb'}
        
        if any(word in text for word in positive_words):
            return JokeSentiment.POSITIVE
        elif any(word in text for word in negative_words):
            return JokeSentiment.NEGATIVE
        return JokeSentiment.NEUTRAL

class DatabaseManager:
    """Advanced database manager with connection pooling and caching"""
    def __init__(self):
        self.users_file = "users.json"
        self.joke_history_file = "joke_history.pkl"  # Using pickle for performance
        self.stats_file = "joke_stats.pkl"
        self.sessions_file = "sessions.pkl"
        self.failed_logins_file = "failed_logins.pkl"
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.write_queue = queue.Queue()
        self.writer_thread = threading.Thread(target=self._async_writer, daemon=True)
        self.writer_thread.start()
        self.initialize_files()

    def initialize_files(self):
        """Initialize all required files with proper data structures"""
        files = {
            self.users_file: {
                "admin": {
                    "password": self._hash_password("admin123"),
                    "role": UserRole.ADMIN.name,
                    "created_at": str(datetime.now()),
                    "last_login": None,
                    "failed_attempts": 0
                }
            },
            self.joke_history_file: defaultdict(deque),
            self.stats_file: {
                "total_jokes_told": 0,
                "popular_jokes": defaultdict(int),
                "jokes_by_category": defaultdict(int),
                "jokes_by_language": defaultdict(int),
                "user_activity": defaultdict(int)
            },
            self.sessions_file: {},
            self.failed_logins_file: defaultdict(dict)
        }

        for file, default_data in files.items():
            if not Path(file).exists():
                self._write_file(file, default_data)

    def _async_writer(self):
        """Background thread for async writes"""
        while True:
            filename, data = self.write_queue.get()
            try:
                with open(filename, 'wb') as f:
                    pickle.dump(data, f)
            except Exception as e:
                logger.error(f"Error writing to {filename}: {e}")
            finally:
                self.write_queue.task_done()

    def _write_file(self, filename: str, data):
        """Write data to file (synchronously)"""
        try:
            if filename.endswith('.json'):
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
            else:
                with open(filename, 'wb') as f:
                    pickle.dump(data, f)
        except Exception as e:
            logger.error(f"Error writing to {filename}: {e}")

    def _hash_password(self, password: str) -> str:
        """Secure password hashing with salt and pepper"""
        salt = os.urandom(32)
        pepper = b"static-pepper-value"  # In production, use env variable
        key = hashlib.pbkdf2_hmac(
            'sha512',
            (password + pepper.decode()).encode('utf-8'),
            salt,
            100000
        )
        return salt.hex() + key.hex()

    def _verify_password(self, stored_password: str, provided_password: str) -> bool:
        """Verify hashed password"""
        if not stored_password or len(stored_password) < 64:
            return False
            
        salt = bytes.fromhex(stored_password[:64])
        stored_key = stored_password[64:]
        pepper = b"static-pepper-value"
        
        new_key = hashlib.pbkdf2_hmac(
            'sha512',
            (provided_password + pepper.decode()).encode('utf-8'),
            salt,
            100000
        ).hex()
        
        return new_key == stored_key

    def get_user(self, username: str) -> Optional[dict]:
        """Get user data with caching"""
        with self.cache_lock:
            if username in self.cache.get('users', {}):
                return self.cache['users'][username]

        users = self.read_file(self.users_file)
        user = users.get(username)
        
        with self.cache_lock:
            if 'users' not in self.cache:
                self.cache['users'] = {}
            self.cache['users'][username] = user
            
        return user

    def update_user(self, username: str, data: dict):
        """Update user data"""
        users = self.read_file(self.users_file)
        users[username] = data
        self.write_file(self.users_file, users)
        
        with self.cache_lock:
            if 'users' in self.cache and username in self.cache['users']:
                self.cache['users'][username] = data

    def read_file(self, filename: str):
        """Read data from file with error handling"""
        try:
            if filename.endswith('.json'):
                with open(filename, 'r') as f:
                    return json.load(f)
            else:
                with open(filename, 'rb') as f:
                    return pickle.load(f)
        except (FileNotFoundError, json.JSONDecodeError, pickle.PickleError) as e:
            logger.error(f"Error reading {filename}: {e}")
            return {}

    def write_file(self, filename: str, data):
        """Queue write operation for async processing"""
        self.write_queue.put((filename, data))

    def log_failed_login(self, username: str, ip_address: str):
        """Track failed login attempts"""
        failed_logins = self.read_file(self.failed_logins_file)
        now = datetime.now()
        
        if username not in failed_logins:
            failed_logins[username] = {
                'count': 1,
                'last_attempt': now,
                'ip_address': ip_address
            }
        else:
            failed_logins[username]['count'] += 1
            failed_logins[username]['last_attempt'] = now
            
        self.write_file(self.failed_logins_file, failed_logins)

    def is_account_locked(self, username: str) -> bool:
        """Check if account is temporarily locked"""
        failed_logins = self.read_file(self.failed_logins_file)
        user_data = failed_logins.get(username, {})
        
        if user_data.get('count', 0) >= MAX_LOGIN_ATTEMPTS:
            last_attempt = datetime.fromisoformat(user_data['last_attempt'])
            return datetime.now() - last_attempt < LOCKOUT_TIME
        return False

    def reset_failed_logins(self, username: str):
        """Reset failed login counter"""
        failed_logins = self.read_file(self.failed_logins_file)
        if username in failed_logins:
            del failed_logins[username]
            self.write_file(self.failed_logins_file, failed_logins)

    def create_session(self, session: UserSession):
        """Store user session"""
        sessions = self.read_file(self.sessions_file)
        sessions[session.token] = {
            'username': session.username,
            'role': session.role.name,
            'login_time': session.login_time.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'expiry': session.expiry.isoformat(),
            'ip_address': session.ip_address
        }
        self.write_file(self.sessions_file, sessions)

    def validate_session(self, token: str, ip_address: str) -> Optional[UserSession]:
        """Validate and update session"""
        sessions = self.read_file(self.sessions_file)
        session_data = sessions.get(token)
        
        if not session_data:
            return None
            
        now = datetime.now()
        expiry = datetime.fromisoformat(session_data['expiry'])
        
        if now > expiry:
            del sessions[token]
            self.write_file(self.sessions_file, sessions)
            return None
            
        # Verify IP address matches
        if session_data['ip_address'] != ip_address:
            return None
            
        # Update last activity
        session_data['last_activity'] = now.isoformat()
        sessions[token] = session_data
        self.write_file(self.sessions_file, sessions)
        
        return UserSession(
            username=session_data['username'],
            role=UserRole[session_data['role']],
            login_time=datetime.fromisoformat(session_data['login_time']),
            last_activity=datetime.fromisoformat(session_data['last_activity']),
            token=token,
            expiry=expiry,
            ip_address=session_data['ip_address']
        )

class UserManager:
    """Advanced user management with session handling"""
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.active_sessions = {}
        self.session_lock = threading.Lock()

    def register_user(self, ip_address: str) -> Optional[dict]:
        """Register a new user with enhanced validation"""
        username = input(Fore.CYAN + "Enter new username (3-20 chars): " + Style.RESET_ALL).strip()
        
        # Validate username
        if not 3 <= len(username) <= 20:
            print(Fore.RED + "Username must be 3-20 characters!")
            return None
            
        if not username.isalnum():
            print(Fore.RED + "Username must be alphanumeric!")
            return None
            
        if self.db.get_user(username):
            print(Fore.RED + "Username already exists!")
            return None

        # Password validation
        while True:
            password = getpass.getpass(Fore.CYAN + "Enter password (min 8 chars): " + Style.RESET_ALL)
            if len(password) < 8:
                print(Fore.RED + "Password must be at least 8 characters!")
                continue
                
            confirm = getpass.getpass(Fore.CYAN + "Confirm password: " + Style.RESET_ALL)
            if password != confirm:
                print(Fore.RED + "Passwords don't match!")
                continue
            break

        # Create user
        user_data = {
            "password": self.db._hash_password(password),
            "role": UserRole.USER.name,
            "created_at": str(datetime.now()),
            "last_login": None,
            "failed_attempts": 0,
            "preferences": {
                "language": "en",
                "favorite_categories": []
            }
        }
        
        self.db.update_user(username, user_data)
        print(Fore.GREEN + "Registration successful!")
        return {"username": username, "role": UserRole.USER}

    def authenticate(self, ip_address: str) -> Optional[UserSession]:
        """Authenticate user with session creation"""
        username = input(Fore.CYAN + "Username: " + Style.RESET_ALL).strip()
        
        # Check if account is locked
        if self.db.is_account_locked(username):
            print(Fore.RED + "Account temporarily locked due to too many failed attempts!")
            return None

        password = getpass.getpass(Fore.CYAN + "Password: " + Style.RESET_ALL)
        user = self.db.get_user(username)
        
        if not user or not self.db._verify_password(user.get('password'), password):
            self.db.log_failed_login(username, ip_address)
            print(Fore.RED + "Invalid credentials!")
            return None
            
        # Reset failed attempts on successful login
        self.db.reset_failed_logins(username)
        
        # Update user last login
        user['last_login'] = str(datetime.now())
        user['failed_attempts'] = 0
        self.db.update_user(username, user)
        
        # Create session
        token = hashlib.sha256(os.urandom(60)).hexdigest()
        expiry = datetime.now() + TOKEN_EXPIRY
        session = UserSession(
            username=username,
            role=UserRole[user['role']],
            login_time=datetime.now(),
            last_activity=datetime.now(),
            token=token,
            expiry=expiry,
            ip_address=ip_address
        )
        
        self.db.create_session(session)
        
        with self.session_lock:
            self.active_sessions[token] = session
            
        print(Fore.GREEN + f"\nWelcome back, {username}!")
        return session

    def change_password(self, username: str) -> bool:
        """Change password with enhanced security checks"""
        user = self.db.get_user(username)
        if not user:
            print(Fore.RED + "User not found!")
            return False

        current = getpass.getpass(Fore.CYAN + "Current password: " + Style.RESET_ALL)
        if not self.db._verify_password(user['password'], current):
            print(Fore.RED + "Incorrect current password!")
            return False

        while True:
            new_pass = getpass.getpass(Fore.CYAN + "New password: " + Style.RESET_ALL)
            if len(new_pass) < 8:
                print(Fore.RED + "Password must be at least 8 characters!")
                continue
                
            if new_pass == current:
                print(Fore.RED + "New password must be different from current password!")
                continue
                
            confirm = getpass.getpass(Fore.CYAN + "Confirm new password: " + Style.RESET_ALL)
            if new_pass != confirm:
                print(Fore.RED + "Passwords don't match!")
                continue
            break

        user['password'] = self.db._hash_password(new_pass)
        user['last_password_change'] = str(datetime.now())
        self.db.update_user(username, user)
        
        # Invalidate all sessions
        with self.session_lock:
            for token, session in list(self.active_sessions.items()):
                if session.username == username:
                    del self.active_sessions[token]
        
        print(Fore.GREEN + "Password changed successfully! Please login again.")
        return True

    def reset_password(self, admin_username: str) -> bool:
        """Admin password reset with audit trail"""
        admin = self.db.get_user(admin_username)
        if not admin or UserRole[admin['role']] != UserRole.ADMIN:
            print(Fore.RED + "Admin privileges required!")
            return False

        target = input(Fore.CYAN + "Enter username to reset: " + Style.RESET_ALL).strip()
        target_user = self.db.get_user(target)
        if not target_user:
            print(Fore.RED + "User not found!")
            return False

        while True:
            new_pass = getpass.getpass(Fore.CYAN + f"New password for {target}: " + Style.RESET_ALL)
            if len(new_pass) < 8:
                print(Fore.RED + "Password must be at least 8 characters!")
                continue
                
            confirm = getpass.getpass(Fore.CYAN + "Confirm new password: " + Style.RESET_ALL)
            if new_pass != confirm:
                print(Fore.RED + "Passwords don't match!")
                continue
            break

        target_user['password'] = self.db._hash_password(new_pass)
        target_user['last_password_change'] = str(datetime.now())
        target_user['reset_by_admin'] = admin_username
        self.db.update_user(target, target_user)
        
        # Invalidate target's sessions
        with self.session_lock:
            for token, session in list(self.active_sessions.items()):
                if session.username == target:
                    del self.active_sessions[token]
        
        print(Fore.GREEN + f"Password for {target} reset successfully!")
        return True

class JokeHistoryManager:
    """Advanced joke history and statistics tracking"""
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.user_rate_limits = defaultdict(RateLimiter)
        self.rate_limit_lock = threading.Lock()

    def log_joke(self, username: str, joke: Joke, rating: Optional[int] = None):
        """Log a joke with rate limiting"""
        # Check rate limit
        with self.rate_limit_lock:
            if not self.user_rate_limits[username].consume():
                print(Fore.YELLOW + "Rate limit exceeded - please wait before requesting more jokes")
                return False

        joke.rating = rating
        joke.timestamp = datetime.now()
        
        # Update history
        history = self.db.read_file(self.db.joke_history_file)
        user_history = history[username]
        
        # Keep only last 100 jokes per user
        if len(user_history) >= 100:
            user_history.popleft()
        user_history.append(joke)
        
        self.db.write_file(self.db.joke_history_file, history)
        
        # Update statistics
        stats = self.db.read_file(self.db.stats_file)
        stats["total_jokes_told"] += 1
        stats["popular_jokes"][joke.content] += 1
        stats["jokes_by_category"][joke.category.name] += 1
        stats["jokes_by_language"][joke.language] += 1
        stats["user_activity"][username] += 1
        
        self.db.write_file(self.db.stats_file, stats)
        return True

    def get_user_history(self, username: str, limit: int = 5) -> List[Joke]:
        """Get user's joke history"""
        history = self.db.read_file(self.db.joke_history_file)
        user_history = history.get(username, deque())
        return list(user_history)[-limit:] if limit else list(user_history)

    def get_user_stats(self, username: str) -> dict:
        """Get comprehensive stats for a user"""
        history = self.db.read_file(self.db.joke_history_file)
        stats = self.db.read_file(self.db.stats_file)
        
        user_history = history.get(username, [])
        if not user_history:
            return {}
            
        # Calculate various stats
        lang_counts = defaultdict(int)
        cat_counts = defaultdict(int)
        sentiment_counts = defaultdict(int)
        rating_total = 0
        rating_count = 0
        
        for joke in user_history:
            lang_counts[joke.language] += 1
            cat_counts[joke.category.name] += 1
            if joke.sentiment:
                sentiment_counts[joke.sentiment.name] += 1
            if joke.rating:
                rating_total += joke.rating
                rating_count += 1
                
        avg_rating = rating_total / rating_count if rating_count else 0
        
        return {
            "total_jokes": len(user_history),
            "favorite_language": max(lang_counts.items(), key=lambda x: x[1])[0],
            "favorite_category": max(cat_counts.items(), key=lambda x: x[1])[0],
            "sentiment_distribution": dict(sentiment_counts),
            "average_rating": round(avg_rating, 2),
            "global_rank": self._get_user_rank(username, stats)
        }

    def _get_user_rank(self, username: str, stats: dict) -> int:
        """Calculate user's global rank based on activity"""
        user_activity = stats.get("user_activity", {})
        if not user_activity or username not in user_activity:
            return 0
            
        sorted_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)
        for rank, (user, _) in enumerate(sorted_users, 1):
            if user == username:
                return rank
        return 0

    def get_global_stats(self) -> dict:
        """Get comprehensive global statistics"""
        stats = self.db.read_file(self.db.stats_file)
        
        # Calculate top jokes
        top_jokes = sorted(
            stats.get("popular_jokes", {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Calculate top categories
        top_categories = sorted(
            stats.get("jokes_by_category", {}).items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Calculate top languages
        top_languages = sorted(
            stats.get("jokes_by_language", {}).items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Calculate top users
        top_users = sorted(
            stats.get("user_activity", {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total_jokes_told": stats.get("total_jokes_told", 0),
            "top_jokes": top_jokes,
            "top_categories": top_categories,
            "top_languages": top_languages,
            "top_users": top_users,
            "daily_average": self._calculate_daily_average()
        }

    def _calculate_daily_average(self) -> float:
        """Calculate average jokes per day"""
        stats = self.db.read_file(self.db.stats_file)
        total_jokes = stats.get("total_jokes_told", 0)
        
        # Get first joke timestamp from history
        history = self.db.read_file(self.db.joke_history_file)
        if not history:
            return 0.0
            
        first_date = None
        for user_history in history.values():
            if user_history:
                first_joke = user_history[0]
                joke_date = first_joke.timestamp.date() if isinstance(first_joke.timestamp, datetime) else datetime.fromisoformat(first_joke.timestamp).date()
                if first_date is None or joke_date < first_date:
                    first_date = joke_date
        
        if not first_date:
            return 0.0
            
        days = (datetime.now().date() - first_date).days
        return round(total_jokes / max(1, days), 2)

# [Rest of the code remains the same as previous implementation...]
# [Include all the UI classes (MainMenu, JokeMenu, AdminPanel) and JokeGame class]
# [Make sure to update them to use the new advanced features]
class MainMenu:
    """Main menu interface with enhanced options"""
    def __init__(self, user_manager: UserManager, joke_api: JokeAPI):
        self.user_manager = user_manager
        self.joke_api = joke_api
        self.current_session = None

    def display(self):
        """Display main menu with dynamic options based on user role"""
        while True:
            print(Fore.YELLOW + "\n" + "="*50)
            print(Fore.CYAN + " JOKE TELLER APPLICATION ".center(50, "~"))
            print(Fore.YELLOW + "="*50 + Style.RESET_ALL)
            
            if self.current_session:
                role_display = self.current_session.role.name.capitalize()
                print(Fore.GREEN + f"\nLogged in as: {self.current_session.username} ({role_display})")
                print(f"Session expires: {self.current_session.expiry.strftime('%Y-%m-%d %H:%M:%S')}")
                
                options = [
                    ("1", "Tell me a joke"),
                    ("2", "Joke history & stats"),
                    ("3", "Change password"),
                    ("4", "Logout")
                ]
                
                # Add admin options if applicable
                if self.current_session.role in [UserRole.ADMIN, UserRole.MODERATOR]:
                    options.insert(3, ("A", "Admin panel"))
                    
            else:
                options = [
                    ("1", "Login"),
                    ("2", "Register"),
                    ("3", "Continue as guest"),
                    ("4", "Exit")
                ]
            
            # Display all options
            for num, text in options:
                print(Fore.CYAN + f"{num}. {text}")
            
            choice = input(Fore.YELLOW + "\nEnter your choice: " + Style.RESET_ALL).strip().lower()
            
            if self.current_session:
                if choice == "1":
                    joke_menu = JokeMenu(self.current_session, self.joke_api)
                    joke_menu.display()
                elif choice == "2":
                    self.show_history_and_stats()
                elif choice == "3":
                    self.change_password()
                elif choice == "4":
                    self.current_session = None
                    print(Fore.GREEN + "Successfully logged out!")
                elif choice == "a" and self.current_session.role in [UserRole.ADMIN, UserRole.MODERATOR]:
                    admin_panel = AdminPanel(self.user_manager, self.joke_api)
                    admin_panel.display()
                else:
                    print(Fore.RED + "Invalid choice!")
            else:
                if choice == "1":
                    self.current_session = self.user_manager.authenticate("127.0.0.1")  # In prod, use real IP
                elif choice == "2":
                    self.user_manager.register_user("127.0.0.1")
                elif choice == "3":
                    guest_session = UserSession(
                        username="guest",
                        role=UserRole.USER,
                        login_time=datetime.now(),
                        last_activity=datetime.now(),
                        token="guest_token",
                        expiry=datetime.now() + TOKEN_EXPIRY,
                        ip_address="127.0.0.1"
                    )
                    joke_menu = JokeMenu(guest_session, self.joke_api)
                    joke_menu.display()
                elif choice == "4":
                    return
                else:
                    print(Fore.RED + "Invalid choice!")

    def change_password(self):
        """Handle password change flow"""
        if not self.current_session:
            print(Fore.RED + "Not logged in!")
            return
            
        if self.user_manager.change_password(self.current_session.username):
            self.current_session = None  # Force re-login after password change

    def show_history_and_stats(self):
        """Display user's joke history and statistics"""
        if not self.current_session:
            print(Fore.RED + "Not logged in!")
            return
            
        history_manager = JokeHistoryManager(DatabaseManager())
        user_history = history_manager.get_user_history(self.current_session.username)
        user_stats = history_manager.get_user_stats(self.current_session.username)
        
        print(Fore.YELLOW + "\n" + "="*50)
        print(Fore.CYAN + " YOUR JOKE HISTORY ".center(50, "~"))
        print(Fore.YELLOW + "="*50 + Style.RESET_ALL)
        
        if not user_history:
            print(Fore.MAGENTA + "\nNo joke history yet!")
            return
            
        for idx, joke in enumerate(reversed(user_history), 1):
            print(Fore.GREEN + f"\nJoke #{idx}:")
            print(Fore.CYAN + f"Category: {joke.category.name}")
            print(Fore.CYAN + f"Language: {joke.language}")
            if joke.sentiment:
                print(Fore.CYAN + f"Sentiment: {joke.sentiment.name}")
            if joke.rating:
                print(Fore.CYAN + f"Your rating: {joke.rating}/5")
            print(Fore.WHITE + textwrap.fill(joke.content, width=70))
            print(Fore.YELLOW + "-"*50)
        
        print(Fore.YELLOW + "\n" + "="*50)
        print(Fore.CYAN + " YOUR STATISTICS ".center(50, "~"))
        print(Fore.YELLOW + "="*50 + Style.RESET_ALL)
        
        if user_stats:
            print(Fore.GREEN + f"\nTotal jokes heard: {user_stats['total_jokes']}")
            print(Fore.GREEN + f"Favorite language: {user_stats['favorite_language']}")
            print(Fore.GREEN + f"Favorite category: {user_stats['favorite_category']}")
            print(Fore.GREEN + f"Average rating given: {user_stats['average_rating']}")
            print(Fore.GREEN + f"Global rank: #{user_stats['global_rank']}")
            
            print(Fore.CYAN + "\nSentiment distribution:")
            for sentiment, count in user_stats['sentiment_distribution'].items():
                print(f"  {sentiment}: {count}")
        
        input(Fore.YELLOW + "\nPress Enter to return to main menu..." + Style.RESET_ALL)

class JokeMenu:
    """Joke telling interface with personalization"""
    def __init__(self, session: UserSession, joke_api: JokeAPI):
        self.session = session
        self.joke_api = joke_api
        self.history_manager = JokeHistoryManager(DatabaseManager())
        self.user_preferences = self._load_preferences()

    def _load_preferences(self) -> dict:
        """Load user preferences if logged in"""
        if self.session.username == "guest":
            return {"language": "en", "favorite_categories": []}
            
        db = DatabaseManager()
        user = db.get_user(self.session.username)
        return user.get("preferences", {"language": "en", "favorite_categories": []})

    def display(self):
        """Display joke menu with customization options"""
        while True:
            print(Fore.YELLOW + "\n" + "="*50)
            print(Fore.CYAN + " JOKE MENU ".center(50, "~"))
            print(Fore.YELLOW + "="*50 + Style.RESET_ALL)
            
            print(Fore.GREEN + f"\nCurrent preferences:")
            print(Fore.CYAN + f"Language: {self.user_preferences['language']}")
            print(Fore.CYAN + f"Favorite categories: {', '.join(self.user_preferences['favorite_categories']) or 'None'}")
            
            options = [
                ("1", "Tell me a random joke"),
                ("2", "Choose joke category"),
                ("3", "Change language"),
                ("4", "Update preferences"),
                ("5", "Rate last joke"),
                ("6", "Back to main menu")
            ]
            
            for num, text in options:
                print(Fore.CYAN + f"{num}. {text}")
            
            choice = input(Fore.YELLOW + "\nEnter your choice: " + Style.RESET_ALL).strip()
            
            if choice == "1":
                self.tell_joke()
            elif choice == "2":
                self.choose_category()
            elif choice == "3":
                self.change_language()
            elif choice == "4":
                self.update_preferences()
            elif choice == "5":
                self.rate_last_joke()
            elif choice == "6":
                return
            else:
                print(Fore.RED + "Invalid choice!")

    def tell_joke(self, category: Optional[JokeCategory] = None):
        """Tell a joke with optional category"""
        try:
            # Determine category based on preferences if not specified
            if not category and self.user_preferences["favorite_categories"]:
                preferred_cats = [
                    JokeCategory[cat.upper()] 
                    for cat in self.user_preferences["favorite_categories"]
                    if cat.upper() in JokeCategory.__members__
                ]
                if preferred_cats:
                    category = random.choice(preferred_cats)
            
            joke = self.joke_api.get_joke(
                category=category or JokeCategory.NEUTRAL,
                language=self.user_preferences["language"]
            )
            
            if not joke:
                print(Fore.RED + "Failed to get a joke. Please try again later.")
                return
                
            print(Fore.YELLOW + "\n" + "="*50)
            print(Fore.CYAN + " HERE'S YOUR JOKE! ".center(50, "~"))
            print(Fore.YELLOW + "="*50 + Style.RESET_ALL)
            print(Fore.WHITE + "\n" + textwrap.fill(joke.content, width=70))
            print(Fore.YELLOW + "\n" + "="*50)
            
            # Log the joke in history
            self.history_manager.log_joke(self.session.username, joke)
            
            # Show sentiment indicator
            if joke.sentiment:
                sentiment_color = {
                    JokeSentiment.POSITIVE: Fore.GREEN,
                    JokeSentiment.NEUTRAL: Fore.YELLOW,
                    JokeSentiment.NEGATIVE: Fore.RED
                }.get(joke.sentiment, Fore.WHITE)
                print(sentiment_color + f"\nSentiment: {joke.sentiment.name}")
            
            input(Fore.YELLOW + "\nPress Enter to continue..." + Style.RESET_ALL)
            
        except Exception as e:
            logger.error(f"Error telling joke: {e}")
            print(Fore.RED + "An error occurred while fetching the joke.")

    def choose_category(self):
        """Let user select a specific joke category"""
        print(Fore.YELLOW + "\nAvailable joke categories:")
        for idx, category in enumerate(JokeCategory, 1):
            print(Fore.CYAN + f"{idx}. {category.name}")
            
        choice = input(Fore.YELLOW + "\nSelect category (1-5): " + Style.RESET_ALL).strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(JokeCategory):
                selected_category = list(JokeCategory)[choice_idx]
                self.tell_joke(selected_category)
            else:
                print(Fore.RED + "Invalid category number!")
        except ValueError:
            print(Fore.RED + "Please enter a number!")

    def change_language(self):
        """Change joke language preference"""
        languages = ['en', 'de', 'es', 'it', 'fr']  # Supported languages
        print(Fore.YELLOW + "\nAvailable languages:")
        for idx, lang in enumerate(languages, 1):
            print(Fore.CYAN + f"{idx}. {lang.upper()}")
            
        choice = input(Fore.YELLOW + "\nSelect language (1-5): " + Style.RESET_ALL).strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(languages):
                self.user_preferences["language"] = languages[choice_idx]
                self._save_preferences()
                print(Fore.GREEN + f"Language set to {languages[choice_idx].upper()}!")
            else:
                print(Fore.RED + "Invalid language number!")
        except ValueError:
            print(Fore.RED + "Please enter a number!")

    def update_preferences(self):
        """Update user preferences for joke personalization"""
        if self.session.username == "guest":
            print(Fore.RED + "Guests cannot save preferences!")
            return
            
        print(Fore.YELLOW + "\nCurrent favorite categories:")
        current_cats = self.user_preferences.get("favorite_categories", [])
        
        if not current_cats:
            print(Fore.CYAN + "None set")
        else:
            for cat in current_cats:
                print(Fore.CYAN + f"- {cat}")
                
        print(Fore.YELLOW + "\nSelect categories to add (comma separated numbers):")
        for idx, category in enumerate(JokeCategory, 1):
            print(Fore.CYAN + f"{idx}. {category.name}")
            
        choices = input(Fore.YELLOW + "\nYour selections: " + Style.RESET_ALL).strip().split(",")
        
        try:
            selected_cats = []
            for choice in choices:
                choice_idx = int(choice.strip()) - 1
                if 0 <= choice_idx < len(JokeCategory):
                    selected_cats.append(list(JokeCategory)[choice_idx].name.lower())
                    
            self.user_preferences["favorite_categories"] = selected_cats
            self._save_preferences()
            print(Fore.GREEN + "Preferences updated successfully!")
        except ValueError:
            print(Fore.RED + "Invalid input! Please enter numbers only.")

    def _save_preferences(self):
        """Save user preferences to database"""
        if self.session.username == "guest":
            return
            
        db = DatabaseManager()
        user = db.get_user(self.session.username)
        user["preferences"] = self.user_preferences
        db.update_user(self.session.username, user)

    def rate_last_joke(self):
        """Allow user to rate the last joke they heard"""
        last_joke = self.history_manager.get_user_history(self.session.username, limit=1)
        if not last_joke:
            print(Fore.RED + "No jokes in your history to rate!")
            return
            
        last_joke = last_joke[0]
        print(Fore.YELLOW + "\nLast joke you heard:")
        print(Fore.WHITE + textwrap.fill(last_joke.content, width=70))
        
        try:
            rating = int(input(Fore.YELLOW + "\nRate this joke (1-5): " + Style.RESET_ALL).strip())
            if 1 <= rating <= 5:
                # Update the joke's rating in history
                last_joke.rating = rating
                self.history_manager.log_joke(self.session.username, last_joke)
                print(Fore.GREEN + "Thanks for your rating!")
            else:
                print(Fore.RED + "Rating must be between 1 and 5!")
        except ValueError:
            print(Fore.RED + "Please enter a number between 1 and 5!")

class AdminPanel:
    """Administrative interface for managing the application"""
    def __init__(self, user_manager: UserManager, joke_api: JokeAPI):
        self.user_manager = user_manager
        self.joke_api = joke_api
        self.db = DatabaseManager()
        self.history_manager = JokeHistoryManager(self.db)

    def display(self):
        """Display admin menu"""
        while True:
            print(Fore.YELLOW + "\n" + "="*50)
            print(Fore.CYAN + " ADMIN PANEL ".center(50, "~"))
            print(Fore.YELLOW + "="*50 + Style.RESET_ALL)
            
            options = [
                ("1", "View system statistics"),
                ("2", "View user accounts"),
                ("3", "Reset user password"),
                ("4", "View locked accounts"),
                ("5", "Unlock account"),
                ("6", "Back to main menu")
            ]
            
            for num, text in options:
                print(Fore.CYAN + f"{num}. {text}")
            
            choice = input(Fore.YELLOW + "\nEnter your choice: " + Style.RESET_ALL).strip()
            
            if choice == "1":
                self.view_system_stats()
            elif choice == "2":
                self.view_user_accounts()
            elif choice == "3":
                self.user_manager.reset_password("admin")  # Assuming admin is logged in
            elif choice == "4":
                self.view_locked_accounts()
            elif choice == "5":
                self.unlock_account()
            elif choice == "6":
                return
            else:
                print(Fore.RED + "Invalid choice!")

    def view_system_stats(self):
        """Display comprehensive system statistics"""
        stats = self.history_manager.get_global_stats()
        
        print(Fore.YELLOW + "\n" + "="*50)
        print(Fore.CYAN + " SYSTEM STATISTICS ".center(50, "~"))
        print(Fore.YELLOW + "="*50 + Style.RESET_ALL)
        
        print(Fore.GREEN + f"\nTotal jokes told: {stats['total_jokes_told']}")
        print(Fore.GREEN + f"Daily average: {stats['daily_average']} jokes/day")
        
        print(Fore.CYAN + "\nTop 5 jokes:")
        for joke, count in stats['top_jokes']:
            print(Fore.WHITE + f"- {joke[:50]}... ({count} times)")
            
        print(Fore.CYAN + "\nJokes by category:")
        for category, count in stats['top_categories']:
            print(Fore.WHITE + f"- {category}: {count}")
            
        print(Fore.CYAN + "\nJokes by language:")
        for language, count in stats['top_languages']:
            print(Fore.WHITE + f"- {language}: {count}")
            
        print(Fore.CYAN + "\nTop 5 active users:")
        for user, count in stats['top_users']:
            print(Fore.WHITE + f"- {user}: {count} jokes")
            
        input(Fore.YELLOW + "\nPress Enter to continue..." + Style.RESET_ALL)

    def view_user_accounts(self):
        """Display list of all user accounts"""
        users = self.db.read_file(self.db.users_file)
        
        print(Fore.YELLOW + "\n" + "="*50)
        print(Fore.CYAN + " USER ACCOUNTS ".center(50, "~"))
        print(Fore.YELLOW + "="*50 + Style.RESET_ALL)
        
        print(Fore.CYAN + f"\n{'Username':<20}{'Role':<15}{'Created At':<25}{'Last Login':<25}")
        print(Fore.YELLOW + "-"*85)
        
        for username, data in users.items():
            role = data.get('role', 'USER')
            created = data.get('created_at', 'Unknown')[:25]
            last_login = data.get('last_login', 'Never')[:25]
            print(Fore.WHITE + f"{username:<20}{role:<15}{created:<25}{last_login:<25}")
            
        input(Fore.YELLOW + "\nPress Enter to continue..." + Style.RESET_ALL)

    def view_locked_accounts(self):
        """Display accounts currently locked due to failed attempts"""
        failed_logins = self.db.read_file(self.db.failed_logins_file)
        
        print(Fore.YELLOW + "\n" + "="*50)
        print(Fore.CYAN + " LOCKED ACCOUNTS ".center(50, "~"))
        print(Fore.YELLOW + "="*50 + Style.RESET_ALL)
        
        if not failed_logins:
            print(Fore.GREEN + "\nNo accounts currently locked!")
            input(Fore.YELLOW + "\nPress Enter to continue..." + Style.RESET_ALL)
            return
            
        print(Fore.CYAN + f"\n{'Username':<20}{'Failed Attempts':<15}{'Last Attempt':<25}{'IP Address':<15}")
        print(Fore.YELLOW + "-"*85)
        
        for username, data in failed_logins.items():
            attempts = data.get('count', 0)
            last_attempt = data.get('last_attempt', 'Unknown')[:25]
            ip = data.get('ip_address', 'Unknown')[:15]
            print(Fore.WHITE + f"{username:<20}{attempts:<15}{last_attempt:<25}{ip:<15}")
            
        input(Fore.YELLOW + "\nPress Enter to continue..." + Style.RESET_ALL)

    def unlock_account(self):
        """Unlock a user account that was locked due to failed attempts"""
        failed_logins = self.db.read_file(self.db.failed_logins_file)
        
        if not failed_logins:
            print(Fore.GREEN + "\nNo accounts currently locked!")
            return
            
        print(Fore.YELLOW + "\nLocked accounts:")
        for idx, username in enumerate(failed_logins.keys(), 1):
            print(Fore.CYAN + f"{idx}. {username}")
            
        choice = input(Fore.YELLOW + "\nSelect account to unlock (number): " + Style.RESET_ALL).strip()
        
        try:
            choice_idx = int(choice) - 1
            username = list(failed_logins.keys())[choice_idx]
            self.db.reset_failed_logins(username)
            print(Fore.GREEN + f"\nAccount {username} unlocked successfully!")
        except (ValueError, IndexError):
            print(Fore.RED + "Invalid selection!")
            
        input(Fore.YELLOW + "\nPress Enter to continue..." + Style.RESET_ALL)

class JokeGame:
    """Main application controller"""
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.user_manager = UserManager(self.db_manager)
        self.joke_api = JokeAPI()
        self.main_menu = MainMenu(self.user_manager, self.joke_api)

    def run(self):
        """Run the main application loop"""
        print(Fore.YELLOW + "\n" + "="*50)
        print(Fore.CYAN + " WELCOME TO JOKE TELLER 2.0! ".center(50, "~"))
        print(Fore.YELLOW + "="*50 + Style.RESET_ALL)
        print(Fore.MAGENTA + "\nThe most advanced joke telling application!")
        
        try:
            self.main_menu.display()
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nGoodbye! Thanks for laughing with us!")
        except Exception as e:
            logger.exception("Application error")
            print(Fore.RED + f"\nAn error occurred: {str(e)}")
        finally:
            print(Fore.YELLOW + "\n" + "="*50)
            print(Fore.CYAN + " THANKS FOR USING JOKE TELLER! ".center(50, "~"))
            print(Fore.YELLOW + "="*50 + Style.RESET_ALL)

if __name__ == "__main__":
    try:
        # Initialize OpenAI API (would use environment variables in production)
        openai.api_key = "your-api-key-here"  # Replace with actual key
        
        game = JokeGame()
        game.run()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nProgram terminated by user")
    except Exception as e:
        logger.exception("An error occurred")
        print(Fore.RED + f"\nAn error occurred: {str(e)}")
