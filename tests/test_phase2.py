import unittest
import os
import sys
import tempfile
import json
import io
from pathlib import Path
from unittest.mock import patch

# Add the project directory to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent / "Library_Management_System_v1.0"
sys.path.insert(0, str(PROJECT_DIR))

import main


class TestPhase2LibrarySystem(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.books_file = os.path.join(self.temp_dir.name, "books.json")
        self.students_file = os.path.join(self.temp_dir.name, "students.json")
        self.transactions_file = os.path.join(self.temp_dir.name, "transactions.json")

        # Seed initial books
        initial_books = [
            {
                "book_id": "B101",
                "title": "Clean Code",
                "author": "Robert C. Martin",
                "category": "Software Engineering",
                "isbn": "9780132350884",
                "quantity": 2,
                "available_status": True
            },
            {
                "book_id": "B102",
                "title": "Python Crash Course",
                "author": "Eric Matthes",
                "category": "Programming",
                "isbn": "9781593279288",
                "quantity": 1,
                "available_status": True
            },
            {
                "book_id": "B103",
                "title": "Zero Stock Book",
                "author": "Test Author",
                "category": "Testing",
                "isbn": "1112223334",
                "quantity": 0,
                "available_status": False
            }
        ]
        with open(self.books_file, "w") as f:
            json.dump(initial_books, f)

        # Seed initial students
        initial_students = [
            {
                "student_id": "S101",
                "name": "Alice Smith",
                "password": "pass123"
            },
            {
                "student_id": "S102",
                "name": "Bob Jones",
                "password": "secretbob"
            }
        ]
        with open(self.students_file, "w") as f:
            json.dump(initial_students, f)

        # Empty initial transactions
        with open(self.transactions_file, "w") as f:
            json.dump([], f)

        self.db = main.DatabaseManager(
            books_file=self.books_file,
            students_file=self.students_file,
            transactions_file=self.transactions_file
        )
        self.service = main.LibraryService(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    # 1. Student login validation
    def test_01_student_login(self):
        student = self.db.get_student("S101")
        self.assertIsNotNone(student)
        self.assertEqual(student.password, "pass123")
        self.assertIsNone(self.db.get_student("NON_EXISTENT"))

    # 2. Student view books
    def test_02_view_books(self):
        with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
            self.service.view_books()
            output = mock_out.getvalue()
            self.assertIn("Clean Code", output)
            self.assertIn("Python Crash Course", output)

    # 3. Student successfully borrows an available book
    # 4. Available copies decrease
    def test_03_04_borrow_book_success_and_quantity_decrease(self):
        student = self.db.get_student("S101")
        initial_qty = self.db.get_book("B101").quantity
        self.assertEqual(initial_qty, 2)

        with patch('builtins.input', side_effect=["B101"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.borrow_book(student)
                output = mock_out.getvalue()
                self.assertIn("successfully borrowed", output)

        book = self.db.get_book("B101")
        self.assertEqual(book.quantity, 1)
        self.assertTrue(book.available_status)
        self.assertEqual(len(self.db.transactions), 1)
        self.assertEqual(self.db.transactions[0].status, "Borrowed")
        self.assertEqual(self.db.transactions[0].student_id, "S101")
        self.assertEqual(self.db.transactions[0].book_id, "B101")
        self.assertIsNone(self.db.transactions[0].return_date)

    # 5. Student sees the book in "My Borrowed Books"
    def test_05_my_borrowed_books_view(self):
        student = self.db.get_student("S101")
        with patch('builtins.input', side_effect=["B101"]):
            self.service.borrow_book(student)

        with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
            self.service.view_student_borrowed_books(student)
            output = mock_out.getvalue()
            self.assertIn("Clean Code", output)
            self.assertIn("Borrowed", output)

    # 6. Student cannot borrow the same active book twice & cannot borrow zero stock book
    def test_06_prevent_duplicate_and_out_of_stock_borrowing(self):
        student = self.db.get_student("S101")

        # First borrow B101
        with patch('builtins.input', side_effect=["B101"]):
            self.service.borrow_book(student)

        # Attempt to borrow B101 again
        with patch('builtins.input', side_effect=["B101"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.borrow_book(student)
                output = mock_out.getvalue()
                self.assertIn("already have an active borrowing record", output)

        # Attempt to borrow out of stock book B103
        with patch('builtins.input', side_effect=["B103"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.borrow_book(student)
                output = mock_out.getvalue()
                self.assertIn("No copies of this book are currently available", output)

    # 7. Student returns the book
    # 8. Available copies increase
    # 9. Transaction changes to Returned
    def test_07_08_09_return_book(self):
        student = self.db.get_student("S101")
        with patch('builtins.input', side_effect=["B102"]):
            self.service.borrow_book(student)

        book_after_borrow = self.db.get_book("B102")
        self.assertEqual(book_after_borrow.quantity, 0)
        self.assertFalse(book_after_borrow.available_status)

        # Return book
        with patch('builtins.input', side_effect=["B102"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.return_book(student)
                output = mock_out.getvalue()
                self.assertIn("returned successfully", output)

        book_after_return = self.db.get_book("B102")
        self.assertEqual(book_after_return.quantity, 1)
        self.assertTrue(book_after_return.available_status)

        tx = self.db.transactions[0]
        self.assertEqual(tx.status, "Returned")
        self.assertIsNotNone(tx.return_date)

    # 10. Admin updates a book
    def test_10_admin_update_book(self):
        # Update title and quantity
        with patch('builtins.input', side_effect=["B101", "Clean Code 2nd Ed", "", "", "", "10"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.update_book()
                output = mock_out.getvalue()
                self.assertIn("Book updated successfully", output)

        book = self.db.get_book("B101")
        self.assertEqual(book.title, "Clean Code 2nd Ed")
        self.assertEqual(book.quantity, 10)

        # Check that admin cannot reduce total copies below active borrowed count
        student = self.db.get_student("S101")
        with patch('builtins.input', side_effect=["B101"]):
            self.service.borrow_book(student)

        # 1 copy is active borrowed now. Attempt to set quantity to 0 when active is 1
        with patch('builtins.input', side_effect=["B101", "", "", "", "", "0"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.update_book()
                output = mock_out.getvalue()
                self.assertIn("Total copies cannot be less than currently borrowed copies", output)

    # 11. Admin deletes an unborrowed book
    def test_11_admin_delete_unborrowed_book(self):
        with patch('builtins.input', side_effect=["B103", "y"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.delete_book()
                output = mock_out.getvalue()
                self.assertIn("Book deleted successfully", output)

        self.assertIsNone(self.db.get_book("B103"))

    # 12. Admin cannot delete a borrowed book
    def test_12_admin_cannot_delete_borrowed_book(self):
        student = self.db.get_student("S101")
        with patch('builtins.input', side_effect=["B101"]):
            self.service.borrow_book(student)

        with patch('builtins.input', side_effect=["B101"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.delete_book()
                output = mock_out.getvalue()
                self.assertIn("Cannot delete book", output)

        self.assertIsNotNone(self.db.get_book("B101"))

    # 13. Admin deletes a student without active borrowings
    def test_13_admin_delete_student(self):
        with patch('builtins.input', side_effect=["S102", "y"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.delete_student()
                output = mock_out.getvalue()
                self.assertIn("Student deleted successfully", output)

        self.assertIsNone(self.db.get_student("S102"))

    # 14. Admin cannot delete a student with active borrowing
    def test_14_admin_cannot_delete_student_with_active_borrowing(self):
        student = self.db.get_student("S101")
        with patch('builtins.input', side_effect=["B101"]):
            self.service.borrow_book(student)

        with patch('builtins.input', side_effect=["S101"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.delete_student()
                output = mock_out.getvalue()
                self.assertIn("Cannot delete student", output)

        self.assertIsNotNone(self.db.get_student("S101"))

    # 15. Student changes password successfully
    # 16. Incorrect current password rejected
    # 17. Mismatched new passwords rejected
    def test_15_16_17_change_password(self):
        student = self.db.get_student("S101")

        # Wrong current password
        with patch('builtins.input', side_effect=["wrongpass"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.change_student_password(student)
                output = mock_out.getvalue()
                self.assertIn("Incorrect current password", output)

        # Mismatched new passwords
        with patch('builtins.input', side_effect=["pass123", "newpass456", "differentpass"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.change_student_password(student)
                output = mock_out.getvalue()
                self.assertIn("do not match", output)

        # Successful change
        with patch('builtins.input', side_effect=["pass123", "brandnew123", "brandnew123"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.change_student_password(student)
                output = mock_out.getvalue()
                self.assertIn("Password changed successfully", output)

        self.assertEqual(student.password, "brandnew123")

    # 18. Student vs Admin isolation & 19. Private borrowing data isolation
    def test_18_19_data_isolation(self):
        s1 = self.db.get_student("S101")
        s2 = self.db.get_student("S102")

        with patch('builtins.input', side_effect=["B101"]):
            self.service.borrow_book(s1)

        # s2 views their borrowed books - should see nothing
        with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
            self.service.view_student_borrowed_books(s2)
            output = mock_out.getvalue()
            self.assertIn("No borrowing history found", output)
            self.assertNotIn("Clean Code", output)

    # 20. Phase 1 features regression test: Add book, Register student, Search book
    def test_20_phase1_regression(self):
        # Register new student
        with patch('builtins.input', side_effect=["S103", "Charlie", "charliepass"]):
            self.service.register_student()
        self.assertIsNotNone(self.db.get_student("S103"))

        # Add new book
        with patch('builtins.input', side_effect=["B104", "New Architecture Book", "Martin Fowler", "Architecture", "999888", "5"]):
            self.service.add_book()
        self.assertIsNotNone(self.db.get_book("B104"))

        # Search book
        with patch('builtins.input', side_effect=["Architecture"]):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.service.search_book()
                output = mock_out.getvalue()
                self.assertIn("New Architecture Book", output)


if __name__ == "__main__":
    unittest.main()
