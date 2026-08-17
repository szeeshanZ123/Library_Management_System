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
        self.book_id = book_id
        self.title = title
        self.author = author
        self.category = category
        self.isbn = isbn
        self.quantity = quantity
        self.available_status = available_status

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
        return cls(
            data["book_id"],
            data["title"],
            data["author"],
            data["category"],
            data["isbn"],
            data["quantity"],
            data["available_status"]
        )


class Student:
    def __init__(self, student_id, name, password):
        self.student_id = student_id
        self.name = name
        self.password = password

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


# ==========================
# DATABASE MANAGER
# ==========================

class DatabaseManager:

    def __init__(self):
        self.books = []
        self.students = []
        self.load_data()

    def load_data(self):

        if os.path.exists(BOOKS_FILE):
            with open(BOOKS_FILE, "r") as f:
                self.books = [Book.from_dict(x) for x in json.load(f)]

        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "r") as f:
                raw_students = json.load(f)
                self.students = [
                    Student.from_dict(x)
                    for x in raw_students
                    if x.get("student_id", "").strip() and x.get("name", "").strip()
                ]

        if not self.books:
            print("No books loaded from data file.")

        if not self.students:
            print("No students loaded from data file.")

    def save_books(self):
        with open(BOOKS_FILE, "w") as f:
            json.dump([b.to_dict() for b in self.books], f, indent=4)

    def save_students(self):
        with open(STUDENTS_FILE, "w") as f:
            json.dump([s.to_dict() for s in self.students], f, indent=4)

    def get_book(self, book_id):
        for book in self.books:
            if book.book_id.lower() == book_id.lower():
                return book
        return None

    def get_student(self, student_id):
        for student in self.students:
            if student.student_id.lower() == student_id.lower():
                return student
        return None
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

        if self.db.get_book(book_id):
            print("Book ID already exists.")
            return

        title = input("Title : ").strip()
        author = input("Author : ").strip()
        category = input("Category : ").strip()
        isbn = input("ISBN : ").strip()

        while True:
            try:
                quantity = int(input("Quantity : "))
                if quantity < 0:
                    raise ValueError
                break
            except ValueError:
                print("Enter a valid quantity.")

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

    # ----------------------

    def view_books(self):

        print("\n=========== BOOK LIST ===========")

        if len(self.db.books) == 0:
            print("No books available.")
            return

        print("-" * 90)

        print(
            f"{'ID':<10}"
            f"{'TITLE':<30}"
            f"{'AUTHOR':<20}"
            f"{'QTY':<8}"
            f"{'STATUS'}"
        )

        print("-" * 90)

        for book in self.db.books:

            status = "Available" if book.quantity > 0 else "Unavailable"

            print(
                f"{book.book_id:<10}"
                f"{book.title:<30}"
                f"{book.author:<20}"
                f"{book.quantity:<8}"
                f"{status}"
            )

        print("-" * 90)

    # ----------------------

    def search_book(self):

        keyword = input("\nEnter Book ID / Title / Author : ").lower()

        found = False

        print("\n========== SEARCH RESULT ==========")

        for book in self.db.books:

            if (
                keyword in book.book_id.lower()
                or keyword in book.title.lower()
                or keyword in book.author.lower()
            ):

                found = True

                print("-----------------------------")
                print("Book ID :", book.book_id)
                print("Title   :", book.title)
                print("Author  :", book.author)
                print("Category:", book.category)
                print("ISBN    :", book.isbn)
                print("Quantity:", book.quantity)

        if not found:
            print("No matching books found.")

    # ----------------------
    # STUDENT OPERATIONS
    # ----------------------

    def register_student(self):

        print("\n===== STUDENT REGISTRATION =====")

        student_id = input("Student ID : ").strip()

        if self.db.get_student(student_id):
            print("Student ID already exists.")
            return

        name = input("Student Name : ").strip()

        password = input("Password : ").strip()

        student = Student(
            student_id,
            name,
            password
        )

        self.db.students.append(student)

        self.db.save_students()

        print("\nStudent registered successfully.")

    # ----------------------

    def view_students(self):

        print("\n========== STUDENTS ==========")

        if len(self.db.students) == 0:
            print("No students registered.")
            return

        print("-" * 50)

        print(f"{'ID':<15}{'NAME'}")

        print("-" * 50)

        for student in self.db.students:

            print(
                f"{student.student_id:<15}"
                f"{student.name}"
            )

        print("-" * 50)

# ==========================
# USER INTERFACE (CLI)
# ==========================


class LibraryCLI:

    def __init__(self):
        self.db = DatabaseManager()
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
            print("2. View Books")
            print("3. Search Book")
            print("4. Register Student")
            print("5. View Students")
            print("6. Logout")

            choice = input("\nEnter Choice : ")

            if choice == "1":
                self.service.add_book()

            elif choice == "2":
                self.service.view_books()

            elif choice == "3":
                self.service.search_book()

            elif choice == "4":
                self.service.register_student()

            elif choice == "5":
                self.service.view_students()

            elif choice == "6":
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
            print("3. Logout")

            choice = input("\nEnter Choice : ")

            if choice == "1":
                self.service.view_books()

            elif choice == "2":
                self.service.search_book()

            elif choice == "3":
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

