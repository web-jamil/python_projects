# import json
# import os

# class BankAccount:
#     def __init__(self, account_holder, balance=0.0, account_type="savings"):
#         self.account_holder = account_holder
#         self.balance = balance
#         self.account_type = account_type

#     def deposit(self, amount):
#         """Deposit money into the account."""
#         if amount <= 0:
#             print("Deposit amount must be greater than zero.")
#         else:
#             self.balance += amount
#             print(f"Deposited {amount}. Current balance: {self.balance}")

#     def withdraw(self, amount):
#         """Withdraw money from the account."""
#         if amount <= 0:
#             print("Withdrawal amount must be greater than zero.")
#         elif amount > self.balance:
#             print("Insufficient funds!")
#         else:
#             self.balance -= amount
#             print(f"Withdrew {amount}. Current balance: {self.balance}")

#     def get_balance(self):
#         """Get the current balance of the account."""
#         return self.balance

#     def __str__(self):
#         """Return account details as a string."""
#         return f"Account Holder: {self.account_holder}, Type: {self.account_type}, Balance: {self.balance}"

#     def to_dict(self):
#         """Convert the bank account details to a dictionary for JSON storage."""
#         return {
#             "account_holder": self.account_holder,
#             "balance": self.balance,
#             "account_type": self.account_type
#         }

#     @staticmethod
#     def from_dict(data):
#         """Create a BankAccount instance from a dictionary."""
#         return BankAccount(data["account_holder"], data["balance"], data["account_type"])


# class Bank:
#     def __init__(self, filename="accounts.json"):
#         self.filename = filename
#         self.accounts = self.load_accounts()

#     def load_accounts(self):
#         """Load accounts from the JSON file."""
#         accounts = {}
#         if os.path.exists(self.filename):
#             try:
#                 with open(self.filename, 'r') as file:
#                     data = json.load(file)
#                     for account_data in data:
#                         account = BankAccount.from_dict(account_data)
#                         accounts[account.account_holder] = account
#             except json.JSONDecodeError:
#                 print("Error: Invalid file format or corrupted file.")
#             except Exception as e:
#                 print(f"Error loading accounts: {e}")
#         return accounts

#     def save_accounts(self):
#         """Save accounts to the JSON file."""
#         try:
#             with open(self.filename, 'w') as file:
#                 json.dump([account.to_dict() for account in self.accounts.values()], file, indent=4)
#         except Exception as e:
#             print(f"Error saving accounts: {e}")

#     def create_account(self, account_holder, account_type="savings"):
#         """Create a new account."""
#         if account_holder in self.accounts:
#             print("Account already exists for this holder.")
#         else:
#             new_account = BankAccount(account_holder, 0.0, account_type)
#             self.accounts[account_holder] = new_account
#             self.save_accounts()
#             print(f"Account created for {account_holder}.")

#     def deposit(self, account_holder, amount):
#         """Deposit money into an account."""
#         if account_holder in self.accounts:
#             self.accounts[account_holder].deposit(amount)
#             self.save_accounts()
#         else:
#             print("Account not found.")

#     def withdraw(self, account_holder, amount):
#         """Withdraw money from an account."""
#         if account_holder in self.accounts:
#             self.accounts[account_holder].withdraw(amount)
#             self.save_accounts()
#         else:
#             print("Account not found.")

#     def check_balance(self, account_holder):
#         """Check the balance of an account."""
#         if account_holder in self.accounts:
#             print(f"Current balance for {account_holder}: {self.accounts[account_holder].get_balance()}")
#         else:
#             print("Account not found.")

#     def list_accounts(self):
#         """List all bank accounts."""
#         if not self.accounts:
#             print("No accounts available.")
#         else:
#             for account in self.accounts.values():
#                 print(account)

#     def is_account_exists(self, account_holder):
#         """Check if an account exists."""
#         return account_holder in self.accounts




# def print_menu():
#     """Print the main menu."""
#     print("\n--- Bank Management System ---")
#     print("1. Create Account")
#     print("2. Deposit Money")
#     print("3. Withdraw Money")
#     print("4. Check Balance")
#     print("5. List All Accounts")
#     print("6. Exit")
#     print("-----------------------------")

# def main():
#     bank = Bank()

#     while True:
#         print_menu()
#         choice = input("Enter your choice: ")

#         if choice == '1':
#             account_holder = input("Enter account holder name: ").strip()
#             account_type = input("Enter account type (savings/checking): ").strip().lower()
#             if account_type not in ["savings", "checking"]:
#                 print("Invalid account type. Defaulting to 'savings'.")
#                 account_type = "savings"
#             bank.create_account(account_holder, account_type)

#         elif choice == '2':
#             account_holder = input("Enter account holder name: ").strip()
#             if bank.is_account_exists(account_holder):
#                 try:
#                     amount = float(input("Enter amount to deposit: ").strip())
#                     bank.deposit(account_holder, amount)
#                 except ValueError:
#                     print("Invalid amount. Please enter a valid number.")
#             else:
#                 print("Account not found.")

#         elif choice == '3':
#             account_holder = input("Enter account holder name: ").strip()
#             if bank.is_account_exists(account_holder):
#                 try:
#                     amount = float(input("Enter amount to withdraw: ").strip())
#                     bank.withdraw(account_holder, amount)
#                 except ValueError:
#                     print("Invalid amount. Please enter a valid number.")
#             else:
#                 print("Account not found.")

#         elif choice == '4':
#             account_holder = input("Enter account holder name: ").strip()
#             if bank.is_account_exists(account_holder):
#                 bank.check_balance(account_holder)
#             else:
#                 print("Account not found.")

#         elif choice == '5':
#             bank.list_accounts()

#         elif choice == '6':
#             print("Exiting the Bank Management System.")
#             break

#         else:
#             print("Invalid choice, please try again.")

# if __name__ == "__main__":
#     main()



import json
import os
import uuid
from datetime import datetime
import hashlib
import getpass
from typing import List, Dict, Optional

class Transaction:
    def __init__(self, transaction_type: str, amount: float, description: str = ""):
        self.transaction_id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        self.transaction_type = transaction_type  # 'deposit', 'withdrawal', 'transfer'
        self.amount = amount
        self.description = description

    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "timestamp": self.timestamp,
            "type": self.transaction_type,
            "amount": self.amount,
            "description": self.description
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Transaction':
        transaction = Transaction(
            data["type"],
            data["amount"],
            data.get("description", "")
        )
        transaction.transaction_id = data["transaction_id"]
        transaction.timestamp = data["timestamp"]
        return transaction

class BankAccount:
    def __init__(self, account_holder: str, account_number: str, balance: float = 0.0, 
                 account_type: str = "savings", overdraft_limit: float = 0.0):
        self.account_holder = account_holder
        self.account_number = account_number
        self.balance = balance
        self.account_type = account_type
        self.overdraft_limit = overdraft_limit
        self.transactions: List[Transaction] = []
        self.interest_rate = self._get_interest_rate()
        self.last_interest_calculation = datetime.now().isoformat()

    def _get_interest_rate(self) -> float:
        rates = {
            "savings": 0.03,  # 3%
            "checking": 0.01,  # 1%
            "business": 0.02   # 2%
        }
        return rates.get(self.account_type, 0.0)

    def deposit(self, amount: float, description: str = "") -> bool:
        if amount <= 0:
            print("Deposit amount must be positive.")
            return False
        
        self.balance += amount
        self.transactions.append(Transaction("deposit", amount, description))
        print(f"Deposited {amount:.2f}. New balance: {self.balance:.2f}")
        return True

    def withdraw(self, amount: float, description: str = "") -> bool:
        if amount <= 0:
            print("Withdrawal amount must be positive.")
            return False
        
        available_balance = self.balance + self.overdraft_limit
        if amount > available_balance:
            print(f"Insufficient funds. Available: {available_balance:.2f}")
            return False
        
        self.balance -= amount
        self.transactions.append(Transaction("withdrawal", amount, description))
        print(f"Withdrew {amount:.2f}. New balance: {self.balance:.2f}")
        return True

    def transfer(self, amount: float, recipient: 'BankAccount', description: str = "") -> bool:
        if amount <= 0:
            print("Transfer amount must be positive.")
            return False
        
        if not self.withdraw(amount, f"Transfer to {recipient.account_number}"):
            return False
        
        if not recipient.deposit(amount, f"Transfer from {self.account_number}"):
            # Refund if deposit fails
            self.deposit(amount, "Refund for failed transfer")
            return False
        
        print(f"Transferred {amount:.2f} to account {recipient.account_number}")
        return True

    def calculate_interest(self) -> float:
        now = datetime.now()
        last_calc = datetime.fromisoformat(self.last_interest_calculation)
        days = (now - last_calc).days
        
        if days <= 0:
            return 0.0
        
        interest = self.balance * self.interest_rate * (days / 365)
        if interest > 0:
            self.deposit(interest, "Interest payment")
            self.last_interest_calculation = now.isoformat()
        
        return interest

    def get_transaction_history(self, limit: int = 10) -> List[Transaction]:
        return self.transactions[-limit:]

    def to_dict(self) -> Dict:
        return {
            "account_holder": self.account_holder,
            "account_number": self.account_number,
            "balance": self.balance,
            "account_type": self.account_type,
            "overdraft_limit": self.overdraft_limit,
            "transactions": [t.to_dict() for t in self.transactions],
            "interest_rate": self.interest_rate,
            "last_interest_calculation": self.last_interest_calculation
        }

    @staticmethod
    def from_dict(data: Dict) -> 'BankAccount':
        account = BankAccount(
            data["account_holder"],
            data["account_number"],
            data["balance"],
            data["account_type"],
            data.get("overdraft_limit", 0.0)
        )
        account.transactions = [Transaction.from_dict(t) for t in data.get("transactions", [])]
        account.interest_rate = data.get("interest_rate", 0.0)
        account.last_interest_calculation = data.get("last_interest_calculation", datetime.now().isoformat())
        return account

class User:
    def __init__(self, username: str, password_hash: str, role: str = "customer"):
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'customer', 'teller', 'manager', 'admin'
        self.accounts: List[str] = []  # List of account numbers

    def verify_password(self, password: str) -> bool:
        return self.password_hash == self._hash_password(password)

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role,
            "accounts": self.accounts
        }

    @staticmethod
    def from_dict(data: Dict) -> 'User':
        user = User(
            data["username"],
            data["password_hash"],
            data.get("role", "customer")
        )
        user.accounts = data.get("accounts", [])
        return user

class Bank:
    def __init__(self, data_dir: str = "bank_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.accounts: Dict[str, BankAccount] = {}
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        
        self._load_data()

    def _load_data(self):
        # Load accounts
        accounts_file = os.path.join(self.data_dir, "accounts.json")
        if os.path.exists(accounts_file):
            with open(accounts_file, "r") as f:
                accounts_data = json.load(f)
                self.accounts = {acc["account_number"]: BankAccount.from_dict(acc) for acc in accounts_data}

        # Load users
        users_file = os.path.join(self.data_dir, "users.json")
        if os.path.exists(users_file):
            with open(users_file, "r") as f:
                users_data = json.load(f)
                self.users = {user["username"]: User.from_dict(user) for user in users_data}

    def _save_data(self):
        # Save accounts
        accounts_file = os.path.join(self.data_dir, "accounts.json")
        with open(accounts_file, "w") as f:
            json.dump([acc.to_dict() for acc in self.accounts.values()], f, indent=2)

        # Save users
        users_file = os.path.join(self.data_dir, "users.json")
        with open(users_file, "w") as f:
            json.dump([user.to_dict() for user in self.users.values()], f, indent=2)

    def generate_account_number(self) -> str:
        while True:
            account_number = str(uuid.uuid4().int)[:10]
            if account_number not in self.accounts:
                return account_number

    def create_account(self, account_holder: str, account_type: str = "savings", 
                      initial_deposit: float = 0.0) -> Optional[BankAccount]:
        account_number = self.generate_account_number()
        new_account = BankAccount(account_holder, account_number, initial_deposit, account_type)
        
        self.accounts[account_number] = new_account
        if self.current_user:
            self.current_user.accounts.append(account_number)
        
        self._save_data()
        print(f"Account created successfully. Account number: {account_number}")
        return new_account

    def login(self, username: str, password: str) -> bool:
        if username in self.users and self.users[username].verify_password(password):
            self.current_user = self.users[username]
            print(f"Welcome, {username}!")
            return True
        print("Invalid username or password.")
        return False

    def register(self, username: str, password: str, role: str = "customer") -> bool:
        if username in self.users:
            print("Username already exists.")
            return False
        
        new_user = User(username, User._hash_password(password), role)
        self.users[username] = new_user
        self._save_data()
        print("Registration successful. Please login.")
        return True

    def get_account(self, account_number: str) -> Optional[BankAccount]:
        return self.accounts.get(account_number)

    def calculate_all_interest(self):
        for account in self.accounts.values():
            account.calculate_interest()
        self._save_data()

    def get_user_accounts(self) -> List[BankAccount]:
        if not self.current_user:
            return []
        return [self.accounts[acc_num] for acc_num in self.current_user.accounts 
                if acc_num in self.accounts]

def print_main_menu():
    print("\n=== Bank Management System ===")
    print("1. Login")
    print("2. Register")
    print("3. Exit")
    print("=============================")

def print_customer_menu():
    print("\n=== Customer Menu ===")
    print("1. Create Account")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Transfer")
    print("5. View Balance")
    print("6. Transaction History")
    print("7. List Accounts")
    print("8. Logout")
    print("=====================")

def main():
    bank = Bank()
    
    while True:
        if not bank.current_user:
            print_main_menu()
            choice = input("Enter your choice: ")

            if choice == '1':  # Login
                username = input("Username: ")
                password = getpass.getpass("Password: ")
                bank.login(username, password)

            elif choice == '2':  # Register
                username = input("Choose a username: ")
                password = getpass.getpass("Choose a password: ")
                bank.register(username, password)

            elif choice == '3':  # Exit
                print("Thank you for using our bank system. Goodbye!")
                break

            else:
                print("Invalid choice, please try again.")
        
        else:  # User is logged in
            print_customer_menu()
            choice = input("Enter your choice: ")

            if choice == '1':  # Create Account
                account_type = input("Account type (savings/checking/business): ").lower()
                if account_type not in ["savings", "checking", "business"]:
                    print("Invalid account type. Defaulting to savings.")
                    account_type = "savings"
                
                initial_deposit = 0.0
                deposit_input = input("Initial deposit amount (optional): ")
                if deposit_input:
                    try:
                        initial_deposit = float(deposit_input)
                    except ValueError:
                        print("Invalid amount. Starting with 0 balance.")
                
                bank.create_account(bank.current_user.username, account_type, initial_deposit)

            elif choice == '2':  # Deposit
                account_number = input("Enter account number: ")
                account = bank.get_account(account_number)
                if account and account_number in bank.current_user.accounts:
                    try:
                        amount = float(input("Enter deposit amount: "))
                        description = input("Enter description (optional): ")
                        account.deposit(amount, description)
                        bank._save_data()
                    except ValueError:
                        print("Invalid amount entered.")
                else:
                    print("Account not found or not authorized.")

            elif choice == '3':  # Withdraw
                account_number = input("Enter account number: ")
                account = bank.get_account(account_number)
                if account and account_number in bank.current_user.accounts:
                    try:
                        amount = float(input("Enter withdrawal amount: "))
                        description = input("Enter description (optional): ")
                        account.withdraw(amount, description)
                        bank._save_data()
                    except ValueError:
                        print("Invalid amount entered.")
                else:
                    print("Account not found or not authorized.")

            elif choice == '4':  # Transfer
                from_account_num = input("Enter your account number: ")
                from_account = bank.get_account(from_account_num)
                
                if from_account and from_account_num in bank.current_user.accounts:
                    to_account_num = input("Enter recipient account number: ")
                    to_account = bank.get_account(to_account_num)
                    
                    if to_account:
                        try:
                            amount = float(input("Enter transfer amount: "))
                            description = input("Enter description (optional): ")
                            if from_account.transfer(amount, to_account, description):
                                bank._save_data()
                        except ValueError:
                            print("Invalid amount entered.")
                    else:
                        print("Recipient account not found.")
                else:
                    print("Your account not found or not authorized.")

            elif choice == '5':  # View Balance
                accounts = bank.get_user_accounts()
                if not accounts:
                    print("No accounts found.")
                for account in accounts:
                    print(f"Account {account.account_number}: {account.balance:.2f}")

            elif choice == '6':  # Transaction History
                account_number = input("Enter account number: ")
                account = bank.get_account(account_number)
                if account and account_number in bank.current_user.accounts:
                    transactions = account.get_transaction_history()
                    if not transactions:
                        print("No transactions found.")
                    for t in transactions:
                        print(f"{t.timestamp} - {t.transaction_type}: {t.amount:.2f} - {t.description}")
                else:
                    print("Account not found or not authorized.")

            elif choice == '7':  # List Accounts
                accounts = bank.get_user_accounts()
                if not accounts:
                    print("No accounts found.")
                for account in accounts:
                    print(f"Account {account.account_number} ({account.account_type}): {account.balance:.2f}")

            elif choice == '8':  # Logout
                bank.current_user = None
                print("Successfully logged out.")

            else:
                print("Invalid choice, please try again.")

if __name__ == "__main__":
    # Create an admin user if none exists
    if not os.path.exists("bank_data/users.json"):
        bank = Bank()
        bank.register("admin", "admin123", "admin")
    
    main()