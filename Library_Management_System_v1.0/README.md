# Library Management System v2.0 (Phase 1 & Phase 2)

A Python-based Library Management System using JSON storage.

## Features

### Phase 1 Features
- **Admin Authentication**: Secure login for library administrators.
- **Student Registration & Login**: Registration and credentials verification for students.
- **Book Management**: Add, view, and search catalog books.
- **Student Directory**: View registered students.

### Phase 2 Features
- **Borrow Book**: Logged-in students can borrow available books with instant quantity updates.
- **Return Book**: Students can return their borrowed books with status updates and quantity restocking.
- **Transaction Management**: Real-time tracking of transactions (Transaction ID, Student ID, Book ID, Borrow Date, Return Date, Status).
- **My Borrowed Books**: Personal borrowing history view isolated to the logged-in student.
- **Change Password**: Self-service student password updates with validation.
- **Admin Book Updates**: Update title, author, category, ISBN, and quantity with active borrow constraints.
- **Admin Delete Book & Student**: Safe deletion protected against removing active borrowed books or students with active borrowings.
- **Admin Transaction Log**: View all library transactions across students and books.

## Getting Started

Run the system using Python:
```bash
python Library_Management_System_v1.0/main.py
```
