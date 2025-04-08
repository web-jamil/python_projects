# import json
# import os

# class Book:
#     def __init__(self, book_id, title, author, genre, available_copies):
#         self.book_id = book_id
#         self.title = title
#         self.author = author
#         self.genre = genre
#         self.available_copies = available_copies
    
#     def __str__(self):
#         return f"ID: {self.book_id}, Title: {self.title}, Author: {self.author}, Genre: {self.genre}, Available Copies: {self.available_copies}"

# class Library:
#     def __init__(self):
#         self.books = []
#         self.load_data()

#     def load_data(self):
#         """Load library data from a file."""
#         if os.path.exists("library_data.json"):
#             with open("library_data.json", "r") as file:
#                 data = json.load(file)
#                 for book_data in data:
#                     book = Book(book_data["book_id"], book_data["title"], book_data["author"], book_data["genre"], book_data["available_copies"])
#                     self.books.append(book)

#     def save_data(self):
#         """Save library data to a file."""
#         data = []
#         for book in self.books:
#             data.append({
#                 "book_id": book.book_id,
#                 "title": book.title,
#                 "author": book.author,
#                 "genre": book.genre,
#                 "available_copies": book.available_copies
#             })
#         with open("library_data.json", "w") as file:
#             json.dump(data, file, indent=4)
    
#     def add_book(self, title, author, genre, available_copies):
#         """Add a new book to the library."""
#         book_id = len(self.books) + 1  # Automatically generate book ID based on the current count
#         new_book = Book(book_id, title, author, genre, available_copies)
#         self.books.append(new_book)
#         print(f"Book '{title}' by {author} added successfully.")

#     def remove_book(self, book_id):
#         """Remove a book from the library."""
#         for book in self.books:
#             if book.book_id == book_id:
#                 self.books.remove(book)
#                 print(f"Book with ID {book_id} has been removed.")
#                 return
#         print("Book not found.")

#     def search_book(self, search_term):
#         """Search for books by title or author."""
#         found_books = [book for book in self.books if search_term.lower() in book.title.lower() or search_term.lower() in book.author.lower()]
        
#         if found_books:
#             print("Search results:")
#             for book in found_books:
#                 print(book)
#         else:
#             print("No books found matching your search.")

#     def display_books(self):
#         """Display all books in the library."""
#         if not self.books:
#             print("No books available in the library.")
#         else:
#             print("\nAll Books in Library:")
#             for book in self.books:
#                 print(book)
    
#     def checkout_book(self, book_id):
#         """Checkout a book (decrease the available copies)."""
#         for book in self.books:
#             if book.book_id == book_id:
#                 if book.available_copies > 0:
#                     book.available_copies -= 1
#                     print(f"Book '{book.title}' checked out successfully. Remaining copies: {book.available_copies}")
#                     return
#                 else:
#                     print("Sorry, no copies available for checkout.")
#                     return
#         print("Book not found.")
    
#     def return_book(self, book_id):
#         """Return a book (increase the available copies)."""
#         for book in self.books:
#             if book.book_id == book_id:
#                 book.available_copies += 1
#                 print(f"Book '{book.title}' returned successfully. Available copies: {book.available_copies}")
#                 return
#         print("Book not found.")

# class LibraryManagementSystem:
#     def __init__(self):
#         self.library = Library()
#         self.run()

#     def display_menu(self):
#         """Display the menu to the user."""
#         print("\nLibrary Management System")
#         print("1. Add Book")
#         print("2. Remove Book")
#         print("3. Search Book")
#         print("4. Display All Books")
#         print("5. Checkout Book")
#         print("6. Return Book")
#         print("7. Exit")

#     def get_choice(self):
#         """Get the user's menu choice."""
#         while True:
#             try:
#                 choice = int(input("Enter your choice (1-7): "))
#                 if choice in range(1, 8):
#                     return choice
#                 else:
#                     print("Invalid choice. Please choose a number between 1 and 7.")
#             except ValueError:
#                 print("Invalid input. Please enter a valid number.")

#     def handle_choice(self, choice):
#         """Handle the user's menu choice."""
#         if choice == 1:  # Add Book
#             title = input("Enter the book title: ")
#             author = input("Enter the author name: ")
#             genre = input("Enter the genre: ")
#             available_copies = int(input("Enter the number of available copies: "))
#             self.library.add_book(title, author, genre, available_copies)

#         elif choice == 2:  # Remove Book
#             book_id = int(input("Enter the book ID to remove: "))
#             self.library.remove_book(book_id)

#         elif choice == 3:  # Search Book
#             search_term = input("Enter a search term (title or author): ")
#             self.library.search_book(search_term)

#         elif choice == 4:  # Display All Books
#             self.library.display_books()

#         elif choice == 5:  # Checkout Book
#             book_id = int(input("Enter the book ID to checkout: "))
#             self.library.checkout_book(book_id)

#         elif choice == 6:  # Return Book
#             book_id = int(input("Enter the book ID to return: "))
#             self.library.return_book(book_id)

#         elif choice == 7:  # Exit
#             self.library.save_data()
#             print("Exiting the system. All data has been saved.")
#             exit()

#     def run(self):
#         """Run the Library Management System."""
#         while True:
#             self.display_menu()
#             choice = self.get_choice()
#             self.handle_choice(choice)

# if __name__ == "__main__":
#     LibraryManagementSystem()



import sqlite3
import datetime
import hashlib
import qrcode
from faker import Faker
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
import random
import string
from enum import Enum

# Initialize database
conn = sqlite3.connect('library.db', check_same_thread=False)
cursor = conn.cursor()

# Create modern tables
cursor.executescript('''
CREATE TABLE IF NOT EXISTS branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    contact TEXT NOT NULL,
    geo_coordinates TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'librarian', 'patron')),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    rfid_tag TEXT UNIQUE,
    branch_id INTEGER REFERENCES branches(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    publisher TEXT,
    publication_year INTEGER,
    genre TEXT,
    total_copies INTEGER DEFAULT 1,
    available_copies INTEGER DEFAULT 1,
    barcode TEXT UNIQUE,
    qr_code TEXT,
    branch_id INTEGER REFERENCES branches(id),
    metadata TEXT,  -- JSON for additional fields
    ai_embedding BLOB  -- For recommendation system
);

CREATE TABLE IF NOT EXISTS digital_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER REFERENCES books(id),
    format TEXT NOT NULL CHECK(format IN ('epub', 'pdf', 'audiobook')),
    drm_key TEXT,  -- Blockchain hash for digital rights
    file_path TEXT NOT NULL,
    access_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL REFERENCES books(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    loan_date TIMESTAMP NOT NULL,
    due_date TIMESTAMP NOT NULL,
    return_date TIMESTAMP,
    status TEXT NOT NULL CHECK(status IN ('active', 'returned', 'overdue', 'lost')),
    renewal_count INTEGER DEFAULT 0,
    fine_amount REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL REFERENCES books(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP,
    status TEXT NOT NULL CHECK(status IN ('pending', 'fulfilled', 'cancelled'))
);

CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    event_data TEXT NOT NULL,  -- JSON
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    branch_id INTEGER REFERENCES branches(id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    book_id INTEGER NOT NULL REFERENCES books(id),
    score REAL NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL CHECK(source IN ('ai', 'popularity', 'similar_users'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS books_fts USING fts5(
    title, author, publisher, genre, 
    tokenize="porter unicode61"
);
''')

conn.commit()

## Modern Features Implementation

class BookStatus(Enum):
    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"
    RESERVED = "reserved"
    OVERDUE = "overdue"

@dataclass
class DigitalRights:
    owner_id: int
    license_type: str
    expiration: str
    blockchain_hash: str

class LibrarySystem:
    def __init__(self):
        self.faker = Faker()
        self._setup_triggers()
        
    def _setup_triggers(self):
        """Create database triggers for modern features"""
        cursor.executescript('''
        -- Update available copies when books are loaned
        CREATE TRIGGER IF NOT EXISTS update_available_copies_loan
        AFTER INSERT ON loans
        BEGIN
            UPDATE books 
            SET available_copies = available_copies - 1 
            WHERE id = NEW.book_id;
            
            -- Log analytics event
            INSERT INTO analytics(event_type, event_data, user_id, branch_id)
            VALUES('book_loan', json_object('book_id', NEW.book_id, 'loan_id', NEW.id), NEW.user_id, NEW.branch_id);
        END;

        -- Update available copies when books are returned
        CREATE TRIGGER IF NOT EXISTS update_available_copies_return
        AFTER UPDATE OF return_date ON loans
        WHEN NEW.return_date IS NOT NULL
        BEGIN
            UPDATE books 
            SET available_copies = available_copies + 1 
            WHERE id = NEW.book_id;
            
            -- Calculate fine if overdue
            UPDATE loans
            SET fine_amount = 
                CASE 
                    WHEN julianday(NEW.return_date) - julianday(NEW.due_date) > 0 
                    THEN (julianday(NEW.return_date) - julianday(NEW.due_date)) * 0.50  -- $0.50/day fine
                    ELSE 0 
                END
            WHERE id = NEW.id;
        END;

        -- FTS index maintenance
        CREATE TRIGGER IF NOT EXISTS books_after_insert
        AFTER INSERT ON books
        BEGIN
            INSERT INTO books_fts(rowid, title, author, publisher, genre)
            VALUES (NEW.id, NEW.title, NEW.author, NEW.publisher, NEW.genre);
        END;
        ''')
        conn.commit()

    # Modern Feature: QR Code/Barcode Generation
    def generate_book_identifiers(self, book_id: int) -> Dict[str, str]:
        """Generate barcode and QR code for physical books"""
        barcode = ''.join(random.choices(string.digits, k=12))
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"LIB-BOOK-{book_id}")
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        qr_path = f"static/qrcodes/{book_id}.png"
        img.save(qr_path)
        
        cursor.execute('''
        UPDATE books SET barcode = ?, qr_code = ? WHERE id = ?
        ''', (barcode, qr_path, book_id))
        conn.commit()
        
        return {'barcode': barcode, 'qr_code': qr_path}

    # Modern Feature: Digital Rights Management
    def register_digital_rights(self, book_id: int, file_path: str, format: str) -> DigitalRights:
        """Register digital asset with blockchain-based DRM"""
        drm_key = hashlib.sha256(f"{book_id}{datetime.datetime.now().isoformat()}".encode()).hexdigest()
        cursor.execute('''
        INSERT INTO digital_assets (book_id, format, drm_key, file_path)
        VALUES (?, ?, ?, ?)
        ''', (book_id, format, drm_key, file_path))
        conn.commit()
        
        return DigitalRights(
            owner_id=1,  # Library org ID
            license_type="library_license",
            expiration="2099-12-31",
            blockchain_hash=drm_key
        )

    # Modern Feature: AI-Powered Search
    def search_books(self, query: str, limit: int = 10) -> List[Dict]:
        """Full-text search with ranking"""
        cursor.execute('''
        SELECT b.id, b.title, b.author, b.available_copies, 
               snippet(books_fts, 0, '<b>', '</b>', '...', 20) as snippet
        FROM books b
        JOIN books_fts f ON b.id = f.rowid
        WHERE books_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        ''', (f"{query}*", limit))
        
        return [dict(row) for row in cursor.fetchall()]

    # Modern Feature: Predictive Analytics
    def generate_recommendations(self, user_id: int) -> List[Dict]:
        """Generate personalized recommendations using multiple strategies"""
        # 1. Get user's loan history
        cursor.execute('''
        SELECT book_id FROM loans 
        WHERE user_id = ? 
        GROUP BY book_id 
        ORDER BY COUNT(*) DESC 
        LIMIT 5
        ''', (user_id,))
        past_loans = [row[0] for row in cursor.fetchall()]
        
        # 2. Get similar users' preferences (simplified)
        similar_books = []
        if past_loans:
            placeholders = ','.join(['?']*len(past_loans))
            cursor.execute(f'''
            SELECT b.id, b.title, COUNT(l.id) as popularity
            FROM books b
            JOIN loans l ON b.id = l.book_id
            WHERE l.user_id IN (
                SELECT DISTINCT user_id FROM loans 
                WHERE book_id IN ({placeholders}) 
                AND user_id != ?
            )
            AND b.id NOT IN ({placeholders})
            GROUP BY b.id
            ORDER BY popularity DESC
            LIMIT 5
            ''', past_loans + [user_id] + past_loans)
            similar_books = [dict(row) for row in cursor.fetchall()]
        
        # 3. Get popular books
        cursor.execute('''
        SELECT b.id, b.title, COUNT(l.id) as loan_count
        FROM books b
        LEFT JOIN loans l ON b.id = l.book_id
        GROUP BY b.id
        ORDER BY loan_count DESC
        LIMIT 5
        ''')
        popular_books = [dict(row) for row in cursor.fetchall()]
        
        # Combine and deduplicate recommendations
        all_recs = {}
        for idx, book in enumerate(similar_books):
            all_recs[book['id']] = {
                'book_id': book['id'],
                'title': book['title'],
                'score': 0.8 - (idx * 0.1),  # Higher score for similar users
                'source': 'similar_users'
            }
        
        for idx, book in enumerate(popular_books):
            if book['id'] not in all_recs:
                all_recs[book['id']] = {
                    'book_id': book['id'],
                    'title': book['title'],
                    'score': 0.6 - (idx * 0.05),  # Lower score for general popularity
                    'source': 'popularity'
                }
        
        # Save recommendations
        for rec in all_recs.values():
            cursor.execute('''
            INSERT INTO recommendations (user_id, book_id, score, source)
            VALUES (?, ?, ?, ?)
            ''', (user_id, rec['book_id'], rec['score'], rec['source']))
        
        conn.commit()
        return list(all_recs.values())

    # Modern Feature: Mobile Checkout
    def mobile_checkout(self, user_id: int, book_id: int, branch_id: int) -> bool:
        """Handle mobile app checkout with QR code verification"""
        # Verify book availability
        cursor.execute('SELECT available_copies FROM books WHERE id = ?', (book_id,))
        result = cursor.fetchone()
        if not result or result[0] < 1:
            return False
        
        # Create loan record
        loan_date = datetime.datetime.now()
        due_date = loan_date + datetime.timedelta(days=14)
        
        cursor.execute('''
        INSERT INTO loans (book_id, user_id, branch_id, loan_date, due_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (book_id, user_id, branch_id, loan_date, due_date, 'active'))
        conn.commit()
        
        # Generate mobile checkout payload
        checkout_data = {
            'loan_id': cursor.lastrowid,
            'due_date': due_date.isoformat(),
            'book_title': self.get_book_title(book_id),
            'renewal_url': f"https://library.example.com/renew/{cursor.lastrowid}"
        }
        
        return checkout_data

    def get_book_title(self, book_id: int) -> str:
        cursor.execute('SELECT title FROM books WHERE id = ?', (book_id,))
        result = cursor.fetchone()
        return result[0] if result else "Unknown Title"

    # Modern Feature: Automated Fines and Notifications
    def check_overdue_loans(self):
        """Batch process for overdue loans (run daily)"""
        cursor.execute('''
        SELECT l.id, u.email, u.full_name, b.title, l.due_date
        FROM loans l
        JOIN users u ON l.user_id = u.id
        JOIN books b ON l.book_id = b.id
        WHERE l.status = 'active' 
        AND date(l.due_date) < date('now')
        ''')
        
        overdue_loans = cursor.fetchall()
        
        for loan in overdue_loans:
            loan_id, email, name, title, due_date = loan
            # Update status
            cursor.execute('''
            UPDATE loans SET status = 'overdue' WHERE id = ?
            ''', (loan_id,))
            
            # Send notification (in a real system, this would email)
            print(f"Notification sent to {email}: Overdue book '{title}' was due on {due_date}")
            
            # Log analytics event
            cursor.execute('''
            INSERT INTO analytics(event_type, event_data, user_id)
            VALUES('overdue_notification', json_object('loan_id', ?, 'book_title', ?), 
            (SELECT user_id FROM loans WHERE id = ?))
            ''', (loan_id, title, loan_id))
        
        conn.commit()
        return len(overdue_loans)

    # Modern Feature: Multi-branch Inventory Management
    def transfer_book(self, book_id: int, from_branch: int, to_branch: int) -> bool:
        """Transfer book between branches"""
        # Verify book exists at source branch
        cursor.execute('''
        SELECT 1 FROM books 
        WHERE id = ? AND branch_id = ? AND available_copies > 0
        ''', (book_id, from_branch))
        
        if not cursor.fetchone():
            return False
        
        # Update branch assignment
        cursor.execute('''
        UPDATE books SET branch_id = ? WHERE id = ?
        ''', (to_branch, book_id))
        
        # Log transfer
        cursor.execute('''
        INSERT INTO analytics(event_type, event_data)
        VALUES('book_transfer', json_object('book_id', ?, 'from_branch', ?, 'to_branch', ?))
        ''', (book_id, from_branch, to_branch))
        
        conn.commit()
        return True

# CLI Interface (simplified)
def admin_cli(library: LibrarySystem):
    print("=== Library Admin Console ===")
    while True:
        print("\n1. Add Book\n2. Search Books\n3. View Recommendations\n4. Process Overdues\n5. Exit")
        choice = input("Select option: ")
        
        if choice == '1':
            title = input("Title: ")
            author = input("Author: ")
            isbn = input("ISBN: ")
            branch_id = input("Branch ID: ")
            
            cursor.execute('''
            INSERT INTO books (title, author, isbn, branch_id)
            VALUES (?, ?, ?, ?)
            ''', (title, author, isbn, branch_id))
            book_id = cursor.lastrowid
            
            # Generate modern identifiers
            identifiers = library.generate_book_identifiers(book_id)
            print(f"Book added! Barcode: {identifiers['barcode']}")
            
        elif choice == '2':
            query = input("Search query: ")
            results = library.search_books(query)
            for book in results:
                print(f"{book['id']}: {book['title']} by {book['author']}")
                print(f"   Snippet: {book['snippet']}")
                
        elif choice == '3':
            user_id = input("User ID: ")
            recs = library.generate_recommendations(user_id)
            print("\nRecommended Books:")
            for rec in sorted(recs, key=lambda x: x['score'], reverse=True):
                print(f"- {rec['title']} (score: {rec['score']:.2f}, source: {rec['source']})")
                
        elif choice == '4':
            count = library.check_overdue_loans()
            print(f"Processed {count} overdue loans")
            
        elif choice == '5':
            break

if __name__ == "__main__":
    # Initialize with sample data
    library = LibrarySystem()
    
    # Create sample branch
    cursor.execute('''
    INSERT INTO branches (name, location, contact, geo_coordinates)
    VALUES ('Main Library', '123 Library St', '555-1234', '40.7128,-74.0060')
    ''')
    conn.commit()
    
    # Start interface
    admin_cli(library)
    conn.close()