from datetime import date, timedelta
from django.core.exceptions import ValidationError
from .models import Book, BookCopy, Loan

def checkout_book(user, book: Book):
    copy = BookCopy.objects.filter(book=book, status='available').first()

    if not copy:
        raise ValidationError("No available copies of this book.")

    loan = Loan.objects.create(
        user=user,
        copy=copy,
        due_date=date.today() + timedelta(days=14),
        status='borrowed'
    )

    copy.status = 'on_loan'
    copy.save()

    return loan


def return_book(loan: Loan):
    if loan.status == 'returned':
        raise ValidationError("This book has already been returned.")

    loan.return_date = date.today()
    loan.status = 'returned'
    loan.save()

    copy = loan.copy
    copy.status = 'available'
    copy.save()

    return loan