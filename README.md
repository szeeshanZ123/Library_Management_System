# 📚 Smart Library Management System (v2.0)

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Phase%201%20%26%202%20Complete-success?style=for-the-badge)](https://github.com/szeeshanZ123/Library_Management_System)
[![Storage](https://img.shields.io/badge/Storage-JSON%20Flat%20Files-orange?style=for-the-badge&logo=json&logoColor=white)](https://github.com/szeeshanZ123/Library_Management_System)
[![Architecture](https://img.shields.io/badge/Architecture-OOP%20%26%20Service%20Layer-blueviolet?style=for-the-badge)](https://github.com/szeeshanZ123/Library_Management_System)
[![Tests](https://img.shields.io/badge/Tests-14%2F14%20Passing-brightgreen?style=for-the-badge)](https://github.com/szeeshanZ123/Library_Management_System)

A robust, modular, object-oriented **Library Management System** developed in Python. The application features dual-role authentication (Admin & Student), persistent JSON data storage, dynamic inventory tracking, and full lifecycle transaction logging for book borrowings and returns with rigorous data-integrity constraints.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
  - [👑 Administrator Panel](#-administrator-panel)
  - [🎓 Student Panel](#-student-panel)
- [🛡️ Business Rules & Integrity Guards](#️-business-rules--integrity-guards)
- [📁 Project Structure](#-project-structure)
- [🚀 Quick Start & Installation](#-quick-start--installation)
- [🔑 Default Credentials](#-default-credentials)
- [💾 Data Schemas](#-data-schemas)
- [🧪 Running Automated Tests](#-running-automated-tests)
- [📋 Release History](#-release-history)

---

## 🌟 Overview

The **Smart Library Management System** is designed to streamline library workflows for educational institutions and organizations. It replaces paper-based or error-prone logs with an automated CLI system that guarantees transactional consistency across books, students, and inventory states.

```
+-------------------------------------------------------------------------+
|                    SMART LIBRARY MANAGEMENT SYSTEM                      |
+-------------------------------------------------------------------------+
                                   |
         +-------------------------+-------------------------+
         |                                                   |
         v                                                   v
  [ 👑 Admin Role ]                                   [ 🎓 Student Role ]
  - Add / Update / Delete Books                       - Search & View Books
  - Register & Delete Students                        - Borrow Available Books
  - View Global Transaction Audit Log                 - Return Borrowed Books
  - Catalog Inspection & Search                       - View Personal Borrow History
                                                      - Self-Service Password Change
```

---

## 🏛️ System Architecture

The codebase follows **Clean Architecture & Separation of Concerns (SoC)** principles:

- **Data Models (`Book`, `Student`, `Transaction`)**: Encapsulate business entities with serialization (`to_dict`) and deserialization (`from_dict`) methods.
- **Database Manager (`DatabaseManager`)**: Handles data persistence, file path resolution across environments, JSON read/write operations, and relational query helpers.
- **Service Layer (`LibraryService`)**: Houses all business logic, transactional validations, inventory recalculation, and integrity verification.
- **Interface Layer (`LibraryCLI`)**: Interactive console UI supporting nested menus, input sanitization, and formatted tabular views.

---

## ✨ Key Features

### 👑 Administrator Panel

| Feature | Description |
| :--- | :--- |
| **Add Book** | Add new titles with ID, Title, Author, Category, ISBN, and initial Quantity. |
| **Update Book** | Selectively update any field (Title, Author, Category, ISBN, Quantity) while preserving unchanged fields. |
| **Delete Book** | Remove books from catalog with safety checks preventing deletion if active borrowings exist. |
| **View Catalog** | Formatted table displaying all books, authors, stock quantities, and availability status. |
| **Search Books** | Fast fuzzy search across Book ID, Title, and Author name. |
| **Register Student** | Create student accounts with unique ID, Name, and initial password. |
| **View Students** | Directory listing all registered students. |
| **Delete Student** | Remove student profiles with safety checks blocking deletion if books are currently borrowed. |
| **View All Transactions**| Master audit trail showing all historical & active borrowings across the entire library. |

---

### 🎓 Student Panel

| Feature | Description |
| :--- | :--- |
| **Catalog Browser** | Browse all available books with real-time stock levels. |
| **Search Engine** | Query the catalog by ID, Title, or Author. |
| **Borrow Book** | Checkout books instantly; automatically decrements available copies and creates an active transaction. |
| **Return Book** | View currently borrowed books and return them; automatically restocks inventory and marks the transaction as `Returned`. |
| **My Borrowed Books** | Private personal history showing active borrowings and returned books with borrow/return dates. |
| **Change Password** | Self-service password management with current password verification and match confirmation. |

---

## 🛡️ Business Rules & Integrity Guards

1. **Zero-Stock Protection**: Students cannot borrow books when available quantity is `0`.
2. **Duplicate Borrow Prevention**: A student cannot borrow multiple copies of the same book at the same time.
3. **Safe Book Deletion**: Admins cannot delete a book that currently has active `"Borrowed"` records.
4. **Safe Student Deletion**: Admins cannot delete a student who has outstanding unreturned books.
5. **Inventory Lower-Bound Guard**: Admins cannot update total book copies to a quantity lower than currently borrowed copies.
6. **Data Isolation**: Students only have access to their own borrowing records and cannot view other students' activity.

---

## 📁 Project Structure

```text
Library_Management_System/
│
├── Library_Management_System_v1.0/     # Core application package
│   ├── main.py                         # Application entry point & CLI logic
│   ├── books.json                      # Book inventory data store
│   ├── students.json                   # Registered students data store
│   ├── transactions.json               # Borrowing/returning transaction records
│   └── README.md                       # Submodule documentation
│
├── tests/                              # Unit & integration test suite
│   └── test_phase2.py                  # Complete Phase 1 & 2 test suite (14 test cases)
│
├── test_data_paths.py                  # Environment & relative path validation tests
├── .gitignore                          # Git ignore rules
└── README.md                           # Master repository documentation
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python **3.8** or higher installed ([Download Python](https://www.python.org/downloads/))
- Git installed on your system

### 1. Clone the Repository
```bash
git clone https://github.com/szeeshanZ123/Library_Management_System.git
cd Library_Management_System
```

### 2. Run the Application
You can run the application directly from the repository root:
```bash
python Library_Management_System_v1.0/main.py
```
*Or navigate into the application directory:*
```bash
cd Library_Management_System_v1.0
python main.py
```

---

## 🔑 Default Credentials

### Administrator
- **Username:** `admin`
- **Password:** `admin123`

### Sample Student Accounts (Ready to Test)
| Student ID | Student Name | Password |
| :--- | :--- | :--- |
| `S101` | Alice Smith | `pass123` |
| `S102` | Bob Jones | `secretbob` |

*(You can also register a new student directly from the Main Menu!)*

---

## 💾 Data Schemas

### `books.json`
```json
[
    {
        "book_id": "B101",
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "category": "Software Engineering",
        "isbn": "9780132350884",
        "quantity": 3,
        "available_status": true
    }
]
```

### `students.json`
```json
[
    {
        "student_id": "S101",
        "name": "Alice Smith",
        "password": "pass123"
    }
]
```

### `transactions.json`
```json
[
    {
        "transaction_id": 1,
        "student_id": "S101",
        "book_id": "B101",
        "borrow_date": "2026-08-17",
        "return_date": null,
        "status": "Borrowed"
    }
]
```

---

## 🧪 Running Automated Tests

The repository includes a comprehensive `unittest` test suite covering authentication, stock mutations, transaction lifecycles, deletion constraints, and regression flows.

Run all tests using:
```bash
python -m unittest discover tests
```

To run path resolution tests:
```bash
python test_data_paths.py
```

---

## 📋 Release History

- **v1.0 (Phase 1)**:
  - Initial CLI scaffold & Admin authentication.
  - Student registration & credential validation.
  - Book catalog management (Add, View, Search).
  - Student directory viewing.
- **v2.0 (Phase 2)**:
  - Interactive Student Borrow & Return workflow.
  - Dynamic stock decrement & restocking.
  - Isolated "My Borrowed Books" dashboard.
  - Global transaction audit log for Admins.
  - Safe deletion safeguards for active books and students.
  - Admin update stock lower-bound protection.
  - Self-service student password updates.
  - Comprehensive automated test suite (`tests/test_phase2.py`).

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
