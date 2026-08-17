import importlib.util
import os
import tempfile
import unittest
from pathlib import Path


class DataPathTests(unittest.TestCase):
    def test_database_loads_books_from_app_directory(self):
        app_dir = Path(__file__).resolve().parent / "Library_Management_System_v1.0"
        spec = importlib.util.spec_from_file_location("library_main", app_dir / "main.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmp_dir)
                db = module.DatabaseManager()
                self.assertGreater(len(db.books), 0, "Expected books to be loaded from the app directory")
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
