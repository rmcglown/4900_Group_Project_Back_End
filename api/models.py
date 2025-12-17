from django.db import models
from django.conf import settings
from decimal import Decimal
import datetime

User = settings.AUTH_USER_MODEL

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    biography = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True)
    genre = models.CharField(max_length=255, blank=True)
    publication_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class BookCopy(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_loan', 'On Loan'),
        ('reserved', 'Reserved'),
        ('lost', 'Lost'),
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='available')
    added_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.book.title

class Loan(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='borrowed')

    fine_paid = models.BooleanField(default=False)
    fine_paid_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    DAILY_FINE_RATE = Decimal("0.50")

    def __str__(self):
        return f"Loan #{self.pk} - {self.copy} to {self.user}"
    def is_overdue(self) -> bool:
        """True if this loan is currently overdue."""
        reference_date = self.return_date or datetime.date.today()
        return reference_date > self.due_date and self.status in ("borrowed", "overdue")

    def calculate_overdue_fine(self) -> Decimal:
        # No fine logic if we can't compute yet
        if getattr(self, "fine_paid", False):
            return Decimal("0.00")
        if not self.due_date:  #due date not entered yet
            return Decimal("0.00")

        reference_date = self.return_date or datetime.date.today()

        # returned on/before due date or status says returned
        if self.status == 'returned' and reference_date <= self.due_date:
            return Decimal("0.00")

        if reference_date <= self.due_date:
            return Decimal("0.00")

        days_overdue = (reference_date - self.due_date).days
        rate = getattr(self, "DAILY_FINE_RATE", Decimal("0.50"))
        return rate * days_overdue

    @property
    def current_fine(self) -> Decimal:
        "admin display"
        return self.calculate_overdue_fine()