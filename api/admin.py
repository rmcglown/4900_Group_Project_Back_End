from django.contrib import admin
from .models import Author, Book, BookCopy, Loan

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date')
    search_fields = ('first_name', 'last_name')

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'genre', 'publication_date')
    search_fields = ('title', 'isbn')
    list_filter =  ('genre',)

class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'added_date')
    list_filter = ('status', 'book')

class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'copy', 'loan_date', 'due_date', 'return_date', 'status')
    list_filter = ('status',)
    search_fields = ('user__username',)


admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookCopy, BookCopyAdmin)
admin.site.register(Loan, LoanAdmin)


