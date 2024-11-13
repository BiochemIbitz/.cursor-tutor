import os
import csv
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class LibraryManagementSystem:
    def __init__(self):
        # Initialize database files
        self.users_db = "library_users.csv"
        self.books_db = "library_books.csv" 
        self.loans_db = "library_loans.csv"
        
        # Create database files if they don't exist
        self._initialize_databases()
    
    def _initialize_databases(self):
        """Initialize database files with headers if they don't exist"""
        if not os.path.exists(self.users_db):
            with open(self.users_db, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['user_id', 'name', 'email', 'phone', 'joined_date'])
        
        if not os.path.exists(self.books_db):
            with open(self.books_db, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['book_id', 'title', 'author', 'category', 'status'])
                
        if not os.path.exists(self.loans_db):
            with open(self.loans_db, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['loan_id', 'book_id', 'user_id', 'borrow_date', 'due_date', 'return_date'])

    def register_user(self, name: str, email: str, phone: str) -> str:
        """Register a new user and return their user ID"""
        user_id = str(uuid.uuid4())
        
        with open(self.users_db, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                user_id,
                name,
                email,
                phone,
                datetime.now().isoformat()
            ])
        return user_id

    def add_book(self, title: str, author: str, category: str) -> str:
        """Add a new book to the library and return its book ID"""
        book_id = str(uuid.uuid4())
        
        with open(self.books_db, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                book_id,
                title,
                author,
                category,
                'available'
            ])
        return book_id

    def borrow_book(self, book_id: str, user_id: str, days: int = 14) -> Optional[str]:
        """Process a book loan and return the loan ID if successful"""
        # Check if book is available
        book = self._get_book(book_id)
        if not book or book['status'] != 'available':
            return None
            
        loan_id = str(uuid.uuid4())
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=days)
        
        # Update book status
        self._update_book_status(book_id, 'borrowed')
        
        # Record loan
        with open(self.loans_db, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                loan_id,
                book_id,
                user_id,
                borrow_date.isoformat(),
                due_date.isoformat(),
                ''
            ])
        return loan_id

    def return_book(self, loan_id: str) -> bool:
        """Process a book return"""
        loan = self._get_loan(loan_id)
        if not loan or loan['return_date']:
            return False
            
        # Update loan record
        self._update_loan_return(loan_id)
        
        # Update book status
        self._update_book_status(loan['book_id'], 'available')
        return True

    def search_books(self, query: str, category: str = None) -> List[Dict]:
        """Search books by title, author, or category"""
        results = []
        with open(self.books_db, 'r') as file:
            reader = csv.DictReader(file)
            for book in reader:
                if (query.lower() in book['title'].lower() or 
                    query.lower() in book['author'].lower()):
                    if category is None or book['category'].lower() == category.lower():
                        results.append(book)
        return results

    def _get_book(self, book_id: str) -> Optional[Dict]:
        """Helper method to get book details"""
        with open(self.books_db, 'r') as file:
            reader = csv.DictReader(file)
            for book in reader:
                if book['book_id'] == book_id:
                    return book
        return None

    def _get_loan(self, loan_id: str) -> Optional[Dict]:
        """Helper method to get loan details"""
        with open(self.loans_db, 'r') as file:
            reader = csv.DictReader(file)
            for loan in reader:
                if loan['loan_id'] == loan_id:
                    return loan
        return None

    def _update_book_status(self, book_id: str, new_status: str):
        """Helper method to update book status"""
        books = []
        with open(self.books_db, 'r') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            for book in reader:
                if book['book_id'] == book_id:
                    book['status'] = new_status
                books.append(book)
        
        with open(self.books_db, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(books)

    def _update_loan_return(self, loan_id: str):
        """Helper method to update loan return date"""
        loans = []
        with open(self.loans_db, 'r') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            for loan in reader:
                if loan['loan_id'] == loan_id:
                    loan['return_date'] = datetime.now().isoformat()
                loans.append(loan)
        
        with open(self.loans_db, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(loans)

# Example usage:
def main():
    library = LibraryManagementSystem()
    
    while True:
        print("\n=== Library Management System ===")
        print("1. Register New User")
        print("2. Add New Book")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. Search Books")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == '1':
            name = input("Enter name: ")
            email = input("Enter email: ")
            phone = input("Enter phone: ")
            user_id = library.register_user(name, email, phone)
            print(f"User registered successfully! User ID: {user_id}")
            
        elif choice == '2':
            title = input("Enter book title: ")
            author = input("Enter author name: ")
            category = input("Enter book category: ")
            book_id = library.add_book(title, author, category)
            print(f"Book added successfully! Book ID: {book_id}")
            
        elif choice == '3':
            book_id = input("Enter book ID: ")
            user_id = input("Enter user ID: ")
            loan_id = library.borrow_book(book_id, user_id)
            if loan_id:
                print(f"Book borrowed successfully! Loan ID: {loan_id}")
            else:
                print("Book is not available for borrowing.")
                
        elif choice == '4':
            loan_id = input("Enter loan ID: ")
            if library.return_book(loan_id):
                print("Book returned successfully!")
            else:
                print("Invalid loan ID or book already returned.")
                
        elif choice == '5':
            query = input("Enter search term: ")
            category = input("Enter category (optional, press Enter to skip): ") or None
            results = library.search_books(query, category)
            if results:
                print("\nSearch Results:")
                for book in results:
                    print(f"Title: {book['title']}")
                    print(f"Author: {book['author']}")
                    print(f"Category: {book['category']}")
                    print(f"Status: {book['status']}")
                    print("---")
            else:
                print("No books found matching your search.")
                
        elif choice == '6':
            print("Thank you for using the Library Management System!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
