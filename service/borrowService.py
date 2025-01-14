from model.waitlistQueue import WaitlistQueue
from model.undoStack import UndoStack
from database.database import db, Book, User, BorrowRecord
from datetime import date

waitlist = {}
undo_stack = UndoStack()

def add_book_to_catalog(title, author, published_date=None):
    book = Book(title=title, author=author, published_date=published_date, available=True)
    db.session.add(book)
    db.session.commit()
    return f"Book '{title}' added to catalog with ID {book.id}."

def find_book_in_catalog(book_id):
    book = Book.query.get(book_id)
    if book:
        return {
            "book_id": book.id,
            "title": book.title,
            "available": book.available
        }
    return None

def borrow_book(user_id, book_id):
    user = User.query.get(user_id)
    book = Book.query.get(book_id)

    if user and book:
        if book.available:
            book.available = False
            db.session.add(BorrowRecord(user_id=user_id, book_id=book_id, borrow_date=date.today()))
            db.session.commit()
            undo_stack.push(("return_book", user_id, book_id))
            return f"Book '{book.title}' borrowed successfully!"
        else:
            if book_id not in waitlist:
                waitlist[book_id] = WaitlistQueue()
            waitlist[book_id].enqueue(user_id)
            return "Book not available, added to the waitlist."
    return "User or book not found."

def return_book(user_id, book_id):
    user = User.query.get(user_id)
    borrow = BorrowRecord.query.filter_by(user_id=user_id, book_id=book_id).first()
    book = Book.query.get(book_id)

    if user and borrow and book:
        borrow.return_date = date.today()
        book.available = True
        db.session.commit()
        undo_stack.push(("borrow_book", user_id, book_id))
        return f"Book '{book.title}' returned successfully!"
    return "Borrow record not found or user not found."

def list_all_books():
    books = Book.query.all()
    return [{"book_id": book.id, "title": book.title, "available": book.available} for book in books]
