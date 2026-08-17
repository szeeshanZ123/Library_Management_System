import json
import os
import datetime
import sys

# ==========================
# FILE PATHS
# ==========================

APP_DIR = os.path.dirname(os.path.abspath(__file__))


def find_data_file(filename):
    candidates = []
    candidates.append(os.path.join(APP_DIR, filename))
    candidates.append(os.path.join(os.path.dirname(APP_DIR), filename))
    candidates.append(os.path.join(os.getcwd(), filename))

    for path in candidates:
        if os.path.exists(path):
            return path

    return os.path.join(APP_DIR, filename)


BOOKS_FILE = find_data_file("books.json")
STUDENTS_FILE = find_data_file("students.json")
TRANSACTIONS_FILE = find_data_file("transactions.json")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ==========================
# DATA MODELS
# ==========================

class Book:
    def __init__(self, book_id, title, author, category, isbn, quantity, available_status=True):
        self.book_id = str(book_id).strip()
        self.title = str(title).strip()
        self.author = str(author).strip()
        self.category = str(category).strip()
        self.isbn = str(isbn).strip()
        self.quantity = int(quantity)
        self.available_status = bool(available_status) if self.quantity > 0 else False

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "isbn": self.isbn,
            "quantity": self.quantity,
            "available_status": self.available_status
        }

    @classmethod
    def from_dict(cls, data):
        quantity = int(data.get("quantity", 0))
        avail = data.get("available_status", quantity > 0)
        return cls(
            data["book_id"],
            data["title"],
            data["author"],
            data["category"],
            data["isbn"],
            quantity,
            avail
        )


class Student:
    def __init__(self, student_id, name, password):
        self.student_id = str(student_id).strip()
        self.name = str(name).strip()
        self.password = str(password).strip()

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "password": self.password
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["student_id"],
            data["name"],
            data["password"]
        )


class Transaction:
    def __init__(self, transaction_id, student_id, book_id, borrow_date, return_date=None, status="Borrowed"):
        self.transaction_id = int(transaction_id)
        self.student_id = str(student_id).strip()
        self.book_id = str(book_id).strip()
        self.borrow_date = str(borrow_date).strip()
        self.return_date = str(return_date).strip() if return_date else None
        self.status = str(status).strip()  # "Borrowed" or "Returned"

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "student_id": self.student_id,
            "book_id": self.book_id,
            "borrow_date": self.borrow_date,
            "return_date": self.return_date,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["transaction_id"],
            data["student_id"],
            data["book_id"],
            data["borrow_date"],
            data.get("return_date"),
            data.get("status", "Borrowed")
        )


# ==========================
# DATABASE MANAGER
# ==========================

class DatabaseManager:

    def __init__(self, books_file=None, students_file=None, transactions_file=None):
        self.books_file = books_file or BOOKS_FILE
        self.students_file = students_file or STUDENTS_FILE
        self.transactions_file = transactions_file or TRANSACTIONS_FILE
        self.books = []
        self.students = []
        self.transactions = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.books_file):
            try:
                with open(self.books_file, "r") as f:
                    raw_books = json.load(f)
                    self.books = [Book.from_dict(x) for x in raw_books]
            except Exception:
                self.books = []

        if os.path.exists(self.students_file):
            try:
                with open(self.students_file, "r") as f:
                    raw_students = json.load(f)
                    self.students = [
                        Student.from_dict(x)
                        for x in raw_students
                        if str(x.get("student_id", "")).strip() and str(x.get("name", "")).strip()
                    ]
            except Exception:
                self.students = []

        if os.path.exists(self.transactions_file):
            try:
                with open(self.transactions_file, "r") as f:
                    raw_transactions = json.load(f)
                    self.transactions = [Transaction.from_dict(x) for x in raw_transactions]
            except Exception:
                self.transactions = []

        if not self.books:
            print("No books loaded from data file.")

        if not self.students:
            print("No students loaded from data file.")

    def save_books(self):
        with open(self.books_file, "w") as f:
            json.dump([b.to_dict() for b in self.books], f, indent=4)

    def save_students(self):
        with open(self.students_file, "w") as f:
            json.dump([s.to_dict() for s in self.students], f, indent=4)

    def save_transactions(self):
        with open(self.transactions_file, "w") as f:
            json.dump([t.to_dict() for t in self.transactions], f, indent=4)

    def get_book(self, book_id):
        if not book_id:
            return None
        book_id_str = str(book_id).strip().lower()
        for book in self.books:
            if book.book_id.lower() == book_id_str:
                return book
        return None

    def get_student(self, student_id):
        if not student_id:
            return None
        student_id_str = str(student_id).strip().lower()
        for student in self.students:
            if student.student_id.lower() == student_id_str:
                return student
        return None

    def get_next_transaction_id(self):
        if not self.transactions:
            return 1
        return max(t.transaction_id for t in self.transactions) + 1

    def get_active_transaction(self, student_id, book_id):
        if not student_id or not book_id:
            return None
        s_id = str(student_id).strip().lower()
        b_id = str(book_id).strip().lower()
        for t in self.transactions:
            if t.student_id.lower() == s_id and t.book_id.lower() == b_id and t.status == "Borrowed":
                return t
        return None

    def get_student_transactions(self, student_id):
        if not student_id:
            return []
        s_id = str(student_id).strip().lower()
        return [t for t in self.transactions if t.student_id.lower() == s_id]

    def get_student_active_transactions(self, student_id):
        if not student_id:
            return []
        s_id = str(student_id).strip().lower()
        return [t for t in self.transactions if t.student_id.lower() == s_id and t.status == "Borrowed"]

    def has_active_borrowing_for_book(self, book_id):
        if not book_id:
            return False
        b_id = str(book_id).strip().lower()
        for t in self.transactions:
            if t.book_id.lower() == b_id and t.status == "Borrowed":
                return True
        return False

    def get_active_borrowed_count_for_book(self, book_id):
        if not book_id:
            return 0
        b_id = str(book_id).strip().lower()
        count = 0
        for t in self.transactions:
            if t.book_id.lower() == b_id and t.status == "Borrowed":
                count += 1
        return count

    def has_active_borrowing_for_student(self, student_id):
        if not student_id:
            return False
        s_id = str(student_id).strip().lower()
        for t in self.transactions:
            if t.student_id.lower() == s_id and t.status == "Borrowed":
                return True
        return False

    def delete_book(self, book_id):
        book = self.get_book(book_id)
        if book:
            self.books.remove(book)
            self.save_books()
            return True
        return False

    def delete_student(self, student_id):
        student = self.get_student(student_id)
        if student:
            self.students.remove(student)
            self.save_students()
            return True
        return False


# ==========================
# LIBRARY SERVICE
# ==========================

class LibraryService:

    def __init__(self, db):
        self.db = db

    # ----------------------
    # BOOK OPERATIONS
    # ----------------------

    def add_book(self):
        print("\n===== ADD BOOK =====")

        book_id = input("Book ID : ").strip()
        if not book_id:
            print("Book ID cannot be empty.")
            return

        if self.db.get_book(book_id):
            print("Book ID already exists.")
            return

        title = input("Title : ").strip()
        if not title:
            print("Title cannot be empty.")
            return

        author = input("Author : ").strip()
        if not author:
            print("Author cannot be empty.")
            return

        category = input("Category : ").strip()
        isbn = input("ISBN : ").strip()

        while True:
            try:
                quantity = int(input("Quantity : "))
                if quantity < 0:
                    raise ValueError
                break
            except ValueError:
                print("Enter a valid non-negative quantity.")

        new_book = Book(
            book_id,
            title,
            author,
            category,
            isbn,
            quantity,
            quantity > 0
        )

        self.db.books.append(new_book)
        self.db.save_books()

        print("\nBook added successfully.")

    def update_book(self):
        print("\n===== UPDATE BOOK =====")

        book_id = input("Enter Book ID to update : ").strip()
        book = self.db.get_book(book_id)

        if not book:
            print("Book not found.")
            return

        print("\n--- Current Details ---")
        print(f"Title    : {book.title}")
        print(f"Author   : {book.author}")
        print(f"Category : {book.category}")
        print(f"ISBN     : {book.isbn}")
        print(f"Quantity : {book.quantity}")

        active_borrowed = self.db.get_active_borrowed_count_for_book(book.book_id)
        if active_borrowed > 0:
            print(f"(Note: {active_borrowed} copies are currently borrowed)")

        print("\n(Press Enter to keep current value)")

        new_title = input(f"New Title [{book.title}]: ").strip()
        new_author = input(f"New Author [{book.author}]: ").strip()
        new_category = input(f"New Category [{book.category}]: ").strip()
        new_isbn = input(f"New ISBN [{book.isbn}]: ").strip()
        new_qty_str = input(f"New Quantity [{book.quantity}]: ").strip()

        if new_title:
            book.title = new_title
        if new_author:
            book.author = new_author
        if new_category:
            book.category = new_category
        if new_isbn:
            book.isbn = new_isbn

        if new_qty_str:
            try:
                new_quantity = int(new_qty_str)
                if new_quantity < 0:
                    print("Quantity cannot be negative. Quantity not updated.")
                elif new_quantity < active_borrowed:
                    print(f"Error: Total copies cannot be less than currently borrowed copies ({active_borrowed}). Quantity not updated.")
                else:
                    book.quantity = new_quantity
            except ValueError:
                print("Invalid quantity entered. Quantity not updated.")

        book.available_status = book.quantity > 0

        self.db.save_books()
        print("\nBook updated successfully.")

    def delete_book(self):
        print("\n===== DELETE BOOK =====")

        book_id = input("Enter Book ID to delete : ").strip()
        book = self.db.get_book(book_id)

        if not book:
            print("Book not found.")
            return

        if self.db.has_active_borrowing_for_book(book.book_id):
            print("\nError: Cannot delete book. This book currently has active borrowing record(s).")
            return

        confirm = input(f"Are you sure you want to delete '{book.title}' (ID: {book.book_id})? (y/n): ").strip().lower()
        if confirm in ["y", "yes"]:
            self.db.delete_book(book.book_id)
            print("\nBook deleted successfully.")
        else:
            print("\nDeletion cancelled.")

    # ----------------------

    def view_books(self):
        print("\n=========== BOOK LIST ===========")

        if len(self.db.books) == 0:
            print("No books available.")
            return

        print("-" * 95)
        print(
            f"{'ID':<10}"
            f"{'TITLE':<30}"
            f"{'AUTHOR':<22}"
            f"{'QTY':<8}"
            f"{'STATUS'}"
        )
        print("-" * 95)

        for book in self.db.books:
            status = "Available" if book.quantity > 0 else "Unavailable"
            print(
                f"{book.book_id:<10}"
                f"{book.title[:28]:<30}"
                f"{book.author[:20]:<22}"
                f"{book.quantity:<8}"
                f"{status}"
            )

        print("-" * 95)

    # ----------------------

    def search_book(self):
        keyword = input("\nEnter Book ID / Title / Author : ").strip().lower()

        if not keyword:
            print("Please enter a valid search term.")
            return

        found = False
        print("\n========== SEARCH RESULT ==========")

        for book in self.db.books:
            if (
                keyword in book.book_id.lower()
                or keyword in book.title.lower()
                or keyword in book.author.lower()
            ):
                found = True
                status = "Available" if book.quantity > 0 else "Unavailable"
                print("-----------------------------")
                print("Book ID :", book.book_id)
                print("Title   :", book.title)
                print("Author  :", book.author)
                print("Category:", book.category)
                print("ISBN    :", book.isbn)
                print("Quantity:", book.quantity)
                print("Status  :", status)

        if not found:
            print("No matching books found.")

    # ----------------------
    # STUDENT OPERATIONS
    # ----------------------

    def register_student(self):
        print("\n===== STUDENT REGISTRATION =====")

        student_id = input("Student ID : ").strip()
        if not student_id:
            print("Student ID cannot be empty.")
            return

        if self.db.get_student(student_id):
            print("Student ID already exists.")
            return

        name = input("Student Name : ").strip()
        if not name:
            print("Name cannot be empty.")
            return

        password = input("Password : ").strip()
        if not password:
            print("Password cannot be empty.")
            return

        student = Student(
            student_id,
            name,
            password
        )

        self.db.students.append(student)
        self.db.save_students()

        print("\nStudent registered successfully.")

    def view_students(self):
        print("\n========== STUDENTS ==========")

        if len(self.db.students) == 0:
            print("No students registered.")
            return

        print("-" * 50)
        print(f"{'ID':<15}{'NAME'}")
        print("-" * 50)

        for student in self.db.students:
            print(f"{student.student_id:<15}{student.name}")

        print("-" * 50)

    def delete_student(self):
        print("\n===== DELETE STUDENT =====")

        student_id = input("Enter Student ID to delete : ").strip()
        student = self.db.get_student(student_id)

        if not student:
            print("Student not found.")
            return

        if self.db.has_active_borrowing_for_student(student.student_id):
            print("\nError: Cannot delete student. This student currently has active borrowed book(s) that must be returned first.")
            return

        confirm = input(f"Are you sure you want to delete student '{student.name}' (ID: {student.student_id})? (y/n): ").strip().lower()
        if confirm in ["y", "yes"]:
            self.db.delete_student(student.student_id)
            print("\nStudent deleted successfully.")
        else:
            print("\nDeletion cancelled.")

    # ----------------------
    # BORROW & RETURN OPERATIONS
    # ----------------------

    def borrow_book(self, student):
        print("\n===== BORROW BOOK =====")

        book_id = input("Enter Book ID to borrow : ").strip()
        if not book_id:
            print("Book ID cannot be empty.")
            return

        book = self.db.get_book(book_id)
        if not book:
            print("Book not found.")
            return

        if book.quantity <= 0:
            print("Cannot borrow: No copies of this book are currently available.")
            return

        active_tx = self.db.get_active_transaction(student.student_id, book.book_id)
        if active_tx:
            print("Cannot borrow: You already have an active borrowing record for this book. Please return it first.")
            return

        book.quantity -= 1
        book.available_status = book.quantity > 0

        transaction_id = self.db.get_next_transaction_id()
        today = datetime.date.today().strftime("%Y-%m-%d")

        new_transaction = Transaction(
            transaction_id=transaction_id,
            student_id=student.student_id,
            book_id=book.book_id,
            borrow_date=today,
            return_date=None,
            status="Borrowed"
        )

        self.db.transactions.append(new_transaction)
        self.db.save_books()
        self.db.save_transactions()

        print(f"\nSuccess: You have successfully borrowed '{book.title}'.")
        print(f"Transaction ID: {transaction_id} | Borrow Date: {today}")

    def return_book(self, student):
        print("\n===== RETURN BOOK =====")

        active_txs = self.db.get_student_active_transactions(student.student_id)
        if not active_txs:
            print("You do not have any currently borrowed books to return.")
            return

        print("\n--- Currently Borrowed Books ---")
        print("-" * 75)
        print(f"{'TX ID':<8}{'BOOK ID':<12}{'TITLE':<30}{'BORROW DATE':<15}")
        print("-" * 75)
        for tx in active_txs:
            b = self.db.get_book(tx.book_id)
            title = b.title if b else "Unknown"
            print(f"{tx.transaction_id:<8}{tx.book_id:<12}{title[:28]:<30}{tx.borrow_date:<15}")
        print("-" * 75)

        book_id = input("\nEnter Book ID to return : ").strip()
        if not book_id:
            print("Book ID cannot be empty.")
            return

        active_tx = self.db.get_active_transaction(student.student_id, book_id)
        if not active_tx:
            print("Error: You do not have an active borrowing record for this Book ID.")
            return

        today = datetime.date.today().strftime("%Y-%m-%d")
        active_tx.status = "Returned"
        active_tx.return_date = today

        book = self.db.get_book(active_tx.book_id)
        if book:
            book.quantity += 1
            book.available_status = True
            self.db.save_books()

        self.db.save_transactions()

        book_title = book.title if book else active_tx.book_id
        print(f"\nSuccess: Book '{book_title}' has been returned successfully on {today}.")

    def view_student_borrowed_books(self, student):
        print(f"\n=========== MY BORROWED BOOKS ({student.name}) ===========")

        student_txs = self.db.get_student_transactions(student.student_id)
        if not student_txs:
            print("No borrowing history found.")
            return

        print("-" * 95)
        print(
            f"{'TX ID':<8}"
            f"{'BOOK ID':<10}"
            f"{'TITLE':<28}"
            f"{'BORROW DATE':<14}"
            f"{'RETURN DATE':<14}"
            f"{'STATUS'}"
        )
        print("-" * 95)

        for tx in student_txs:
            book = self.db.get_book(tx.book_id)
            title = book.title if book else "Unknown / Deleted"
            ret_date = tx.return_date if tx.return_date else "-"
            print(
                f"{tx.transaction_id:<8}"
                f"{tx.book_id:<10}"
                f"{title[:26]:<28}"
                f"{tx.borrow_date:<14}"
                f"{ret_date:<14}"
                f"{tx.status}"
            )

        print("-" * 95)

    def change_student_password(self, student):
        print("\n===== CHANGE PASSWORD =====")

        current_pw = input("Current Password : ").strip()
        if current_pw != student.password:
            print("\nError: Incorrect current password.")
            return

        new_pw = input("New Password : ").strip()
        if not new_pw:
            print("\nError: Password cannot be empty.")
            return

        confirm_pw = input("Confirm New Password : ").strip()
        if new_pw != confirm_pw:
            print("\nError: New password and confirm password do not match.")
            return

        student.password = new_pw
        self.db.save_students()

        print("\nSuccess: Password changed successfully.")

    def view_all_transactions(self):
        print("\n========================= ALL TRANSACTIONS =========================")

        if not self.db.transactions:
            print("No transactions recorded.")
            return

        print("-" * 105)
        print(
            f"{'TX ID':<8}"
            f"{'STUDENT':<16}"
            f"{'BOOK ID':<10}"
            f"{'TITLE':<25}"
            f"{'BORROW DATE':<14}"
            f"{'RETURN DATE':<14}"
            f"{'STATUS'}"
        )
        print("-" * 105)

        for tx in self.db.transactions:
            stu = self.db.get_student(tx.student_id)
            stu_info = f"{tx.student_id}" + (f" ({stu.name[:8]})" if stu else "")
            book = self.db.get_book(tx.book_id)
            book_title = book.title if book else "Unknown"
            ret_date = tx.return_date if tx.return_date else "-"

            print(
                f"{tx.transaction_id:<8}"
                f"{stu_info[:14]:<16}"
                f"{tx.book_id:<10}"
                f"{book_title[:23]:<25}"
                f"{tx.borrow_date:<14}"
                f"{ret_date:<14}"
                f"{tx.status}"
            )

        print("-" * 105)


# ==========================
# USER INTERFACE (CLI)
# ==========================

class LibraryCLI:

    def __init__(self, db=None):
        self.db = db or DatabaseManager()
        self.service = LibraryService(self.db)

    # -------------------------
    # ADMIN LOGIN
    # -------------------------

    def admin_login(self):
        print("\n========== ADMIN LOGIN ==========")

        username = input("Username : ").strip()
        password = input("Password : ").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            print("\nLogin Successful!")
            self.admin_menu()
        else:
            print("\nInvalid Username or Password.")

    # -------------------------
    # STUDENT LOGIN
    # -------------------------

    def student_login(self):
        print("\n========== STUDENT LOGIN ==========")

        sid = input("Student ID : ").strip()
        password = input("Password : ").strip()

        student = self.db.get_student(sid)

        if student is None:
            print("\nStudent not found.")
            return

        if student.password != password:
            print("\nIncorrect Password.")
            return

        print(f"\nWelcome {student.name}")
        self.student_menu(student)

    # -------------------------
    # ADMIN MENU
    # -------------------------

    def admin_menu(self):
        while True:
            print("\n===================================")
            print("         ADMIN PANEL")
            print("===================================")
            print("1. Add Book")
            print("2. Update Book")
            print("3. Delete Book")
            print("4. View Books")
            print("5. Search Book")
            print("6. Register Student")
            print("7. View Students")
            print("8. Delete Student")
            print("9. View Transactions")
            print("10. Logout")

            choice = input("\nEnter Choice : ").strip()

            if choice == "1":
                self.service.add_book()
            elif choice == "2":
                self.service.update_book()
            elif choice == "3":
                self.service.delete_book()
            elif choice == "4":
                self.service.view_books()
            elif choice == "5":
                self.service.search_book()
            elif choice == "6":
                self.service.register_student()
            elif choice == "7":
                self.service.view_students()
            elif choice == "8":
                self.service.delete_student()
            elif choice == "9":
                self.service.view_all_transactions()
            elif choice == "10":
                print("\nLogging Out...")
                break
            else:
                print("\nInvalid Choice.")

    # -------------------------
    # STUDENT MENU
    # -------------------------

    def student_menu(self, student):
        while True:
            print("\n===================================")
            print(f"      STUDENT PANEL ({student.name})")
            print("===================================")
            print("1. View Books")
            print("2. Search Book")
            print("3. Borrow Book")
            print("4. Return Book")
            print("5. My Borrowed Books")
            print("6. Change Password")
            print("7. Logout")

            choice = input("\nEnter Choice : ").strip()

            if choice == "1":
                self.service.view_books()
            elif choice == "2":
                self.service.search_book()
            elif choice == "3":
                self.service.borrow_book(student)
            elif choice == "4":
                self.service.return_book(student)
            elif choice == "5":
                self.service.view_student_borrowed_books(student)
            elif choice == "6":
                self.service.change_student_password(student)
            elif choice == "7":
                print("\nLogging Out...")
                break
            else:
                print("\nInvalid Choice.")

    # -------------------------
    # MAIN MENU
    # -------------------------

    def run(self):
        while True:
            print("\n===================================")
            print(" SMART LIBRARY MANAGEMENT SYSTEM ")
            print("===================================")
            print("1. Admin Login")
            print("2. Student Registration")
            print("3. Student Login")
            print("4. Exit")

            choice = input("\nEnter Choice : ").strip()

            if choice == "1":
                self.admin_login()
            elif choice == "2":
                self.service.register_student()
            elif choice == "3":
                self.student_login()
            elif choice == "4":
                print("\nThank you for using Library Management System.")
                break
            else:
                print("\nInvalid Choice.")


# ==========================
# UTILITY METHODS
# ==========================

def print_banner():
    print("=" * 50)
    print("      SMART LIBRARY MANAGEMENT SYSTEM")
    print("=" * 50)


def pause():
    input("\nPress Enter to continue...")


# ==========================
# APPLICATION ENTRY POINT
# ==========================

def main():
    print_banner()
    app = LibraryCLI()

    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
    except Exception as e:
        print("\nUnexpected Error:", e)
    finally:
        print("\nThank you for using the system.")


if __name__ == "__main__":
    main()
