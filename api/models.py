from django.db import models
from django.conf import settings


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

    def __str__(self):
        return f"Loan #{self.pk} - {self.copy} to {self.user}"